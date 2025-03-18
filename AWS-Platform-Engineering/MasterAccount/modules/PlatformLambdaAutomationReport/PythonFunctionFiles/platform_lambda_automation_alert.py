import json
import logging
import boto3
import datetime
import time
import gzip
import csv
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from io import StringIO # Python 3.x

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
LOGGER.addHandler(CH)

"""
This Lambda function is used to send daily alert if any lambda function created or role policy changed in core account (payer,shared,audit,logging)
"""

class lambdaAlert(object):
    
    def __init__(self,event, context):
        try:
            LOGGER.info("in init")
            self.session = boto3.session.Session()
            self.ses_client = self.session.client('ses')
            self.ssm_client = self.session.client('ssm')
            self.cloudtrail_client = self.session.client('cloudtrail')
            self.s3_client =boto3.client("s3")
            
            #self.bucket_name=os.environ['BUCKET']
            self.bucket_name = os.environ['BUCKET']
            self.s3_uri='s3://'+self.bucket_name+'/'
            response_datalakeid = self.ssm_client.get_parameter(Name='platform_datalakeid')
            self.datalake_id = response_datalakeid['Parameter']['Value']
            self.account_id_payer = os.environ['MASTER_ACCOUNT_ID']
            self.account_id_audit = os.environ['AUDIT_ACCOUNT_ID']
            self.account_id_logging = os.environ['LOGGING_ACCOUNT_ID']
            self.account_id_shared = os.environ['SHARED_ACCOUNT_ID']
            
            current_datetime = datetime.datetime.now()
            self.current_date = current_datetime.date()
            startTime = (datetime.datetime.now() - datetime.timedelta(days=1)).isoformat()
            startTime=str(startTime)
            print(startTime)
            LOGGER.info("get the date out of the datetime object")
            self.startTime="'"+startTime[:10]+ " 00:00:00"+"'"
            LOGGER.info(startTime)
            endTime = (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat()
            endTime = str(endTime)
            self.endTime="'"+endTime[:10]+ " 00:00:00"+"'"
            #endTime=str(self.current_date)+ " 00:00:00"
            #self.endTime="'"+endTime+"'"
            
        except Exception as e:
            print(str(e))
            raise Exception(str(e))
        
    def send_email(self,file_path_create,bodystring):
        try:
            LOGGER.info("inside send_email")
            sender_id = "SITI-ECP-AWS-AT-SHELL@shell.com"
            recipient_list = ['GX-SITI-CPE-Team-Titan@shell.com','GX-IDSO-SOM-ET-DP-CLOUD-SECURITY-COMPLIANCE@shell.com']
            body_text = "Hello\r\nPlease find the lambda function creation and policy attached alert for AWS@Shell core Account."\
                                                                          "\r\nRegards,\r\nAWS@Shell Platform Engineering Team"
            # The HTML body of the email.
            body_html = """<html>
            <head></head>
            <body>
            <p style="font-family:'Futura Medium'">Hello Team,</p>
            <p style="font-family:'Futura Medium'">Please find the lambda function creation and policy attached alert for AWS@Shell core Account.</p>
            <p style="font-family:'Futura Medium'">Best Regards,</p>
            <p style="font-family:'Futura Medium'">AWS@Shell Platform Engineering Team</p>
            <href>GX-SITI-CPE-Team-Titan@shell.com</href>
            </body>
            </html>
            """
            if self.account_id_payer == '604596384198':
                mail_subject = "{0} alert in core account - {1}".format(bodystring,"Prod")
            elif self.account_id_payer == '136349175397':
                mail_subject = "{0} alert in core account - {1}".format(bodystring,"UAT")
            else:
                mail_subject = "{0} alert in core account - {1}".format(bodystring,"Dev")
            #mail_subject = "{0} alert in core account".format(bodystring)
            message = MIMEMultipart('mixed')
            message['Subject'] = mail_subject
            message_body = MIMEMultipart('alternative')
            char_set = "utf-8"
            textpart = MIMEText(body_text.encode(char_set), 'plain', char_set)
            htmlpart = MIMEText(body_html.encode(char_set), 'html', char_set)
            message_body.attach(textpart)
            message_body.attach(htmlpart)
            attachment_template = file_path_create
            print('put value in attachment')
            attribute = MIMEApplication(open(attachment_template, 'rb').read())
            print('read the attribute')
            attribute.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment_template))
            message.attach(attribute)
            message.attach(message_body)
            mail_response = self.ses_client.send_raw_email(
                            Source=sender_id,
                            Destinations=recipient_list,
                            RawMessage={
                                'Data': message.as_string()
                                
                            })
            LOGGER.info('mail send successfully')
            
        except Exception as e:
            print(str(e))
            raise Exception(str(e))
        
    def get_lambda_alert_data(self):
        
        try:
        
            #s3_uri_value = 's3://monitoring-alert-test-demo-12345/createFunction/'
            #s3://monitoring-alert-test-demo-12345/createFunction/AWSLogs/364355817034/CloudTrail-Lake/Query/2024/03/21/8e016cac-ceac-4047-a048-3590238788c5/
            s3_uri_value = self.s3_uri+'createFunction/'
            
            query_statement = "SELECT recipientAccountId,awsRegion,eventTime,eventName,useridentity.sessioncontext.sessionissuer.username,useridentity.principalid,useridentity.type,requestParameters from {0} WHERE eventName = 'CreateFunction20150331' AND eventTime > {1} AND eventTime < {2} AND (recipientAccountId = '{3}' OR recipientAccountId = '{4}' OR recipientAccountId = '{5}' OR recipientAccountId = '{6}')".format(self.datalake_id,self.startTime,self.endTime,self.account_id_payer,self.account_id_audit,self.account_id_logging,self.account_id_shared)
                
              
            response = self.cloudtrail_client.start_query(
                    QueryStatement=query_statement,
                    DeliveryS3Uri=s3_uri_value
                    )
            
            s3_uri_value1 = self.s3_uri+'rolePolicyAttached/'
            
            query_statement1 = "SELECT recipientAccountId,awsRegion,eventTime,eventName,useridentity.sessioncontext.sessionissuer.username,useridentity.principalid,useridentity.type,requestParameters from {0} WHERE (eventName = 'AttachRolePolicy' OR eventName = 'DetachRolePolicy') AND eventTime > {1} AND eventTime < {2} AND (recipientAccountId = '{3}' OR recipientAccountId = '{4}' OR recipientAccountId = '{5}' OR recipientAccountId = '{6}')".format(self.datalake_id,self.startTime,self.endTime,self.account_id_payer,self.account_id_audit,self.account_id_logging,self.account_id_shared)
            
            response1 = self.cloudtrail_client.start_query(
                    QueryStatement=query_statement1,
                    DeliveryS3Uri=s3_uri_value1
                    )
                    
            print(response)
            account_id=self.account_id_payer
            current_date=str(self.current_date)
            current_date=current_date.replace('-','/')
            s3_object_uri='createFunction/AWSLogs/'+account_id+'/CloudTrail-Lake/Query/'+current_date+'/'+response['QueryId']+'/result_1.csv.gz'
            LOGGER.info(s3_object_uri)
            time.sleep(600)
            temp_file_path='/tmp/result_1.csv.gz'
            temp_file_key=str(s3_object_uri)
            self.s3_client.download_file(self.bucket_name,temp_file_key ,temp_file_path)
            
            list_of_dict_data = []
            jsonFilePath = '/tmp/result.json'
            with gzip.open(temp_file_path, 'rt') as gz_file:
                # Read the contents of the .gz file
                csv_content = csv.reader(gz_file)
                #print(csv_content)
                next(csv_content)
                next(csv_content)
                for row in csv_content:
                    print(row)
                    list_of_dict_data.append({'recipientAccountId':row[0],'awsRegion':row[1],'eventTime':row[2],'eventName':row[3],'username':row[4],'principalid':row[5],'type':row[6],'requestParameters':row[7]})
            len_list = len(list_of_dict_data)
            substr = 'functionName='
            for i in range(len_list):
                li = list_of_dict_data[i]['requestParameters'].split(',')
                lambda_FunctionName = ''
                for item in li:
                    if item.find(substr) != -1:
                        print(item[14:])
                        lambda_FunctionName = lambda_FunctionName+item[14:]
                list_of_dict_data[i]['lambda_FunctionName'] = lambda_FunctionName
                del list_of_dict_data[i]['requestParameters']
            
            fields = ['recipientAccountId','awsRegion','eventTime','eventName','username','principalid','type','lambda_FunctionName']    
            filename_create = "platform_lambda_creation_alert.csv"
            file_path_create = "/tmp/" + filename_create
                    
            with open(file_path_create, 'w') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fields)
                writer.writeheader()
                writer.writerows(list_of_dict_data)
                csvfile.close()
                
            bodystring = 'lambda function creation'
            self.send_email(file_path_create,bodystring)  

            self.get_rolePolicyAttached_alert_data(response1)  
            
            
        except Exception as e:
            print(str(e))
            
    
    def get_rolePolicyAttached_alert_data(self,response1):
        
        try:

            response = response1

            print(response)
            account_id=self.account_id_payer
            current_date=str(self.current_date)
            current_date=current_date.replace('-','/')
            s3_object_uri='rolePolicyAttached/AWSLogs/'+account_id+'/CloudTrail-Lake/Query/'+current_date+'/'+response['QueryId']+'/result_1.csv.gz'
            LOGGER.info(s3_object_uri)
            #time.sleep(60)
            temp_file_path='/tmp/result_1.csv.gz'
            temp_file_key=str(s3_object_uri)
            self.s3_client.download_file(self.bucket_name,temp_file_key ,temp_file_path)
            list_of_dict_data = []
            jsonFilePath = '/tmp/result.json'
            with gzip.open(temp_file_path, 'rt') as gz_file:
                # Read the contents of the .gz file
                csv_content = csv.reader(gz_file)
                #print(csv_content)
                next(csv_content)
                next(csv_content)
                for row in csv_content:
                    #print(row)
                    list_of_dict_data.append({'recipientAccountId':row[0],'awsRegion':row[1],'eventTime':row[2],'eventName':row[3],'username':row[4],'principalid':row[5],'type':row[6],'requestParameters':row[7]})
            
            len_list = len(list_of_dict_data)
            substr_policy = 'policyArn='
            substr_role = 'roleName='
            
            for i in range(len_list):
                refine_data = list_of_dict_data[i]['requestParameters']
                refine_data1 = refine_data.replace("}",'')
                li = refine_data1.split(',')
                policyArn = ''
                roleName = ''
                for item in li:
                    if item.find(substr_policy) != -1:
                        print(item[11:])
                        policyArn = policyArn+item[11:]
                    elif item.find(substr_role) != -1:
                        roleName = roleName+item[10:]
                    else:
                        policyArn = policyArn+'NA'
                        roleName = roleName+'NA'
                list_of_dict_data[i]['policyArn'] = policyArn
                list_of_dict_data[i]['roleName'] = roleName
                del list_of_dict_data[i]['requestParameters']
                
            print(list_of_dict_data)
            fields = ['recipientAccountId','awsRegion','eventTime','eventName','username','principalid','type','policyArn','roleName']    
            filename_create = "Role_policy_attach_alert.csv"
            file_path_create = "/tmp/" + filename_create
                    
            with open(file_path_create, 'w') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fields)
                writer.writeheader()
                writer.writerows(list_of_dict_data)
                csvfile.close()
                
            bodystring = 'Role Policy attached'
            self.send_email(file_path_create,bodystring)    
            #print(list_of_dict_data)
        
        except Exception as e:
            print(str(e))
            raise Exception(str(e))

def lambda_handler(event, context):
    try:
        # TODO implement
        object =lambdaAlert(event,context)
        object.get_lambda_alert_data()
        #object.get_rolePolicyAttached_alert_data()
        return {
            'statusCode': 200,
            'body': json.dumps('Hello from Lambda!')
        }
    except Exception as ex:
        LOGGER.error("Lambda failed with the error:'{0}'".format(ex))
        return "FAILED"
