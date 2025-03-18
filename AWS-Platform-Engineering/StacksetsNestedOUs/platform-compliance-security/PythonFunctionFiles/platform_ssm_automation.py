import os
import logging
import json
import random
import boto3
import csv
import datetime
import calendar
from datetime import timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
LOGGER.addHandler(CH)

class mail_automation(object):
    """class: bundles the functions for ssm mail automation
    object: object for the class"""
    def __init__(self, event, context):
        """method: main function for global variables
        event: get the event from lambda 
        context: runtime environment context of the lambda"""
        self.event = event
        self.context = context
        self.session_client = boto3.session.Session()
        self.sts_client = self.session_client.client('sts')
        self.end_time=datetime.datetime.now(timezone.utc)
        self.ec2_client = self.session_client.client('ec2')
        self.session = boto3.session.Session()
        self.ses_client = self.session.client('ses')
        self.ssm_client = boto3.client('ssm')
        self.account_number = self.sts_client.get_caller_identity()['Account']
        
    def child_account_instances_compliant(self):
        try:
            """method: gets ssm details on instances and checks if it requires reconciliation
            param: account number of the current account"""
            regions_response = self.ssm_client.get_parameter(Name='platform_whitelisted_regions')
            regions_results = regions_response['Parameter']['Value']
            regions = regions_results.split(',')
            instanceidlist=[]
            imagelist=[]
            regionlist=[]
            instance_details_dict={}
            region_details_dict={}
            for region in regions:
                LOGGER.info(regions)
                region_info = []
                ssm_prmtr_client=boto3.client('ssm',region_name=region)
                response = ssm_prmtr_client.get_parameter(Name='/Platform-Tag/platform_Custodian')
                custodian=response['Parameter']['Value']
                ec2_client = boto3.client('ec2', region_name=region)
                ec2_response = ec2_client.describe_instances(MaxResults=999, Filters=[{
                'Name': 'tag:platform_ssminstall', 'Values': ['yes']}])
                if ec2_response['Reservations']:
                    for item in ec2_response['Reservations']:
                        instance = {}
                        for elements in item['Instances']:
                            image_id = elements['ImageId']
                            instance_id=elements['InstanceId']
                            image_details = ec2_client.describe_images(ImageIds=[image_id])
                            for item in image_details:
                                temp = image_details[item]
                                for temp_items in temp:
                                    if 'Name' in temp_items:
                                        instance['ImageName'] = temp_items['Name']
                            if 'ImageName' not in instance:
                                instance['ImageName'] = ''
                            if 'PublicIpAddress' in elements:
                                instance['PublicIpAddress'] = elements['PublicIpAddress']
                            else:
                                instance['PublicIpAddress'] = ' '
                            start_time=elements['LaunchTime']
            
                            ssm_response = boto3.client('ssm',region_name=region).describe_instance_information(
                            InstanceInformationFilterList=[
                               {
                                'key': 'InstanceIds',
                                'valueSet': [
                                    elements['InstanceId'],
                                ]
                                },
                            ]
                            )
                            print("SSM Response",ssm_response['InstanceInformationList'])
                            ping_status=''
                            #start_time=end_time
                            for parameter in ssm_response['InstanceInformationList']:
                                for key,value in parameter.items():
                                    if key=='PingStatus':
                                        ping_status=value    
                            LOGGER.info(start_time) 
                            LOGGER.info(self.end_time) 
                            delta=self.end_time.replace(tzinfo=None)-start_time.replace(tzinfo=None)
                            creation_span=delta.total_seconds()/3600
                            #check for ping status and time lapsed since creation
                            if ping_status!='Online' and int(creation_span)>=6 and elements['State']['Name']!='stopped':
                                region_details_dict[elements['InstanceId']]=region      
            if len(region_details_dict)>0:
                self.send_ssm_emails(region_details_dict,custodian)
        except Exception as exception:
            LOGGER.error("Lambda failed with the error:'{0}'".format(exception))
            return "FAILED"
            
    def send_ssm_emails(self,region_list,custodian):
        """method: sends reconciliation emails to team and custodian
        param: image name list
        param: instance id list 
        param: region list 
        param: account custodian name 
        param: account number"""
        mail_body=""      
        DNSSESKeyEmail = self.ssm_client.get_parameter(Name='/platform-dns/DNSSESKeyEmail')
        DNSSESKeyEmail = DNSSESKeyEmail['Parameter']['Value']
        DNSSESSecrtEmail = self.ssm_client.get_parameter(Name='/platform-dns/DNSSESSecrtEmail')
        DNSSESSecrtEmail = DNSSESSecrtEmail['Parameter']['Value']
        platform_dl = self.ssm_client.get_parameter(Name='/Platform-Tag/platform_DL')
        platform_dl_response = platform_dl['Parameter']['Value']
        session_client = boto3.session.Session()
        try:
            ses_client = session_client.client('ses', region_name='us-east-1', aws_access_key_id=DNSSESKeyEmail, aws_secret_access_key=DNSSESSecrtEmail)
        except Exception as exception:
            print(exception)
        serial_number=1
        html=""
        for (instance_id,region_value) in region_list.items():
            html+="""<tr>
                    <td width="20%">"""+str(serial_number)+"""</td>
                    <td width="40%">"""+instance_id+"""</td>
                    <td width="40%">""" +region_value+ """</td>
                    </tr>"""
            serial_number+=1
            mail_body=mail_body+"""\nRegion:"""+region_value+""" """+"""\nInstance ID:"""+instance_id
        mail_body="""Hello Team,
            We could identify the below ec2 instances as SSM non-compliant(SSM not installed/not working). Please take the necessary measures to make the instances SSM compliant. 
            *Account Number:""" +self.account_number+""" """+mail_body+"""\nRegards,\nCloud Services Team"""
        mail_subject= "SSM Agent Compliance Reconciliation for Account Number: "+self.account_number
        body_html = """<html>
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
                <p style="font-family:'Futura Medium'">Hello Team,</p>
                <p style="font-family:'Futura Medium'"> We could identify the below ec2 instances as SSM non-compliant(SSM not installed/not working). Please take the necessary measures to make the instances SSM compliant.</p>
                
                <table style="width:100%">
                    <col style="width:20%">
                    <col style="width:40%">
                    <col style="width:40%">
                    <tr bgcolor="yellow">
                    <td width="20%">Serial Number</td>
                    <td width="40%">Instance Id</td>
                    <td width="40%">Region</td>
                    </tr>"""+html+"""
                </table>
                <p style="font-family:'Futura Medium'">Refer the below link to install SSM agent on the respective OS versions if it is not installed/running:<p>
                <p style="font-family:'Futura Medium'">For Linux:</p>
                <href>https://docs.aws.amazon.com/systems-manager/latest/userguide/sysman-manual-agent-install.html</href>
                <p style="font-family:'Futura Medium'">For Windows:</p>
                <href>https://docs.aws.amazon.com/systems-manager/latest/userguide/sysman-install-win.html</href>
                <p style="font-family:'Futura Medium'">Best Regards,</p>
                <p style="font-family:'Futura Medium'">AWS@Shell Team</p>
                </body>
                </html>
                """
        try:
            LOGGER.info("Inside custom Send Mail")
            char_set = "utf-8"
            LOGGER.info("Hello\r\nWe could see the below instances are not having SSM agent installed and this would make the instances SSM non-compliant in our platform. Request you to install the SSM agent ASAP and  update us. \r\nAccount Number:" +self.account_number+mail_body+"\r\nRegards,\r\nCloud Services Team")
            response = ses_client.send_email(
                Destination={
                    "ToAddresses": [
                            "GX-IDSO-ETSOM-DP-CLOUD-AWS-DEVOPS@shell.com",platform_dl_response,custodian,
                            ],
                        },
                Message={
                        "Subject": {
                            "Data": mail_subject,
                                    },
                        "Body": {
                            "Text": {
                                "Data": mail_body,
                            },
                            "Html":{
                                "Data":body_html
                            }
                                },
                               },
                Source="SITI-CLOUD-SERVICES@shell.com",
                        )
            LOGGER.info("Email sent!")
        except Exception as exception:
            LOGGER.error("Lambda failed with the error:'{0}'".format(exception))
            return "FAILED" 
            
def lambda_handler(event, context):
    """method: Main lambda handler takes event as dictionary and context as an object
        param: event
        param: context"""
    create_mail_obj=mail_automation(event,context)
    try:
        LOGGER.info("Calling compliance check function")
        status = create_mail_obj.child_account_instances_compliant()
    except Exception as exception:
        print("Exception in Lambda Handler", exception)