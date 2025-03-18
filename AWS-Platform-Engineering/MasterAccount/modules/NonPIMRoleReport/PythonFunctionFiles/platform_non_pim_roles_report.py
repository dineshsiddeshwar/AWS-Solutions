import csv
import boto3
import sys
import logging
import datetime
import calendar
import os
import datetime
import gzip
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from boto3.dynamodb.conditions import Key, Attr
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
from io import StringIO # Python 3.x
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
LOGGER.addHandler(CH)
class roles_report:
    def __init__(self):
        LOGGER.info("in init")
        self.session = boto3.session.Session()
        self.ses_client = self.session.client('ses')
        self.ssm_client = self.session.client('ssm')
        self.cloudtrail_client = self.session.client('cloudtrail')
        self.s3=boto3.client("s3")
        self.bucket_name=os.environ['BUCKET']

    def run_query(self):
        try:
            current_datetime = datetime.datetime.now()
            current_date = current_datetime.date()
            startTime = (datetime.datetime.now() - datetime.timedelta(days=31)).isoformat()
            startTime=str(startTime)
            LOGGER.info("get the date out of the datetime object")
            startTime="'"+startTime[:10]+ " 00:00:00"+"'"
            LOGGER.info(startTime)
            endTime=str(current_date)+ " 00:00:00"
            endTime="'"+endTime+"'"
            LOGGER.info(endTime)
            self.s3_uri='s3://'+self.bucket_name+'/'
            sender_response_psexternal = self.ssm_client.get_parameter(Name='platform_contributorexternalrolearn')
            sender_response_psmaster = self.ssm_client.get_parameter(Name='platform_mastercontributorrolearn')
            sender_response_datalakeid = self.ssm_client.get_parameter(Name='platform_datalakeid')
            s3_uri_value='s3://'+os.environ['BUCKET']+'/'
            permission_set_external="'"+sender_response_psexternal['Parameter']['Value']+"'"
            permission_set_master="'"+sender_response_psmaster['Parameter']['Value']+"'"
            account_id_payer="'"+self.getAccountId()+"'"
            account_id_audit="'"+os.environ['AUDIT_ACCOUNT_ID']+"'"
            account_id_logging="'"+os.environ['LOGGING_ACCOUNT_ID']+"'"
            account_id_shared="'"+os.environ['SHARED_ACCOUNT_ID']+"'"
            datalake_id=sender_response_datalakeid['Parameter']['Value']
            query_statement="""
            SELECT useridentity.sessioncontext.sessionissuer.username,useridentity.principalid,useridentity.type,eventtype,recipientAccountId, awsregion, eventid, eventname,responseElements,readOnly, eventsource, eventtime, sourceipaddress, errorcode, errormessage from """ + datalake_id + """ WHERE recipientAccountId = """+account_id_payer+""" AND eventTime > """ + startTime + """ AND eventTime < """ + endTime + """ AND readOnly = false AND eventname in ('CreateAccountAssignment','DeleteAccountAssignment') AND NOT (useridentity.sessioncontext.sessionissuer.username='platform_Operator') AND (useridentity.sessioncontext.sessionissuer.username NOT LIKE 'amplify-teamidcapp-main%') AND (useridentity.sessioncontext.sessionissuer.username NOT LIKE 'platform_Admin') AND ((element_at(requestParameters, 'permissionSetArn') LIKE """+permission_set_external+""") OR (element_at(requestParameters, 'permissionSetArn') LIKE """+permission_set_master+""")) AND (element_at(requestParameters,'targetId') in ("""+account_id_payer+""","""+account_id_audit+""","""+account_id_logging+""","""+account_id_shared+"""))
            """
            response = self.cloudtrail_client.start_query(
                QueryStatement=query_statement,
                DeliveryS3Uri=s3_uri_value,
                )
            account_id=self.getAccountId()
            current_date=str(current_date)
            current_date=current_date.replace('-','/')
            s3_object_uri='AWSLogs/'+account_id+'/CloudTrail-Lake/Query/'+current_date+'/'+response['QueryId']+'/result_1.csv.gz'
            LOGGER.info(s3_object_uri)
            time.sleep(120)
            self.send_results(s3_object_uri,str(response['QueryId']))
        except Exception as exception:
            print(exception)

    def send_results(self,s3_object_uri,response):
        try:
            file_key=s3_object_uri
            print("Inside Send Mail")
            sender_response = self.ssm_client.get_parameter(Name='sender_id')
            sender_id = "SITI-ECP-AWS-AT-SHELL@shell.com"
            rec_response = "GX-SITI-CPE-Team-Titan@shell.com"
            to_recipient = rec_response
            recipient_list = to_recipient.split(',')
        # The email body for recipients with non-HTML email clients.
            body_text = "Hello\r\nPlease find the attached filtered non-PIM roles report for AWS@Shell."\
                                                                      "\r\nRegards,\r\nAWS@Shell Platform Engineering Team"
        # The HTML body of the email.
            body_html = """<html>
        <head></head>
        <body>
        <p style="font-family:'Futura Medium'">Hello Team,</p>
        <p style="font-family:'Futura Medium'">Please find the attached filtered non-PIM roles report for AWS@Shell.</p>
        <p style="font-family:'Futura Medium'">Best Regards,</p>
        <p style="font-family:'Futura Medium'">AWS@Shell Platform Engineering Team</p>
        <href>GX-SITI-CPE-Team-Titan@shell.com</href>
        </body>
        </html>
        """
            try:
                temp_file_path='/tmp/result_1.csv.gz'
                temp_file_key=str(s3_object_uri)
                #temp_file_key='AWSLogs/364355817034/CloudTrail-Lake/Query/2023/10/18/'+response+'/result_1.csv.gz'
                self.s3.download_file(self.bucket_name,temp_file_key ,'/tmp/result_1.csv.gz')
                with gzip.open(temp_file_path, 'rb') as gz_file:
                    # Read the contents of the .gz file
                    csv_content = gz_file.read()
                with open('/tmp/Monthly_Non_Pim_Roles_Assumed_Report.csv', 'wb') as csv_file:
                    csv_file.write(csv_content)
                    self.s3.upload_file("/tmp/Monthly_Non_Pim_Roles_Assumed_Report.csv",self.bucket_name,"/tmp/Monthly_Non_Pim_Roles_Assumed_Report.csv")
                try:
                    LOGGER.info('mailing')
                    mail_subject = "Privileged Permission Set Assigned Directly (Without TEAM) On Accounts Reports for The Month"
                    #attachment_template = file_name  # "{}".format(file_name)
                    message = MIMEMultipart('mixed')
                    message['Subject'] = mail_subject
                    #message['From'] = sender_id
                    #message['To'] = to_recipient
                    message_body = MIMEMultipart('alternative')
                    char_set = "utf-8"
                    textpart = MIMEText(body_text.encode(char_set), 'plain', char_set)
                    htmlpart = MIMEText(body_html.encode(char_set), 'html', char_set)
                    message_body.attach(textpart)
                    message_body.attach(htmlpart)
                    attachment_template = '/tmp/Monthly_Non_Pim_Roles_Assumed_Report.csv'
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
                    LOGGER.info('mailed')

                except Exception as exception:
                   print(exception)

            except Exception as exception:
                print(exception)
        except Exception as exception:
            print(exception)
       
    def delete_from_s3(self):
        try:
            self.s3.delete_objects(Bucket=self.bucket_name, Delete={"Objects":[{"Key":"/tmp/Monthly_Non_Pim_Roles_Assumed_Report.csv"}]})
        except Exception as ex:
            LOGGER.error("Lambda failed with the error:'{0}'".format(ex))
            return "FAILED"    
        
    def getAccountId(self):
        try:
            sts_client = boto3.client('sts')
            response = sts_client.get_caller_identity()
            account_id = response['Account']
            return account_id    
        except Exception as ex:
            LOGGER.error("Lambda failed with the error:'{0}'".format(ex))
            return "FAILED"        

def lambda_handler(event,context):
    try:
        LOGGER.info("Calling classs object")
        obj=roles_report()
        LOGGER.info("Calling run query function")
        obj.run_query()   
        LOGGER.info("Deleting folder from s3")
        obj.delete_from_s3()
    except Exception as ex:
        LOGGER.error("Lambda failed with the error:'{0}'".format(ex))
        return "FAILED"
        