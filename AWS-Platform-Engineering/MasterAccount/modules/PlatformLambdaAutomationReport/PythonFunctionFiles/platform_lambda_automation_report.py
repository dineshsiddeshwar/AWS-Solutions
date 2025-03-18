import json
import boto3
import csv
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import logging
import datetime
import random
import calendar
import os.path



LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
LOGGER.addHandler(CH)

"""
This Lambda function is used to Filter core account (payer,shared,audit,logging) platform automation lambda data and attached policies
"""
class AccountMonitoring(object):
    """
    # Class: Core account Monitoring
    # Description: Core account platform lambda Monitoring solution
    """

    def __init__(self,event, context):
        try:
            LOGGER.info("in init")
            session = boto3.session.Session()
            self.config_client = boto3.client('config',region_name = 'us-east-1')
            self.ses_client = session.client('ses')
            self.ssm_client = session.client('ssm')
            response_aggregatorName = self.ssm_client.get_parameter(Name='ConfigAggregatorName')
            self.aggregatorName = response_aggregatorName['Parameter']['Value']
            #self.count = 0
            self.account_id_payer=os.environ['MASTER_ACCOUNT_ID']
            self.account_id_audit=os.environ['AUDIT_ACCOUNT_ID']
            self.account_id_logging=os.environ['LOGGING_ACCOUNT_ID']
            self.account_id_shared=os.environ['SHARED_ACCOUNT_ID']
            self.year = str(datetime.datetime.today().year)
            self.month = str(datetime.datetime.today().month)
            self.month_name = calendar.month_name[int(self.month)]
            self.bucketName = os.environ['BUCKET']
            self.filename_mail = "platform_automation_report_for_"+ self.month +".csv"
            self.file_path_mail =  "/tmp/" + self.filename_mail
            
            self.refine_data_list = []
            self.policy_list = []
            
        except Exception as e:
            print(str(e))
            raise Exception(str(e))
            
    def upload_audit_s3(self,data,fields,flag):
        try:
            
            #s3_client = self.assumeRoleSession.client('s3', region_name='us-east-1')
            s3_client = boto3.client('s3', region_name='us-east-1')

            if flag == 0:
                month = str(int(self.month)-1)
                filename = "platform_automation_report_"+ month +".csv"
                file_path = "/tmp/" + filename
                key = '/'.join([self.year,month,filename])
            else:
                filename = "platform_automation_report_"+self.month +".csv"
                file_path = "/tmp/" + filename
                key = '/'.join([self.year,self.month,filename])
            
            with open(file_path, 'w') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fields)
                writer.writeheader()
                writer.writerows(data)
                csvfile.close()
            print("Trying to upload consolidated file")
            response = s3_client.upload_file(file_path, self.bucketName ,key)
            
            print("File uploaded successfully!!!")
        
        except Exception as e:
            print(str(e))
            raise Exception(str(e))
            
    def report_data(self,list_data,policy_data):
        try:
            LOGGER.info("inside report_data function")
            for i in range(len(list_data)):
                if policy_data[i] != 'NA':
                    list_data[i]['PolicyAttached'] = policy_data[i]['policyName']
                else:
                    list_data[i]['PolicyAttached'] = policy_data[i]
            
            
            s3_client = boto3.client('s3', region_name='us-east-1')
            response = s3_client.list_objects_v2(Bucket = self.bucketName)

            list_response = response['Contents']
            flag = 0
            yearstr = self.year+'/'
            for item in list_response:
                if item['Key'].startswith(yearstr):
                    flag = 1
            
            # field names
            fields = ['accountId', 'awsRegion', 'resourceName', 'roleType' , 'roleName', 'roleARN' , 'PolicyAttached']
            
            
            if int(self.month) >1:
                month = str(int(self.month)-1)
                filename_download = "platform_automation_report_"+ month +".csv"
                file_path_download = "/tmp/" + filename_download
                key_download = '/'.join([self.year,month,filename_download])
            
            else:
                month = '12'
                year = str(int(self.year)-1)
                filename_download = "platform_automation_report_"+ month +".csv"
                file_path_download = "/tmp/" + filename_download
                key_download = '/'.join([year,month,filename_download])
                
            if flag == 1:
                
                print('trying to download file from s3 bucket')
                s3_client.download_file(self.bucketName,key_download, file_path_download)
                print('file downloaded successfully!!!!')
                
                filename_create = "platform_automation_report_"+ self.month +".csv"
                file_path_create = "/tmp/" + filename_create
                
                with open(file_path_create, 'w') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fields)
                    writer.writeheader()
                    writer.writerows(self.refine_data_list)
                    csvfile.close()
                
                print('comparing files=====')
                
                with open(file_path_download,'r') as t1,open(file_path_create,'r') as t2:
                    fileone = t1.readlines()
                    filetwo = t2.readlines()
                with open(self.file_path_mail, 'w') as outfile:
                    writer = csv.DictWriter(outfile, fieldnames=fields)
                    writer.writeheader()
                    for line in filetwo:
                        if line not in fileone:
                            outfile.write(line)
                     
                print('comparison completed=====')
                            
                self.upload_audit_s3(self.refine_data_list,fields,flag)
                LOGGER.info("invoking send_mail function")
                self.send_email()
                
                
            else:
                self.upload_audit_s3(self.refine_data_list,fields,flag)
                LOGGER.info("Since no data is uploaded yet for reference so this run upload the data and next month run will send the report")
                
                        
            LOGGER.info("report_data function completed successfully")
            
            
        except Exception as e:
            print(str(e))
            raise Exception(str(e))
       
    def get_policy(self,accountid,roleName):
        
        try:
            LOGGER.info("inside get_policy")
            policy_responce = self.config_client.select_aggregate_resource_config(
            Expression= "SELECT accountId,awsRegion,configuration.attachedManagedPolicies.policyName,configuration.rolePolicyList.policyName  WHERE resourceType = 'AWS::IAM::Role' AND accountId = '{0}' AND configuration.roleName = '{1}'".format(accountid,roleName),
            ConfigurationAggregatorName=self.aggregatorName
            )
            changed_resources = policy_responce["Results"]
            if len(changed_resources)>0:
                json_list = [json.loads(line) for line in changed_resources]
                if len(json_list[0])>=3 and 'attachedManagedPolicies' in json_list[0]['configuration'].keys() and 'rolePolicyList' in json_list[0]['configuration'].keys():
                    l1 = json_list[0]['configuration']['attachedManagedPolicies']
                    l2 = json_list[0]['configuration']['rolePolicyList']
                    li = l1+l2
                    string = ''
                    dict_test = {}
                    for item in li:
                        string = string+item['policyName']+','
                    dict_test['policyName'] = string

                    self.policy_list.append(dict_test)
                    
                elif 'attachedManagedPolicies' in json_list[0]['configuration'].keys():
                    li = json_list[0]['configuration']['attachedManagedPolicies']
                    string = ''
                    dict_test = {}
                    #list_test = []
                    for item in li:
                        string = string+item['policyName']+','
                    dict_test['policyName'] = string

                    self.policy_list.append(dict_test)
                    
                elif 'rolePolicyList' in json_list[0]['configuration'].keys():
                    li = json_list[0]['configuration']['rolePolicyList']
                    string = ''
                    dict_test = {}
                    for item in li:
                        string = string+item['policyName']+','
                    dict_test['policyName'] = string

                    self.policy_list.append(dict_test)
                else:
                    self.policy_list.append('NA')
            else:
                self.policy_list.append('NA')
        
        except Exception as e:
            print(str(e))
            print('error inside get_policy function')
            raise Exception(str(e))
    
    
    def Core_Account_data(self):
        try:
            LOGGER.info("inside Core_Account_data")
            
            data_list = []
            
            paginator = self.config_client.get_paginator('select_aggregate_resource_config')
            response_iterator = paginator.paginate(
                Expression= "SELECT accountId,awsRegion,configuration.role,resourceName,relationships.resourceType,relationships.resourceName WHERE resourceType = 'AWS::Lambda::Function' AND (configuration.functionName LIKE 'platform%' OR configuration.functionName LIKE 'Platform%') AND (accountId = '{0}' OR accountId = '{1}' OR accountId = '{2}' OR accountId = '{3}')".format(self.account_id_payer,self.account_id_shared,self.account_id_audit,self.account_id_logging),
                ConfigurationAggregatorName=self.aggregatorName
                )
            
            for response in response_iterator:
                changed_resources = response["Results"]
                json_list = [json.loads(line) for line in changed_resources]
                data_list = data_list+json_list
            
            for dict_data in data_list:
                dict_data['roleType']=dict_data['relationships'][0]['resourceType']
                dict_data['roleName']=dict_data['relationships'][0]['resourceName']
                dict_data['roleARN'] = dict_data['configuration']['role']
                del dict_data['relationships']
                del dict_data['configuration']
                self.refine_data_list.append(dict_data)
                
            for item in self.refine_data_list:
                accountid = item['accountId']
                roleName = item['roleName']
                self.get_policy(accountid,roleName)
            
            LOGGER.info("invoking report_data function")    
            self.report_data(self.refine_data_list,self.policy_list)
            
            

        except Exception as e:
            print(str(e))
            raise Exception(str(e))
    
    def send_email(self):
        try:
            LOGGER.info("inside send_email")
            sender_id = "SITI-ECP-AWS-AT-SHELL@shell.com"
            recipient_list = ['GX-SITI-CPE-Team-Titan@shell.com','GX-IDSO-SOM-ET-DP-CLOUD-SECURITY-COMPLIANCE@shell.com']
            body_text = "Hello\r\nPlease find the attached platform-automation report for AWS@Shell core Account."\
                                                                          "\r\nRegards,\r\nAWS@Shell Platform Engineering Team"
            # The HTML body of the email.
            body_html = """<html>
            <head></head>
            <body>
            <p style="font-family:'Futura Medium'">Hello Team,</p>
            <p style="font-family:'Futura Medium'">Please find the attached platform-automation report for AWS@Shell.</p>
            <p style="font-family:'Futura Medium'">Best Regards,</p>
            <p style="font-family:'Futura Medium'">AWS@Shell Platform Engineering Team</p>
            <href>GX-SITI-CPE-Team-Titan@shell.com</href>
            </body>
            </html>
            """
            if self.account_id_payer == '604596384198':
                mail_subject = "{0}- Platform Automation Reports for The Month-{1}".format("Prod",self.month_name)
            elif self.account_id_payer == '136349175397':
                mail_subject = "{0}- Platform Automation Reports for The Month-{1}".format("UAT",self.month_name)
            else:
                mail_subject = "{0}- Platform Automation Reports for The Month-{1}".format("Dev",self.month_name)
            message = MIMEMultipart('mixed')
            message['Subject'] = mail_subject
            message_body = MIMEMultipart('alternative')
            char_set = "utf-8"
            textpart = MIMEText(body_text.encode(char_set), 'plain', char_set)
            htmlpart = MIMEText(body_html.encode(char_set), 'html', char_set)
            message_body.attach(textpart)
            message_body.attach(htmlpart)
            attachment_template = self.file_path_mail
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
    



def lambda_handler(event, context):
    
    try:
        LOGGER.info("Calling classs object")
        Acct_Mobj = AccountMonitoring(event, context)
        Acct_Mobj.Core_Account_data()
    
    except Exception as ex:
        LOGGER.error("Lambda failed with the error:'{0}'".format(ex))
        return "FAILED"
