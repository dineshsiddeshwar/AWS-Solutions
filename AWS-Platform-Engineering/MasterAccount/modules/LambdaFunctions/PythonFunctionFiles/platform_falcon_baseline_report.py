import csv
import boto3
import sys
import logging
import datetime
import calendar
import os
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
class falcon:
    """method: function to filter instances with agent exception tag"""
    def __init__(self):
        LOGGER.info("in init")
        self.final=[] 
        self.instance_id=[]
        self.s3=boto3.client("s3")
        self.bucket_name=os.environ['BUCKET']
        current_year = str(datetime.datetime.now().year)
        current_month = calendar.month_name[datetime.datetime.now().month]
        self.s3_object="Monthly-Reports/master_inventory_list_"+current_month+"_"+current_year+".csv"
        obj=self.s3.get_object(Bucket=self.bucket_name,Key=self.s3_object)
        self.session = boto3.session.Session()
        self.ses_client = self.session.client('ses')
        self.ssm_client = self.session.client('ssm')

    def agent_exception(self):
        """method: function to filter instances with agent exception tag"""
        LOGGER.info("in agent exception")
        csv_obj = self.s3.get_object(Bucket=self.bucket_name, Key=self.s3_object)
        body = csv_obj['Body']
        csv_string = body.read().decode('utf-8')
        csvreader = csv.reader(StringIO(csv_string))
        global_l=[]
        try:
            for row in csvreader:
                tag_string=row[12]
                tag_string=tag_string[1:len(tag_string)-1]
                tag=tag_string.split(",")
                final_data={}
                input_data={}
                for word in tag:
                    word=word.strip()
                    if word[2:5]=="Key" and word[9:len(word)-1]=="Agents_Exception":
                        input_data['account_id']=row[0]
                        input_data['ou_name']=row[1]
                        input_data['account_name']=row[2]
                        input_data['account_workload']=row[3]
                        input_data['instanceType']=row[4]
                        input_data['instance_id']=row[5]
                        input_data['imageid']=row[6]
                        input_data['subnetid']=row[7]
                        input_data['vpcid']=row[8]
                        input_data['lastlauncheddate']=row[9]
                        input_data['state']=row[10]
                        input_data['privateipaddress']=row[11]
                        input_data['tags']=row[12]
                        global_l.append(input_data) 
                        final_data=input_data.copy()
                        final_data['reason for exclusion']='Agent exception'
                        self.final.append(final_data) 
                        self.instance_id.append(row[4])
                        break
        
            column_names=['account_id','ou_name','account_name','account_workload','instance_id','instanceType','imageid','subnetid','vpcid','lastlauncheddate','state','privateipaddress','tags']
            with open('/tmp/Agent_Exception.csv', 'w') as out:
                writer = csv.DictWriter(out,fieldnames=column_names)
                writer.writeheader()
                writer.writerows(global_l)
                self.s3.upload_file("/tmp/Agent_Exception.csv",self.bucket_name,"/tmp/Agent_Exception.csv")
        except Exception as ex:
            LOGGER.error("Lambda failed with the error:'{0}'".format(ex))
            return "FAILED"

    def kiteworks(self):
        """method: function to filter instances with kiteworks exception tag"""
        LOGGER.info("in kiteworks")
        csv_obj = self.s3.get_object(Bucket=self.bucket_name, Key=self.s3_object)
        body = csv_obj['Body']
        csv_string = body.read().decode('utf-8')
        csvreader = csv.reader(StringIO(csv_string))
        global_l=[]
        try:
            for row in csvreader:
                final_data={}
                input_data={}
                if row[0]=="558250107255" or row[0]=="704564691918" or row[0]=="859797659877":
                    input_data['account_id']=row[0]
                    input_data['ou_name']=row[1]
                    input_data['account_name']=row[2]
                    input_data['account_workload']=row[3]
                    input_data['instance_id']=row[4]
                    input_data['instanceType']=row[5]
                    input_data['imageid']=row[6]
                    input_data['subnetid']=row[7]
                    input_data['vpcid']=row[8]
                    input_data['lastlauncheddate']=row[9]
                    input_data['state']=row[10]
                    input_data['privateipaddress']=row[11]
                    input_data['tags']=row[12]
                    global_l.append(input_data) 
                    final_data=input_data.copy()
                    final_data['reason for exclusion']='Kiteworks'
                    self.final.append(final_data) 
                    self.instance_id.append(row[4])
            column_names=['account_id','ou_name','account_name','account_workload','instance_id','instanceType','imageid','subnetid','vpcid','lastlauncheddate','state','privateipaddress','tags']
            with open('/tmp/Kitework.csv', 'w') as out:
                writer = csv.DictWriter(out,fieldnames=column_names)
                writer.writeheader()
                writer.writerows(global_l)
                self.s3.upload_file("/tmp/Kitework.csv",self.bucket_name,"/tmp/Kitework.csv")
        except Exception as ex:
            LOGGER.error("Lambda failed with the error:'{0}'".format(ex))
            return "FAILED"
            
    def clusters(self):
        """method: function to filter instances with eks clusters tag"""
        csv_obj = self.s3.get_object(Bucket=self.bucket_name, Key=self.s3_object)
        body = csv_obj['Body']
        csv_string = body.read().decode('utf-8')
        csvreader = csv.reader(StringIO(csv_string))
        LOGGER.info("in clusters")
        global_l=[]
        try:
            for row in csvreader:
                final_data={}
                input_data={}
                tag_string=row[12]
                tag_string=tag_string[1:len(tag_string)-1]
                tag=tag_string.split(",")
                for word in tag:
                    word=word.strip()
                    if word[2:5]=="Key" and word[9:len(word)-1]=='aws:eks:cluster-name':
                        input_data['account_id']=row[0]
                        input_data['ou_name']=row[1]
                        input_data['account_name']=row[2]
                        input_data['account_workload']=row[3]
                        input_data['instance_id']=row[4]
                        input_data['instanceType']=row[5]
                        input_data['imageid']=row[6]
                        input_data['subnetid']=row[7]
                        input_data['vpcid']=row[8]
                        input_data['lastlauncheddate']=row[9]
                        input_data['state']=row[10]
                        input_data['privateipaddress']=row[11]
                        input_data['tags']=row[12]
                        global_l.append(input_data) 
                        final_data=input_data.copy()
                        final_data['reason for exclusion']='Clusters'
                        self.final.append(final_data) 
                        self.instance_id.append(row[4])
                        break
            column_names=['account_id','ou_name','account_name','account_workload','instance_id','instanceType','imageid','subnetid','vpcid','lastlauncheddate','state','privateipaddress','tags']
            with open('/tmp/Clusters.csv', 'w') as out:
                writer = csv.DictWriter(out,fieldnames=column_names)
                writer.writeheader()
                writer.writerows(global_l)
                self.s3.upload_file("/tmp/Clusters.csv",self.bucket_name,"/tmp/Clusters.csv")
        except Exception as ex:
            LOGGER.error("Lambda failed with the error:'{0}'".format(ex))
            return "FAILED"
            
    def test_account(self):
        """method: function to filter test account instances"""
        global_l=[]
        LOGGER.info("in test account")
        k=0
        csv_obj = self.s3.get_object(Bucket=self.bucket_name, Key=self.s3_object)
        body = csv_obj['Body']
        csv_string = body.read().decode('utf-8')
        csvreader = csv.reader(StringIO(csv_string))
        try:
            for row in csvreader:
                input_data={}
                final_data={}
                if row[0]=="641011229815":
                    input_data['account_id']=row[0]
                    input_data['ou_name']=row[1]
                    input_data['account_name']=row[2]
                    input_data['account_workload']=row[3]
                    input_data['instance_id']=row[4]
                    input_data['instanceType']=row[5]
                    input_data['imageid']=row[6]
                    input_data['subnetid']=row[7]
                    input_data['vpcid']=row[8]
                    input_data['lastlauncheddate']=row[9]
                    input_data['state']=row[10]
                    input_data['privateipaddress']=row[11]
                    input_data['tags']=row[12]
                    global_l.append(input_data) 
                    final_data=input_data.copy()
                    final_data['reason for exclusion']='Test Account'
                    self.final.append(final_data) 
                    self.instance_id.append(row[4]) 
            column_names=['account_id','ou_name','account_name','account_workload','instance_id','instanceType','imageid','subnetid','vpcid','lastlauncheddate','state','privateipaddress','tags']
            with open('/tmp/Test_Account.csv', 'w') as out:
                writer = csv.DictWriter(out,fieldnames=column_names)
                writer.writeheader()
                writer.writerows(global_l)
                self.s3.upload_file("/tmp/Test_Account.csv",self.bucket_name,"/tmp/Test_Account.csv")
        except Exception as ex:
            LOGGER.error("Lambda failed with the error:'{0}'".format(ex))
            return "FAILED"    
    def service_team(self):
        """method: fucntion to filter instances with service-team tag"""
        global_l=[]
        LOGGER.info("in service team")
        k=0
        csv_obj = self.s3.get_object(Bucket=self.bucket_name, Key=self.s3_object)
        body = csv_obj['Body']
        csv_string = body.read().decode('utf-8')
        csvreader = csv.reader(StringIO(csv_string))
        try:
            for row in csvreader:
                final_data={}
                input_data={}
                tag_string=row[12]
                tag_string=tag_string[1:len(tag_string)-1]
                tag=tag_string.split(",")
                for word in tag:
                    word=word.strip()
                    if word[2:5]=="Key" and word[9:len(word)-1]=="service-team" :
                        input_data['account_id']=row[0]
                        input_data['ou_name']=row[1]
                        input_data['account_name']=row[2]
                        input_data['account_workload']=row[3]
                        input_data['instance_id']=row[4]
                        input_data['instanceType']=row[5]
                        input_data['imageid']=row[6]
                        input_data['subnetid']=row[7]
                        input_data['vpcid']=row[8]
                        input_data['lastlauncheddate']=row[9]
                        input_data['state']=row[10]
                        input_data['privateipaddress']=row[11]
                        input_data['tags']=row[12]
                        global_l.append(input_data) 
                        final_data=input_data.copy()
                        final_data['reason for exclusion']='Service Team'
                        self.final.append(final_data) 
                        self.instance_id.append(row[4]) 
                        break
            column_names=['account_id','ou_name','account_name','account_workload','instance_id','instanceType','imageid','subnetid','vpcid','lastlauncheddate','state','privateipaddress','tags']
            with open('/tmp/Service_Team.csv', 'w') as out:
                writer = csv.DictWriter(out,fieldnames=column_names)
                writer.writeheader()
                writer.writerows(global_l)
                self.s3.upload_file("/tmp/Service_Team.csv",self.bucket_name,"/tmp/Service_Team.csv")
        except Exception as ex:
            LOGGER.error("Lambda failed with the error:'{0}'".format(ex))
            return "FAILED"    
    def stopped(self):
        """method: function to filter stopped instances"""
        global_l=[]
        LOGGER.info("in stopped")
        k=0
        csv_obj = self.s3.get_object(Bucket=self.bucket_name, Key=self.s3_object)
        body = csv_obj['Body']
        csv_string = body.read().decode('utf-8')
        csvreader = csv.reader(StringIO(csv_string))
        try:
            for row in csvreader:
                input_data={}
                final_data={}
                if row[10]=='stopped':
                    input_data['account_id']=row[0]
                    input_data['ou_name']=row[1]
                    input_data['account_name']=row[2]
                    input_data['account_workload']=row[3]
                    input_data['instance_id']=row[4]
                    input_data['instanceType']=row[5]
                    input_data['imageid']=row[6]
                    input_data['subnetid']=row[7]
                    input_data['vpcid']=row[8]
                    input_data['lastlauncheddate']=row[9]
                    input_data['state']=row[10]
                    input_data['privateipaddress']=row[11]
                    input_data['tags']=row[12] 
                    global_l.append(input_data) 
                    final_data=input_data.copy()
                    final_data['reason for exclusion']='Stopped'
                    self.final.append(final_data) 
                    self.instance_id.append(row[4]) 
            column_names=['account_id','ou_name','account_name','account_workload','instance_id','instanceType','imageid','subnetid','vpcid','lastlauncheddate','state','privateipaddress','tags']
            with open('/tmp/Stopped.csv', 'w') as out:
                writer = csv.DictWriter(out,fieldnames=column_names)
                writer.writeheader()
                writer.writerows(global_l)
                self.s3.upload_file("/tmp/Stopped.csv",self.bucket_name,"/tmp/Stopped.csv")
        except Exception as ex:
            LOGGER.error("Lambda failed with the error:'{0}'".format(ex))
            return "FAILED"
            
    def baseline_rep(self):
        """method: function to filter instances that are excluded"""
        LOGGER.info("in baseline")
        k=0
        global_l=[]
        csv_obj = self.s3.get_object(Bucket=self.bucket_name, Key=self.s3_object)
        body = csv_obj['Body']
        csv_string = body.read().decode('utf-8')
        csvreader = csv.reader(StringIO(csv_string))
        self.instance_id=[*set(self.instance_id)]
        print(len(self.final))
        try:
            for row in csvreader:
                input_data={}
                if row[4] not in self.instance_id:
                    input_data['account_id']=row[0]
                    input_data['ou_name']=row[1]
                    input_data['account_name']=row[2]
                    input_data['account_workload']=row[3]
                    input_data['instance_id']=row[4]
                    input_data['instanceType']=row[5]
                    input_data['imageid']=row[6]
                    input_data['subnetid']=row[7]
                    input_data['vpcid']=row[8]
                    input_data['lastlauncheddate']=row[9]
                    input_data['state']=row[10]
                    input_data['privateipaddress']=row[11]
                    input_data['tags']=row[12]
                    global_l.append(input_data)
            column_names=['account_id','ou_name','account_name','account_workload','instance_id','instanceType','imageid','subnetid','vpcid','lastlauncheddate','state','privateipaddress','tags']
            with open('/tmp/Baseline.csv', 'w') as out:
                writer = csv.DictWriter(out,fieldnames=column_names)
                writer.writeheader()
                writer.writerows(global_l)
                self.s3.upload_file("/tmp/Baseline.csv",self.bucket_name,"/tmp/Baseline.csv")
        except Exception as ex:
            LOGGER.error("Lambda failed with the error:'{0}'".format(ex))
            return "FAILED"

    def exclusions(self):
        try:
            final_column_names=['account_id','ou_name','account_name','account_workload','instance_id','instanceType','imageid','subnetid','vpcid','lastlauncheddate','state','privateipaddress','tags','reason for exclusion']
            with open('/tmp/exclusion.csv', 'w') as out:
                writer = csv.DictWriter(out,fieldnames=final_column_names)
                writer.writeheader()
                writer.writerows(self.final)
                self.s3.upload_file("/tmp/exclusion.csv",self.bucket_name,"/tmp/exclusion.csv")
        except Exception as ex:
            LOGGER.error("Lambda failed with the error:'{0}'".format(ex))
            return "FAILED"
            
    def send_mail(self):
        try:
            file_name_list=['/tmp/Clusters.csv','/tmp/Baseline.csv','/tmp/exclusion.csv','/tmp/Stopped.csv','/tmp/Agent_Exception.csv','/tmp/Kitework.csv','/tmp/Test_Account.csv','/tmp/Service_Team.csv']
            print("Inside Send Mail")
            sender_response = self.ssm_client.get_parameter(Name='sender_id')
            sender_id = sender_response['Parameter']['Value']
            rec_response = "GX-IDSO-ETSOM-DP-CLOUD-AWS-DEVOPS@shell.com, zaheer.ahmed@shell.com"
            to_recipient = rec_response
            recipient_list = to_recipient.split(',')
        # The email body for recipients with non-HTML email clients.
            body_text = "Hello\r\nPlease find the attached filtered reports and the baseline report for AWS@Shell."\
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
                mail_subject = "Falcon Baseline Reports"
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
            self.s3.delete_objects(Bucket=self.bucket_name, Delete={"Objects":[{"Key":"/tmp/Clusters.csv"},{"Key":"/tmp/Baseline.csv"},{"Key":"/tmp/exclusion.csv"},{"Key":"/tmp/Stopped.csv"},
            {"Key":"/tmp/Agent_Exception.csv"},{"Key":"/tmp/Kitework.csv"},{"Key":"/tmp/Test_Account.csv"},{"Key":"/tmp/Service_Team.csv"}]})
        except Exception as ex:
            LOGGER.error("Lambda failed with the error:'{0}'".format(ex))
            return "FAILED"
def lambda_handler(event,context):
    try:
        LOGGER.info("Calling classs object")
        obj=falcon()
        LOGGER.info("Calling agent exception tag filtering function")
        obj.agent_exception() 
        LOGGER.info("Calling kiteworks tag filtering function") 
        obj.kiteworks()
        LOGGER.info("Calling clusters tag filtering function")
        obj.clusters()
        LOGGER.info("Calling test account tag filtering function")
        obj.test_account()
        LOGGER.info("Calling service team tag filtering function")
        obj.service_team()
        LOGGER.info("Calling stopped instances filtering function")
        obj.stopped()
        LOGGER.info("Calling baseline report filtering function")
        obj.baseline_rep()
        LOGGER.info("Calling exclusions filtering function")
        obj.exclusions()
        LOGGER.info("Calling send email function")
        obj.send_mail()
        LOGGER.info("Deleting folder from s3")
        obj.delete_from_s3()
    except Exception as ex:
        LOGGER.error("Lambda failed with the error:'{0}'".format(ex))
        return "FAILED"

    
    