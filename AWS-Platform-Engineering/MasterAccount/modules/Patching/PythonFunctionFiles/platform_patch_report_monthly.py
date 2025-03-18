import time
import boto3
import os
import logging
import csv
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
        self.athena_client = boto3.client('athena')
        self.sns_client = boto3.client('sns')
        self.s3_client = boto3.client('s3', config=Config(signature_version='s3v4'))

        try:
            self.database = os.environ['DATABASE']
            self.output_bucket = os.environ['OUTPUTBUCKET']
            self.topic_arn = os.environ['TOPICARN']
            self.query_managed = os.environ['QUERYMANAGED']
            self.query_nonmanaged = os.environ['QUERYNONMANAGED']
            self.query_master = os.environ['QUERYMASTER']
            self.query_consolidated = os.environ['QUERYCONSOLIDATED']
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
        """
        method: function to execute the query string
        param: query string
        return: QueryExecutionId
        """
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

    def get_athena_results(self, query_id):
        """
        method: function to get the athena query result with reference to QueryExecutionId
        param: QueryExecutionId
        return: Query_id
        """
        status = False
        while status != True:
            response = self.athena_client.get_query_execution(
                QueryExecutionId=query_id
            )
            if response['QueryExecution']['Status']['State'] == ('FAILED' or 'CANCELLED'):
                logger.info('Athena_query has failed please check the flow.')
            elif response['QueryExecution']['Status']['State'] == ('RUNNING' or 'QUEUED'):
                time.sleep(5)
            elif response['QueryExecution']['Status']['State'] == 'SUCCEEDED':
                status = True
            print(response)
        return query_id


    def rename_file(self, file_name, type):
        """
        method: function to organize the monthly patching report accordingly to type managed, non-managed and consolidated
        param: file_name, type of report
        return: key 
        """
        now = datetime.now()
        month = now.strftime('%B')
        year = now.strftime('%Y')
        if type == 'managed':
            key = 'Monthly-Reports/managed_inventory_patch_compliance_{}_{}.csv'.format(month,year)
        elif type == 'nonmanaged':
            key = 'Monthly-Reports/non_managed_inventory_list_{}_{}.csv'.format(month,year)
        elif type == 'master':
            key = 'Monthly-Reports/master_inventory_list_{}_{}.csv'.format(month,year)            
        elif type == 'consolidated':
            key = 'Monthly-Reports/consolidated_patch_compliance_report_{}_{}.csv'.format(month,year)            
        copy_source = '{}/{}.csv'.format(self.output_bucket, file_name)
        self.s3_client.copy_object(
            CopySource=copy_source, 
            Bucket=self.output_bucket, 
            Key=key
        ) 
        return key

    def publish_to_sns(self, new_file_name, new_file_name_2, new_file_name_3, new_file_name_4):
        """
        method: function to publish report to sns
        param: new_file_location_managed, new_file_location_nonmanaged, new_file_location_master, new_file_location_consolidated
        return: sns responce
        """
        response = self.sns_client.publish(
            TopicArn=self.topic_arn,
            Subject='Monthly Patching Status Report',
            Message='The monthly patching status report for EC2 instances is ready.\n Please find it in the bucket with the below details: \n Bucket Name: {0} \n Managed inventory file name: {1} \n Non-Managed inventory file name: {2} \n Master inventory file name: {3} \n Consolidated patch complaince file name: {4} \n'.format(self.output_bucket, new_file_name, new_file_name_2, new_file_name_3, new_file_name_4)
        )
        return response
    

    def mail_report(self):
        """
        method: Creates a formated report ready to be used to send compliance mail based on each account owner
        return: mailing status
        """
        try:
            print('Inside Mail report')
            now = datetime.now()
            month = now.strftime('%B')
            year = now.strftime('%Y')
            key = 'Monthly-Reports/consolidated_patch_compliance_report_{}_{}.csv'.format(month,year)
            items = []
            status = ''
            # Get s3 object to read patching patching report
            s3_object = self.s3_client.get_object(Bucket=self.output_bucket, Key=key)
            body = s3_object['Body']
            data = body.read().decode('utf-8')
            lines = csv.reader(StringIO(data))             
            for line in lines:
                if line[1] == 'NON_COMPLIANT':
                    items.append(line)
            
            for item in items:
                report = []
                custodian = item[5]
                if 'read' not in item:
                    temp = []
                    for each_item in items:
                        if each_item[5] == custodian and 'read' not in each_item:
                            temp.append(each_item)
                            each_item.append('read')
                            temp_report = {'InstanceId' : each_item[0],
                                      'AccountId' : each_item[2],
                                      'AccountName' : each_item[4],
                                      'Custodian' : each_item[5],
                                      'Region' : each_item[6]}
                            report.append(temp_report)
                if report != []:
                    status = self.send_ec2_emails(report)
                    logger.info(report)
            if status == '':
                logger.info('There are no Non-compiant EC2 instances')
            return(status)
        except Exception as ex:
            logger.info(ex)


    def send_ec2_emails(self, report):
        """method: sends reconciliation emails to team and custodian
        param: list containing instance id, account id, account name, account custodian name
        return: mailing response
        """
        mail_body = ''
        html = ''
        custodian = ''
        client = boto3.client('ses')
        
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
                <p style="font-family:'Futura Medium'"> This email is to inform that the below instances are not patched for more than 15 days in your account. Kindly take the neccessary actions and let us know.</p>
                
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
                <p style="font-family:'Futura Medium'"><b>NOTE : </b>Please ensure the instance is available to receive the default patch which runs every friday at 5AM UTC.</p>
                <br>
                <p style="font-family:'Futura Medium'">Best Regards,</p>
                <p style="font-family:'Futura Medium'">AWS@Shell Team</p>
                </body>
                </html>
                """
        try:
            logger.info('Inside custom Send Mail')
            response = client.send_email(
                Destination={
                    'ToAddresses': ['GX-IDSO-ETSOM-DP-CLOUD-AWS-DEVOPS@shell.com', 'GXSOMWIPROCLOUDAWSDA2@shell.com','GX-SITI-CPE-Team-Titan@shell.com', custodian]
                        },
                Message={
                        'Subject': {
                            'Data': 'Patch Compliance',
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
                Source='SITI-CLOUD-SERVICES@shell.com',
                        )
            logger.info('Email sent!')
            return(response)
        except Exception as exception:
            logger.error("Lambda failed with the error:'{0}'".format(exception))
            return "FAILED"

    def send_report_main(self):
        """
        method: function to consolidate the ec2 patching compliance reports
        """
        query_managed_string = self.get_query_string(self.query_managed)
        query_id_managed = self.athena_query(query_managed_string)
        file_location_managed = self.get_athena_results(query_id_managed)
        new_file_location_managed = self.rename_file(file_location_managed,'managed')
        
        query_nonmanaged_string = self.get_query_string(self.query_nonmanaged)
        query_id_nonmanaged = self.athena_query(query_nonmanaged_string)
        file_location_nonmanaged = self.get_athena_results(query_id_nonmanaged)
        new_file_location_nonmanaged = self.rename_file(file_location_nonmanaged,'nonmanaged')
        
        query_master_string = self.get_query_string(self.query_master)
        query_id_master = self.athena_query(query_master_string)
        file_location_master = self.get_athena_results(query_id_master)
        new_file_location_master = self.rename_file(file_location_master,'master')
        
        query_consolidated_string = self.get_query_string(self.query_consolidated)
        query_id_consolidated = self.athena_query(query_consolidated_string)
        file_location_consolidated = self.get_athena_results(query_id_consolidated)
        new_file_location_consolidated = self.rename_file(file_location_consolidated,'consolidated')
        self.publish_to_sns(new_file_location_managed,new_file_location_nonmanaged,new_file_location_master,new_file_location_consolidated)
        mail_status = self.mail_report()
        logger.info(mail_status)


def lambda_handler(event, context):
    """
    method: Main lambda handler takes event as dictionary and context as an object
    param: event
    param: context
    """
    inventory_patching_report = InventoryPatchingReport(event, context)
    inventory_patching_report.send_report_main()

