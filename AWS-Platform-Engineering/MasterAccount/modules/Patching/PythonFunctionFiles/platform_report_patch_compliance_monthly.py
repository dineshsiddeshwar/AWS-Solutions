import json
import time
import random
import boto3
import os
import logging
from decimal import Decimal
import csv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from boto3.dynamodb.conditions import Key, Attr
from botocore.config import Config
from datetime import datetime
from io import StringIO
year = str(datetime.today().year)
month = str(datetime.today().month)
day = str(datetime.today().day)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
logger.addHandler(CH)
class InventoryPatchingReport(object):
    """
    class: bundles the functions for ec2 patching report and mail automation
    object: object for the class
    """
    def __init__(self, event, context):
        """
        method: main function for global variables
        """
        self.s3 = boto3.client('s3')
        
        self.session = boto3.session.Session()
        self.ses_client = self.session.client('ses')
        self.dynamodb_client = boto3.resource('dynamodb')
        self.ssm_client = self.session.client('ssm')
        
        try:
            self.output_bucket = os.environ['OUTPUTBUCKET']
            self.table_name_var = "TRB_AMI_Exception_Management"
        except Exception as exp:
            logger.info('Failed at init')
            raise Exception(str(exp))
            
    def get_exception_details(self, non_compliant_instances_accounts):
        """
        method: function for fetching exception table data
        """
        ami= ''
        table_name= self.table_name_var
        table =self.dynamodb_client.Table(table_name)
        response = table.scan()
        data = response['Items']
        exception_records=[]

        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            data.extend(response['Items'])
        print("print response of scan")
        print(data)
        for item in data:
            if item['AccountNumber'] in non_compliant_instances_accounts:
                print(type(item))
                exception_records.append(item)
        print("exception records......")
        print(exception_records)
        return exception_records
        
    def modify_report(self):
        now = datetime.now()
        month = now.strftime('%B')
        year = now.strftime('%Y')
        key = 'Monthly-Reports/consolidated_patch_compliance_report_{}_{}.csv'.format(month,year)
        s3_object = self.s3.get_object(Bucket=self.output_bucket, Key=key)
        body = s3_object['Body']
        #data = body.read().decode('utf-8')
        csv_string = body.read().decode('utf-8')
        csvreader = csv.reader(StringIO(csv_string))
        ami_name=''
        final_data={}
        tag_value=''
        global_l=[]
        iterator=0
        non_compliant_instances_accounts=[]
        for row in csvreader:
            input_data={}

            if row[1]=='NON_COMPLIANT':
                non_compliant_instances_accounts.append(row[2])
                print(row[12])
                response=self.get_image_name(row[2],row[12],row[0],row[6])
                ami_name=response[0]
                tag_value=response[1]
            else:
                ami_name='Not Applicable for compliant instances'
                tag_value='Not Applicable for compliant instances'
            if iterator==1:
                input_data['resourceid']=row[0]
                input_data['status']=row[1]
                input_data['accountid']=row[2]
                input_data['account_workload']=row[3]
                input_data['account_name']=row[4]
                input_data['account_owner']=row[5]
                input_data['region']=row[6]
                input_data['capturetime']=row[7]
                input_data['platformname']=row[8]
                input_data['ipaddress']=row[9]
                input_data['platformtype']=row[10]
                input_data['instancestatus']=row[11]
                input_data['imageid']=row[12]
                input_data['ami_name']=ami_name
                input_data['patch_install_tag_status']=tag_value
                global_l.append(input_data)
                print(global_l)
            iterator=1
            
        column_names=['resourceid','status','accountid','account_workload','account_name','account_owner','region','capturetime','platformname','ipaddress','platformtype','instancestatus','imageid','ami_name','patch_install_tag_status']
        with open('/tmp/Compliance_Report.csv', 'w') as out:
            writer = csv.DictWriter(out,fieldnames=column_names)
            writer.writeheader()
            writer.writerows(global_l)
            self.s3.upload_file("/tmp/Compliance_Report.csv",self.output_bucket,"/tmp/Compliance_Report.csv")
        exception_records=self.get_exception_details(non_compliant_instances_accounts)
        self.send_mail(exception_records)
        
    def get_image_name(self,account_no,image_id,instance_id,region):
        instance_and_ami_name=[]
        tag_value='Tag not found'
        self.iam_arn_string_1 = "arn:aws:iam::"
        self.str_sts_assume_role = "sts:AssumeRole"
        self.str_lambda_arn = "lambda.amazonaws.com"
        self.session_client = boto3.session.Session()
        self.account_number=account_no
        self.sts_master_client = self.session_client.client('sts')
        self.child_account_session_name = "ChildAccountSession-" + str(random.randint(1, 100000))
        self.child_account_role_arn = self.iam_arn_string_1 + str(self.account_number) + ":role/AWSControlTowerExecution"
        child_account_role_creds = self.sts_master_client.assume_role(RoleArn=self.child_account_role_arn,
                                                                          RoleSessionName=self.child_account_session_name)
        child_credentials = child_account_role_creds.get('Credentials')
        child_access_key_id = child_credentials.get('AccessKeyId')
        child_secret_access_key = child_credentials.get('SecretAccessKey')
        child_session_token = child_credentials.get('SessionToken')
        self.child_assume_role_session = boto3.Session(child_access_key_id, child_secret_access_key,
                                                           child_session_token)
        self.ec2_client =self.child_assume_role_session.client('ec2',region_name=region)
        try:
            response = self.ec2_client.describe_images(ImageIds=[image_id])
            if response['Images'][0]['Name']:
                instance_and_ami_name.append(response['Images'][0]['Name'])
            else:
                instance_and_ami_name.append('AMI has been deleted')
        except Exception as exception:
            instance_and_ami_name.append('AMI not found')
        try:
            response = self.ec2_client.describe_instances(InstanceIds=[instance_id])
            for tag in (response['Reservations'][0]['Instances'][0]['Tags']):
                if tag['Key']=='platform_install_patch':
                    tag_value=tag['Value']
            instance_and_ami_name.append(tag_value)
        except Exception as exception:
            instance_and_ami_name.append('Instance not found')
        return instance_and_ami_name
        
    
    def send_mail(self,exception_records):
        try:
            file_name_list='/tmp/Compliance_Report.csv'
            print("Inside Send Mail")
            sender_id = 'SITI-ECP-AWS-AT-SHELL@shell.com'
            rec_response = "mari.shankar@shell.com,rekhu.chinnarathod@shell.com,d.kumar6@shell.com,abeesh.abraham@shell.com,kaushiki.singh@shell.com"
            to_recipient = rec_response
            recipient_list = to_recipient.split(',')
        # The email body for recipients with non-HTML email clients.
            body_text = "Hello\r\nPlease find the attached compliance report for AWS@Shell."\
                                                                      "\r\nRegards,\r\nCloud Services Team"
        # The HTML body of the email.
            toe_response = self.ssm_client.get_parameter(Name='TOE_Complaint_OS_Flavours')
            toe_value = toe_response['Parameter']['Value']
            print(toe_value)
            body_html = """<html>
        <head></head>
        <body>
        <p style="font-family:'Futura Medium'">Hello Team,</p>
        <p style="font-family:'Futura Medium'">Please find the attached compliance report for AWS@Shell.</p>
        <p style="font-family:'Futura Medium'">Also please find the below generalized list of TOE compliant images.</p>"""+toe_value+"""
        <p style="font-family:'Futura Medium'">Best Regards,</p>
        <p style="font-family:'Futura Medium'">AWS@Shell Platform Engineering Team</p>
        <href>GX-SITI-CPE-Team-Titan@shell.com</href>
        </body>
        </html>
        """
            mail_body = ''
            html = ''
              # The email body for recipients with non-HTML email clients.
            body_text = "Hello\r\nPlease find the attached filtered report for AWS@Shell."\
                                                                      "\r\nRegards,\r\nAWS@Shell Platform Engineering Team"
        # The HTML body of the email.
            for line in exception_records:
                print("lineee",type(line))
                html+="""<tr>
                    <td width="22%">"""+line['RequestNumber']+"""</td>
                    <td width="22%">"""+line['AccountNumber']+"""</td>
                    <td width="18%">""" +line['CustodianMailId']+ """</td>
                    <td width="45%">""" +line['RequestParameter']+ """</td>
                    </tr>"""
                mail_body=mail_body+"""\nRequest Number: """+line['RequestNumber']+"""\nAccount Number: """+line['AccountNumber']+"""\nAccount Owner: """+line['CustodianMailId']+"""\nAMI Name exempted for the account: """+line['RequestParameter']
        
            text_body="""Hello,
            This email is to inform that the below instances are not patched for more than 15 days in your account. Kindly take the neccessary actions and let us know. """ +mail_body+"""\n\nRegards,\nCloud Services Team"""
            html_body = """<html>
                <head>
                <style>
                    table, td {
                    border: 1px solid black;
                    border-collapse: collapse;
                    }      
                    
                    th {
                    border: 1px solid black;
                    border-collapse: collapse;
                    font-weight: bold
                    }
                    
                    td, th {
                    padding-left: 10px;
                    text-align: left;
                    }
                </style>
                </head>
                <body>
                <p style="font-family:'Futura Medium'">Hello,</p>
                <p style="font-family:'Futura Medium'"> Please find the attached non compliance report. Below are the details of accounts listing as non compliannt in the above report but have exceptions approved in them</p>
                
                <table style="width:100%">
                    <col style="width:20%">
                    <col style="width:40%">
                    <col style="width:40%">
                    <tr bgcolor="yellow">
                    <td width="15%">Request Number</td>
                    <td width="10%">Account Number</td>
                    <td width="20%">Account Owner</td>
                     <td width="50%">AMI details exempted for the account</td>
                    </tr>"""+html+"""
                </table>
                <p style="font-family:'Futura Medium'"><b>NOTE : </b>Please ensure the instance is available to receive the default patch which runs every friday at 5AM UTC.</p>
                <br>
                <p style="font-family:'Futura Medium'">Best Regards,</p>
                <p style="font-family:'Futura Medium'">AWS@Shell Platform Engineering Team</p>
                <href>GX-SITI-CPE-Team-Titan@shell.com</href>
                </body>
                </html>
                """
            try:
                # Replace recipient@example.com with a "To" address.
                # # The subject line for the email.
                mail_subject = "Consolidated Patching Report"
                #attachment_template = file_name  # "{}".format(file_name)
                message = MIMEMultipart('mixed')
                message['Subject'] = mail_subject
                message['From'] = sender_id
                message['To'] = to_recipient
                message_body = MIMEMultipart('alternative')
                char_set = "utf-8"
                if len(exception_records)>0:
                    textpart = MIMEText(text_body.encode(char_set), 'plain', char_set)
                    htmlpart = MIMEText(html_body.encode(char_set), 'html', char_set)
                else:
                    textpart = MIMEText(body_text.encode(char_set), 'plain', char_set)
                    htmlpart = MIMEText(body_html.encode(char_set), 'html', char_set)
                message_body.attach(textpart)
                message_body.attach(htmlpart)
                attachment_template = file_name_list
                attribute = MIMEApplication(open(attachment_template, 'rb').read())
                attribute.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment_template))
                message.attach(attribute)
                message.attach(message_body)
                mail_response = self.ses_client.send_raw_email(
                    Source=sender_id,
                    Destinations=recipient_list,
                    RawMessage={
                    'Data': message.as_string()
                })

            except Exception as exception:
                print(exception)
        except Exception as exception:
            print(exception)
    
    def delete_from_s3(self):
        try:
            self.s3.delete_objects(Bucket=self.output_bucket, Delete={"Objects":[{"Key":"/tmp/Compliance_Report.csv"}]})
        except Exception as ex:
            logger.error("Lambda failed with the error:'{0}'".format(ex))
            return "FAILED"

 
def lambda_handler(event, context):
    # TODO implement
    inventory_patching_report = InventoryPatchingReport(event, context)
    logger.info('modifying report')
    inventory_patching_report.modify_report()
    logger.info('deleting from s3')
    inventory_patching_report.delete_from_s3()
    #inventory_patching_report.send_mail()
