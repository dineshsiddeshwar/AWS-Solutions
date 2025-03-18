"""
    This module uses AWS cost explorer APIs to get the list of resoruces launched
    Create a report and shares with Business for necessary actions
"""
import os

import random
import csv

import datetime
from datetime import timedelta

from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

from dateutil.relativedelta import relativedelta

import boto3

import logging

from botocore.exceptions import ClientError

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
LOGGER.addHandler(CH)

RESULT_LIST = {}


class ChargeableResourceInventory(object):
    """ Initialze all the variables from event """

    def __init__(self, event, context):
        self.event = event
        self.context = context
        LOGGER.info("Event: %s" % self.event)
        LOGGER.info("Context: %s" % self.context)
        try:
            # Create a new STS resource
            session_client = boto3.Session()
            self.ssm_client = session_client.client('ssm')
            sender_id_response = self.ssm_client.get_parameter(Name="sender_id")
            self.sender_id = sender_id_response['Parameter']['Value']
            failure_id_response = self.ssm_client.get_parameter(Name="failure_operation_dl")
            self.failure_operation_dl = failure_id_response['Parameter']['Value']
            success_id_response = self.ssm_client.get_parameter(Name="success_operation_dl")
            self.success_operation_dl = success_id_response['Parameter']['Value']
            resource_properties = event['ResourceProperties']
            self.requestor_email = resource_properties['RequestorEmail']
            self.sts_client = session_client.client('sts')
            # Create a new SES resource and specify a region.
            self.ses_client = boto3.client('ses')
            # get relevant input params from event
            self.account_number = event['accountNumber']
            self.custodian_user = event['ResourceProperties']['CustodianUser']
            self.dl_for_new_account = event['dlForNewAccount']
            self.shell_extension = "@shell.com"
        except Exception as exception:
            RESULT_LIST['ChargeableResourceInventory'] = "FAILED"
            self.reason_data = "Missing required property %s" % exception
            LOGGER.error(self.reason_data)
            return

    def get_cost_usage(self):
        """
            This function is used to get the list of chargeable resources for a months time

             Returns:
                    list:The return value - Decommission date when success, error message otherwise.
        """
        try:
            child_account_role_arn = 'arn:aws:iam::' + str(self.account_number) + ":role/AWSControlTowerExecution"
            child_accountsessionsame = "ChildAccountSession-" + str(random.randint(1, 100000))
            child_accountrolecreds = self.sts_client.assume_role(
                RoleArn=child_account_role_arn, RoleSessionName=child_accountsessionsame)
            child_credentials = child_accountrolecreds.get('Credentials')
            child_accesskey = child_credentials.get('AccessKeyId')
            child_secret_accesskey = child_credentials.get('SecretAccessKey')
            child_sessiontoken = child_credentials.get('SessionToken')
            child_assumeroleression = boto3.Session(child_accesskey, child_secret_accesskey,
                                                    child_sessiontoken)
            ce_client = child_assumeroleression.client('ce', region_name="us-east-1")

            # Get the date on which the Lambda is executed and 1 month ago date to fetch the report
            today_date = datetime.datetime.now()
            end_time = today_date.strftime('%Y-%m-%d')
            one_m_ago = today_date - relativedelta(months=1)
            start_time = one_m_ago.strftime('%Y-%m-%d')
            # Save the report at temporary location in Lambda and mail the report once generated
            with open('/tmp/CostUsage.csv', 'w+', newline='') as csvfile:
                filewriter = csv.writer(csvfile, delimiter=",", quoting=csv.QUOTE_MINIMAL)
                filewriter.writerow(['Region', 'Services', 'BlendedCost', 'UnblendedCost',
                                     'UsageQuantity'])
                response = ce_client.get_cost_and_usage(
                    TimePeriod={
                        'Start': start_time,
                        'End': end_time
                    },
                    Granularity='DAILY',
                    Metrics=['BlendedCost', 'UnblendedCost', 'UsageQuantity'],
                    GroupBy=[
                        {
                            'Type': 'DIMENSION',
                            'Key': 'SERVICE'
                        },
                        {
                            'Type': 'DIMENSION',
                            'Key': 'REGION'
                        }
                    ]
                )

                result_response = response.get('ResultsByTime')
                next_page_token = response.get('NextPageToken')
                print(next_page_token)
                for result_by_time in result_response:
                    cost_details_list = result_by_time['Groups']
                    # print("cost_details_list",cost_details_list)
                    if cost_details_list:
                        for cost_detail in cost_details_list:
                            service_details = str(cost_detail['Keys'][0])
                            print("service", service_details)
                            region_of_resource = str(cost_detail['Keys'][1])
                            print("region", region_of_resource)
                            metrics_details = cost_detail.get('Metrics')
                            blended_cost = metrics_details.get("BlendedCost", {}).get('Amount')
                            unblended_cost = metrics_details.get("UnblendedCost", {}).get('Amount')
                            usage_quantity = metrics_details.get('UsageQuantity', {}).get('Amount')

                            filewriter.writerow([region_of_resource, service_details, blended_cost,
                                                 unblended_cost, usage_quantity])
            decomission_start_date = datetime.datetime.now() + timedelta(days=1)
            decomission_start_date = str(decomission_start_date)
            d = decomission_start_date.split(' ')[0]
            t = ((decomission_start_date.split(' '))[1].split(' '))[0].split('.')[0]
            decomission_start_date_formatted = d + 'T' + t + 'Z'
            RESULT_LIST.update({'decomissionstartdate': str(decomission_start_date_formatted)})
            RESULT_LIST.update({'get_cost_usage': "PASSED"})
            self.send_mail()
        except Exception as exception:
            LOGGER.error(exception)
            RESULT_LIST['emailParameter'].append('decomFailure')

    def send_mail(self):
        """
            This function is used to send mail to Business with an attachment report for the list
            of chargeable resources

                Returns:
                    Nothing
        """
        try:
            receiver_name = self.requestor_email.replace(self.shell_extension, "").replace(".", " ").title()
            LOGGER.info("Inside send mail")
            # create raw email
            # Replace sender@example.com with your "From" address.
            # This address must be verified with Amazon SES.
            sender_id = self.sender_id

            # Remove -B to get valid mail ID
            # Replace recipient@example.com with a "To" address.
            to_recipient = str(self.custodian_user)
            cc_recipient = str(self.dl_for_new_account)

            # The subject line for the email.
            mail_subject = "Action Required: AWS@Shell Account Decommission - Resource(s) clean up required"


            # The full path to the file that will be attached to the email.
            attachment_template = "/tmp/CostUsage.csv"

            # The email body for recipients with non-HTML email clients.
            body_text = """Important Action Required\nAWS@Shell – Resource(s) clean up required\nWhat’s happening?\nYou are receiving this notification because you have requested decommissioning of your AWS@Shell account """\
                        +self.event['subscription_name']+""" and we need your action.\nThe attached billing report contains the list of rechargeable marketplace"""\
                        +""" resources and AWS resources that might still be running in your account.\nWhat is expected from you?\nPlease delete the resources. """\
                        +"""You can use the AWS Resource Group feature to check whether the resources are still running in across regions within your account. """\
                        +"""The resources will not be accessible post account termination within next 24 hours.\n Any pending payment(s) due to """\
                        +"""savings plan purchases, would continue to be charged even after account closure. Please refer to the Savings Plan QRG for more information."""\
                        +"""\n<b>Note:</b> If you are getting Access Denied error while trying to delete resources, please ignore the error as the resource """\
                        +"""may belong to the AWS@Shell platform managed resources.\nIf you have any questions or comments regarding this email, then please contact us at """\
                        +self.sender_id+""".\nBest Regards,\nCloud Services Team\nAWS at Shell Yammer, AWS User Voice Portal and Service Now"""

            # The HTML body of the email.
            body_html = """
                    <html>
                    <head></head>
                    <body>
                    <p style="color:red;font-family:'Futura Medium'"><b>Important: Action Required</b></p>
                    <p style="color:#1F497D;font-family:'Futura Medium'"><b>AWS@Shell – Resource(s) clean up required</b></p>
                    <p style="color:red;font-family:'Futura Medium'">What’s happening?</p>
                    <p style="font-family:'Futura Medium'">You are receiving this notification because you have requested decommissioning of your AWS@Shell account """+self.event['subscription_name']+""" and we need your action.</p> 
                    <p style="font-family:'Futura Medium'">The attached billing report contains the list of rechargeable marketplace resources and AWS resources that might still be running in your account.</p> 
                    <p style="color:red;font-family:'Futura Medium'">What is expected from you?</p>
                    <p style="font-family:'Futura Medium'">Please delete the resources. You can use the AWS Resource Group feature to check whether the resources are still running in across regions within your account. The resources will not be accessible post account termination within next 24 hours.</p>
                    <p style="font-family:'Futura Medium'">Any pending payment(s) due to savings plan purchases, would continue to be charged even after account closure. Please refer to the following QRG for more information <a href=https://eu001-sp.shell.com/:w:/r/sites/AAFAA5187/L3/IB-Cloud%20CoE/AWS%20DA%202.0/QRGs/QRG_Savings%20Plan.docx?d=w351942acd05b4e919dafb49b353dcacf&csf=1&web=1&e=r3LMqa >Savings Plan QRG</a>.</p>
                    <p style="font-family:'Futura Medium'"><b>Note:</b> If you are getting Access Denied error while trying to delete resources, please ignore the error as the resource may belong to the AWS@Shell platform managed resources.</p>
                    <p style="font-family:'Futura Medium'">If you have any questions or comments regarding this email, then please contact us at """+self.sender_id+""".</p>
                    <p style="font-family:'Futura Medium'">Best Regards,</p>
                    <p style="font-family:'Futura Medium'">Cloud Services Team</p>
                    <p style="font-family:'Futura Medium'"><a href=https://www.yammer.com/shell.com/#/threads/inGroup?type=in_group&feedId=13574864&view=all>AWS at Shell Yammer</a>, <a href=https://ideas.cloud.shell.com//>AWS User Voice Portal</a> and <a href=https://shell.service-now.com/sp?id=sc_cat_item_guide&sys_id=2a8fa788db605f40f16ef1951d96199b>Service Now</a>.</p>
                    
                    </body>
                    </html>
                    """

            # The character encoding for the email.
            char_set = "utf-8"

            # Create a multipart/mixed parent container.
            msg = MIMEMultipart('mixed')
            # Add subject, from and to lines.
            msg['Subject'] = mail_subject
            msg['From'] = sender_id
            msg['To'] = str(to_recipient)
            msg['CC'] = str(cc_recipient)

            # Create a multipart/alternative child container.
            msg_body = MIMEMultipart('alternative')

            # Encode the text and HTML content and set the character encoding. This step is
            # necessary if you're sending a message with characters outside the ASCII range.
            textpart = MIMEText(body_text.encode(char_set), 'plain', char_set)
            htmlpart = MIMEText(body_html.encode(char_set), 'html', char_set)

            # Add the text and HTML parts to the child container.
            msg_body.attach(textpart)
            msg_body.attach(htmlpart)

            # Define the attachment part and encode it using MIMEApplication.
            att = MIMEApplication(open(attachment_template, 'rb').read())

            # Add a header to tell the email client to treat this part as an attachment,
            # and to give the attachment a name.
            att.add_header('Content-Disposition', 'attachment',
                           filename=os.path.basename(attachment_template))

            # Attach the multipart/alternative child container to the multipart/mixed
            # parent container.
            msg.attach(msg_body)

            # Add the attachment to the parent container.
            msg.attach(att)
            try:
                # Provide the contents of the email.
                response = self.ses_client.send_raw_email(
                    Source=sender_id,
                    Destinations=[
                        to_recipient, cc_recipient
                    ],
                    RawMessage={
                        'Data': msg.as_string(),
                    }
                )

            # Display an error if something goes wrong.
            except ClientError as client_error:
                LOGGER.error(client_error.response['Error']['Message'])
            else:
                LOGGER.info("Email sent! Message ID:", )
                LOGGER.info(response['ResponseMetadata']['RequestId'])
                RESULT_LIST.update({'send_mail': "PASSED"})
        except Exception as exception:
            LOGGER.error(exception)


def lambda_handler(event, context):
    """
        lambda_handler is used to get the event from the Step Functions execution.
        This is the starting point of execution for this module.
    """
    try:
        LOGGER.info(event)
        RESULT_LIST.update(event)
        inventory_result = ChargeableResourceInventory(event, context)
        inventory_result.get_cost_usage()
        LOGGER.info(RESULT_LIST)
        RESULT_LIST['ChargeableResourceInventory'] = "PASSED"
        RESULT_LIST['count'] = 1
        print(RESULT_LIST['count'])
        return RESULT_LIST
    except Exception as exception:
        LOGGER.error(str(exception))
