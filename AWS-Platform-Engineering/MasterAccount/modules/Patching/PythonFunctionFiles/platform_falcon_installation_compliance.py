from io import StringIO
import time
import boto3
import csv
import random
import os
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from botocore.config import Config
from datetime import datetime

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

class FalconComplianceReport(object):
    def __init__(self, event, context):
        self.athena_client = boto3.client('athena')
        self.s3_client = boto3.client('s3', config=Config(signature_version='s3v4'))
        self.session = boto3.session.Session()
        self.ses_client = self.session.client('ses')
        self.ssm_client = self.session.client('ssm')

        try:
            self.database = os.environ['DATABASE']
            self.output_bucket = os.environ['OUTPUTBUCKET']
            self.query = os.environ['QUERY']
        except Exception as exp:
            logger.info('Failed at init')
            raise Exception(str(exp))
    def get_query_string(self,named_query_id):
        """
        mothod: function to get the saved query
        param: Query ID
        return: Query string 
        """
        response = self.athena_client.get_named_query(
            NamedQueryId=named_query_id
        )

        return response['NamedQuery']['QueryString']
        
    def athena_query(self,query):
        try:
            response = self.athena_client.start_query_execution(
                QueryString=query,
                QueryExecutionContext={
                    'Database': self.database
                },
                ResultConfiguration={
                    'OutputLocation': 's3://{}/'.format(self.output_bucket)
                }
            )
            time.sleep(5)
            return response['QueryExecutionId']
        except Exception as exception:
            print(exception)

    def get_athena_results(self, query_id):
        status = False
        try:
            while status != True:
                response = self.athena_client.get_query_execution(
                    QueryExecutionId=query_id
                )
                if response['QueryExecution']['Status']['State'] in ['FAILED','CANCELLED']:
                    query_id = self.athena_query()
                elif response['QueryExecution']['Status']['State'] in ['RUNNING', 'QUEUED']:
                    time.sleep(5)
                elif response['QueryExecution']['Status']['State'] == 'SUCCEEDED':
                    status = True
        except Exception as exception:
            print(exception)

        return query_id


    def rename_file(self, file_name):
        now = datetime.now()
        day = now.strftime('%d')
        month = now.strftime('%B')
        year = now.strftime('%Y')
        key = 'Monthly-Reports/falcon_compliance_report_{}_{}.csv'.format(month,year)
        copy_source = '{}/{}.csv'.format(self.output_bucket, file_name)
        try:
            self.s3_client.copy_object(
                CopySource=copy_source, 
                Bucket=self.output_bucket, 
                Key=key
            ) 
            return key
        except Exception as exception:
            print(exception)
            return 'FAILED'

    def generate_report_main(self):
        query_managed_string = self.get_query_string(self.query)
        query_id = self.athena_query(query_managed_string)
        file_location = self.get_athena_results(query_id)
        new_file_location = self.rename_file(file_location)
    
    def get_tag_value(self, account_id, region, instance_id):
        config_client = boto3.client('config')
        tag_value=''
        try:
            response = config_client.get_aggregate_resource_config(
            ConfigurationAggregatorName='aws-controltower-ConfigAggregatorForOrganizations',
            ResourceIdentifier={
            'SourceAccountId': str(account_id),
            'SourceRegion': str(region),
            'ResourceId': str(instance_id),
            'ResourceType': 'AWS::EC2::Instance'
             }) 
            response=response['ConfigurationItem']['tags']
            if response['platform_falcon_linux']:
                tag_value=response['platform_falcon_linux']
            elif response['platform_falcon_windows']:
                tag_value=response['platform_falcon_windows']
            else:
                tag_value='Tag Not Found'
            print(tag_value)
        except Exception as exception:
            tag_value='Resource Not Found'
        return tag_value
    
    def get_custodian(self, account_id):
        account_id=str(account_id)
        print(account_id)
        client = boto3.client('dynamodb')
        try:
            response = client.get_item(
             Key={
            'AccountNumber': {
                'S': account_id,
            },
            },
           TableName='Account_Details',
            )
            custodian_data=response['Item']['CustodianUser']['S']
        except Exception as exception:
            custodian_data='No data fetched'
        return custodian_data

    def modify_report(self):
        now = datetime.now()
        month = now.strftime('%B')
        year = now.strftime('%Y')
        key = 'Monthly-Reports/falcon_compliance_report_{}_{}.csv'.format(month,year)
        s3_object = self.s3_client.get_object(Bucket=self.output_bucket, Key=key)
        body = s3_object['Body']
        #data = body.read().decode('utf-8')
        csv_string = body.read().decode('utf-8')
        csvreader = csv.reader(StringIO(csv_string))
        ami_name=''
        iterator=0
        final_data={}
        tag_value=''
        custodian_user=''
        global_l=[]
        report=[]
        items=[]
        non_compliant_instances_accounts=[]
        for row in csvreader:
            input_data={}

            if row[7]=='Falcon Not Installed':
                non_compliant_instances_accounts.append(row[2])
                print(row[12])
                tag_value=self.get_tag_value(row[2],row[3],row[5])
                custodian_user=self.get_custodian(row[2])
            else:
                tag_value='Not Applicable for compliant instances'
                custodian_user='Not Applicable for compliant instances'
            if iterator==1:
                input_data['ou_name']=row[0]
                input_data['account_name']=row[1]
                input_data['account_id']=row[2]
                input_data['region']=row[3]
                input_data['imageid']=row[4]
                input_data['instance_id']=row[5]
                input_data['instance_state']=row[6]
                input_data['status_of_falcon_installation']=row[7]
                input_data['platform_name']=row[8]
                input_data['platform_type']=row[9]
                input_data['custodian']=custodian_user
                input_data['tag_value']=tag_value
                global_l.append(input_data)
                print(global_l)
            iterator=1
            if row[7]=='Falcon Not Installed' and row[6]=='stopped' and "@" in custodian_user and tag_value=="yes":
                row.append(custodian_user)
                items.append(row)
            
        column_names=['ou_name','account_name','account_id','region','imageid','instance_id','instance_state','status_of_falcon_installation','platform_name','platform_type','custodian','tag_value']
        with open('/tmp/Falcon_Compliance_Report.csv', 'w') as out:
            writer = csv.DictWriter(out,fieldnames=column_names)
            writer.writeheader()
            writer.writerows(global_l)
            self.s3_client.upload_file("/tmp/Falcon_Compliance_Report.csv",self.output_bucket,"/tmp/Falcon_Compliance_Report.csv")
    
        self.send_report()
        try:
            if items!=[]:
                for item in items:
                    report = []
                    custodian = item[13]
                    if 'read' not in item:
                        temp = []
                        for each_item in items:
                            if each_item[13] == custodian and 'read' not in each_item:
                                temp.append(each_item)
                                each_item.append('read')
                                temp_report = {'InstanceId' : each_item[5],
                                            'AccountId' : each_item[2],
                                            'AccountName' : each_item[1],
                                            'Custodian' : each_item[13],
                                            'Region' : each_item[3]}
                                report.append(temp_report)
                        if report != []:
                            self.send_ec2_emails(report)
                            logger.info(report)
        except Exception as exception:
            print(exception)
        
    def send_report(self):
        try:
            file_name_list=['/tmp/Falcon_Compliance_Report.csv']
            print("Inside Send Mail")
            sender_response = self.ssm_client.get_parameter(Name='sender_id')
            sender_id = sender_response['Parameter']['Value']
            rec_response = "GX-IDSO-SOM-ET-DP-CLOUD-SECURITY-COMPLIANCE@shell.com"
            to_recipient = rec_response
            recipient_list = to_recipient.split(',')
        # The email body for recipients with non-HTML email clients.
            body_text = "Hello\r\nPlease find the attached baseline report for AWS@Shell."\
                                                                      "\r\nRegards,\r\nCloud Services Team"
        # The HTML body of the email.
            body_html = """<html>
        <head></head>
        <body>
        <p style="font-family:'Futura Medium'">Hello Team,</p>
        <p style="font-family:'Futura Medium'">Please find the attached filtered reports and the baseline report for AWS@Shell.</p>
        <p style="font-family:'Futura Medium'">Best Regards,</p>
        <p style="font-family:'Futura Medium'">Cloud Services Team</p>
        </body>
        </html>
        """
            try:
                # Replace recipient@example.com with a "To" address.
                # # The subject line for the email.
                mail_subject = "Falcon Compliance Reports"
                #attachment_template = file_name  # "{}".format(file_name)
                message = MIMEMultipart('mixed')
                message['Subject'] = mail_subject
                message['From'] = sender_id
                message['To'] = to_recipient
                message_body = MIMEMultipart('alternative')
                char_set = "utf-8"
                textpart = MIMEText(body_text.encode(char_set), 'plain', char_set)
                htmlpart = MIMEText(body_html.encode(char_set), 'html', char_set)
                message_body.attach(textpart)
                message_body.attach(htmlpart)
                for f in file_name_list:
                    attachment_template = f 
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
            self.s3_client.delete_objects(Bucket=self.output_bucket, Delete={"Objects":[{"Key":"/tmp/Falcon_Compliance_Report.csv"}]})
        except Exception as ex:
            logger.error("Lambda failed with the error:'{0}'".format(ex))
            return "FAILED"
            
    def send_ec2_emails(self, report):
        """method: sends reconciliation emails to team and custodian
        param: list containing instance id, account id, account name, account custodian name
        return: mailing response
        """
        mail_body = ''
        html = ''
        custodian = ''
        client = boto3.client('ses')
        print(report)
        for item in report:
            custodian = item['Custodian']
            html+="""<tr>
                    <td width="22%">"""+item['InstanceId']+"""</td>
                    <td width="22%">"""+item['Region']+"""</td>
                    <td width="18%">""" +item['AccountId']+ """</td>
                    <td width="45%">""" +item['AccountName']+ """</td>
                    </tr>"""
            mail_body=mail_body+"""\nInstance ID: """+item['InstanceId']+"""\nInstance region: """+item['Region']+""" """+"""\nAccount ID: """+item['AccountId']+"""\nAccount Name: """+item['AccountName']
            text_body="""Hello,
                This email is to inform that the below instances is stopped in your accounts and does not have falcon agent installed on it. Kindly move it to running state for agent installation to happen and let us know. """ +mail_body+"""\n\nRegards,\nCloud Services Team"""
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
                    <p style="font-family:'Futura Medium'"> This email is to inform that the below instance is stopped in your account and does not have falcon agent installed on it. Kindly move it to running state for agent installation to happen and let us know.</p>
                    
                    <table style="width:100%">
                        <col style="width:20%">
                        <col style="width:40%">
                        <col style="width:40%">
                        <tr bgcolor="yellow">
                        <td width="20%">Instance Id</td>
                        <td width="15%">Region</td>
                        <td width="15%">AccountId</td>
                        <td width="50%">AccountName</td>
                        </tr>"""+html+"""
                    </table>
                    <br>
                    <p style="font-family:'Futura Medium'">Best Regards,</p>
                    <p style="font-family:'Futura Medium'">AWS@Shell Platform Engineering Team</p>
                    <href>GX-SITI-CPE-Team-Titan@shell.com</href>
                    </body>
                    </html>
                    """
        try:
            logger.info('Inside custom Send Mail')
            response = client.send_email(
                Destination={
                    'ToAddresses': [custodian]
                        },
                Message={
                        'Subject': {
                            'Data': 'Falcon Agent Compliance',
                                    },
                        'Body': {
                            'Text': {
                                'Data': text_body,
                            },
                            'Html':{
                                'Data':html_body
                            }
                                },
                               },
                Source='SITI-ECP-AWS-AT-SHELL@shell.com',
                        )
            logger.info('Email sent!')
            return(response)
        except Exception as exception:
            logger.error("Lambda failed with the error:'{0}'".format(exception))
            return "FAILED"
   

def lambda_handler(event, context):
    falcon_compliance_report = FalconComplianceReport(event, context)
    falcon_compliance_report.generate_report_main()
    logger.info('modifying report')
    falcon_compliance_report.modify_report()
    logger.info('deleting from s3')
    falcon_compliance_report.delete_from_s3()