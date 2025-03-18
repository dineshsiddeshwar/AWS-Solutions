"""
This module is used to templatize mail to all stakeholders based on different actions
performed for account management activities
"""
import json
import logging
import boto3

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
LOGGER.addHandler(CH)
counter = 0



class SendDecomMail(object):
    """
        This class is used to send mails based on templates created in Automation account
        This class uses already created templates and will not create new template
        To create new template use CreateTemplate Lambda and for any updates use UpdateTemplate
        Lambda
    """

    def __init__(self, event, context):
        self.event = event
        self.context = context
        LOGGER.info("Event: %s" % self.event)
        LOGGER.info("Context: %s" % self.context)
        try:
            if type(event) == list:
                email_parameter = []
                for event_type in event:
                    if type(event_type) == dict and "emailParameter" in event_type.keys():
                        print('eve emailParameters >' + str(event_type['emailParameter']))
                        email_parameter.extend(event_type['emailParameter'])
                        new_event = event_type
                print(type(event_type))
                event = new_event

            counter = event['count']
            print("Count:", counter)
            resource_properties = event['ResourceProperties']
            self.request_number = event['ResourceProperties']['RequestNo']
            self.dl_for_new_account = event['dlForNewAccount']
            session_client = boto3.Session()
            self.ssm_client = session_client.client('ssm')
            self.sender_id = event['SSMParametres']['sender_id']
            self.failure_operation_dl = event['SSMParametres']['failure_operation_dl']
            self.success_operation_dl = event['SSMParametres']['success_operation_dl']
            self.account_name = resource_properties['AccountName']
            self.budget_value = resource_properties['Budget']
            self.requestor_email = resource_properties['RequestorEmail']
            self.custodian_user = resource_properties['CustodianUser']
            self.subscription_name = event['subscription_name']
            self.email_parameter = event['emailParameter']
            if 'dlForNewAccount' in event.keys():
                self.dl_for_new_account = event['dlForNewAccount']
            if 'accountNumber' in event.keys():
                self.account_number = event['accountNumber']
            self.account_name = resource_properties['AccountName']
            self.budget_value = resource_properties['Budget']
            # From Yml Config File
            self.admin_users = resource_properties['SupportDL']
        except Exception as exception:
            self.reason_data = "Missing required property %s" % exception
            print("Exception in __init__()", exception)
            LOGGER.error(self.reason_data)
            raise exception

    def send_email_to_users(self):
        """
        This function to send mail based on the result send by Step Function stages
        Already created Template is used to send mails
        :return:
        """
        print('EmailParameters >' + str(self.email_parameter))
        receiver_name = ''
        ses_client = boto3.client('ses')
        try:

            if "decomSuccess" in self.email_parameter:
                receiver_name = self.requestor_email.replace("@shell.com", "").replace(".", " ").title()

                # This address must be verified with Amazon SES.
                sender_id = self.sender_id

                # The email body for recipients with non-HTML email clients.
                body_text = """Dear """ + receiver_name + """,\r\nAs requested, your AWS@Shell account """ + self.subscription_name + """  
                is closed and AWS resources under this account will no longer be accessible. \r\nIf you have any questions or comments regarding this email, then please contact us at"""\
                            +self.sender_id+ """\r\nBest Regards,\r\nCloud Services Team \r\nAWS at Shell Yammer, AWS User Voice Portal and Service Now
                    """

                # The HTML body of the email.
                body_html = """<p style="font-family:'Futura Medium'">Dear """ + receiver_name + """, </p>
                    <p style="font-family:'Futura Medium'">As requested, your AWS@Shell account """ + self.subscription_name + """ is closed and AWS resources under this account will no longer be accessible.</p>
                    <P></p>
                    <p style="font-family:'Futura Medium'">If you have any questions or comments regarding this email, then please contact us at """+self.sender_id+""".</p>
                    <p style="font-family:'Futura Medium'">Best Regards,</p>
                    <p style="font-family:'Futura Medium'">Cloud Services Team</p>
                    <p style="font-family:'Futura Medium'"><a href=https://www.yammer.com/shell.com/#/threads/inGroup?type=in_group&feedId=13574864&view=all>AWS at Shell Yammer</a>, <a href=https://ideas.cloud.shell.com//>AWS User Voice Portal</a> and <a href=https://shell.service-now.com/sp?id=sc_cat_item_guide&sys_id=2a8fa788db605f40f16ef1951d96199b>Service Now</a>.</p>
                """

                # Provide the contents of the email.

                send_mail_response = ses_client.send_email(
                    Source=sender_id,
                    Destination={
                        'ToAddresses': [self.dl_for_new_account],
                        'CcAddresses': [self.custodian_user]
                    },
                    Message={
                        'Subject': {
                            'Data': "Your AWS@Shell account is decommissioned"
                        },
                        'Body': {
                            'Text': {
                                'Data': body_text

                            },
                            'Html': {
                                'Data': body_html

                            }
                        }
                    }
                )
                print("Response", send_mail_response)
            if "AccountDecomCleanupMail" in self.email_parameter:
                # Send mail to operations team for account closure

                print("NAME>>>>>>>>", self.success_operation_dl)

                # This address must be verified with Amazon SES.
                sender_id = self.sender_id

                # The email body for recipients with non-HTML email clients.
                body_text = """
                    Important Action Required\nAWS@Shell - Account closure.\nWhat’s happening?\nYou are receiving this notification because the following AWS@Shell account """+ \
                            self.subscription_name+ """ is ready for decommissioning.\nBelow are the account details:\n * Subscription Name:""" + self.subscription_name \
                            + """\n* Account Number :""" + self.account_number + """\n* Account Name : """ + self.account_name + """\n* Custodian Admin : """ + self.custodian_user +"""
                            \nWhat is expected from you?\nPlease delete all VPC associations and proceed with manual closure of the AWS@Shell account """+self.subscription_name+""".\nBest Regards,\nCloud Services Team"""

                # The HTML body of the email.
                body_html = """<html>
                    <head></head>
                    <body>
                    <p style="color:red;font-family:'Futura Medium'"><b>Important: Action Required</b></p>
                    <p style="color:#1F497D;font-family:'Futura Medium'"><b>AWS@Shell - Account closure.</b></p>
                    <p style="color:red;font-family:'Futura Medium'">What’s happening?</p>
                    <p style="font-family:'Futura Medium'">You are receiving this notification because the following 
                    AWS@Shell account """+ self.subscription_name+ """ is ready for decommissioning.</p> 
                    <p style="font-family:'Futura Medium'">Below are the account details:</p>
                    <ul>
                    <li style="font-family:'Futura Medium'">Subscription Name : """ + self.subscription_name + """</li>
                    <li style="font-family:'Futura Medium'">Account Number : """ + self.account_number + """</li>
                    <li style="font-family:'Futura Medium'">Account Name : """ + self.account_name + """</li>
                    <li style="font-family:'Futura Medium'">Custodian Admin : """ + self.custodian_user + """</li>
                    </ul>
                    <p style="color:red;font-family:'Futura Medium'">What is expected from you?</p>
                    <p style="font-family:'Futura Medium'">Please delete all VPC associations and proceed with manual closure of the AWS@Shell account """+self.subscription_name+""".</p>
                    <p style="font-family:'Futura Medium'">Best Regards,</p>
                    <p style="font-family:'Futura Medium'">Cloud Services Team</p>
                    </body>
                    </html>
                    """
                # Provide the contents of the email.

                send_mail_response = ses_client.send_email(
                    Source=sender_id,
                    Destination={
                        'ToAddresses': [self.success_operation_dl]
                    },
                    Message={
                        'Subject': {
                            'Data': "Action Required: AWS@Shell account closure"

                        },
                        'Body': {
                            'Text': {
                                'Data': body_text

                            },
                            'Html': {
                                'Data': body_html

                            }
                        }
                    }
                )
                print(send_mail_response)
            if "decomFailure" in self.email_parameter:
                # Send mail to operations team for account decom failure

                print("NAME>>>>>>>>", self.success_operation_dl)

                # This address must be verified with Amazon SES.
                sender_id = self.sender_id

                # The email body for recipients with non-HTML email clients.
                body_text = """Important Action Required\nAWS@Shell - Account decommissioning failure.\nWhat’s happening?\nYou are receiving this """+"""notification because the following AWS@Shell account """+ \
                            self.subscription_name+ """ has failed to decommission.\nBelow are the account details:Subscription Name : """ + \
                            self.subscription_name + """Account Number : """ + self.account_number + """\nAccount Name : """ + \
                            self.account_name + """Custodian Admin : """ + self.custodian_user + """\nPlease check the AWS Step Function’s (platform_AVMStatemachine) state machine """\
                            +"""flow diagram and CloudWatch logs for additional details.\nPlease investigate and take appropriate action.\nBest Regards,\nCloud Services Team """

                # The HTML body of the email.
                body_html = """<html>
                    <head></head>
                    <body>
                    <p style="color:red;font-family:'Futura Medium'"><b>Important: Action Required</b></p>
                    <p style="color:#1F497D;font-family:'Futura Medium'"><b>AWS@Shell - Account decommissioning failure.</b></p>
                    <p style="color:red;font-family:'Futura Medium'">What’s happening?</p>
                    <p style="font-family:'Futura Medium'">You are receiving this notification because the following 
                    AWS@Shell account """+ self.subscription_name+ """ has failed to decommission.</p> 
                    <p style="font-family:'Futura Medium'">Below are the account details:</p>
                    <ul>
                    <li style="font-family:'Futura Medium'">Subscription Name : """ + self.subscription_name + """</li>
                    <li style="font-family:'Futura Medium'">Account Number : """ + self.account_number + """</li>
                    <li style="font-family:'Futura Medium'">Account Name : """ + self.account_name + """</li>
                    <li style="font-family:'Futura Medium'">Custodian Admin : """ + self.custodian_user + """</li>
                    </ul>
                    <p style="color:red;font-family:'Futura Medium'">What is expected from you?</p>
                    <p style="font-family:'Futura Medium'">Please check the AWS Step Function’s (platform_AVMStatemachine) state machine flow diagram and CloudWatch logs for additional details.</p>
                    <p style="font-family:'Futura Medium'">Please investigate and take appropriate action.</p>
                    <p style="font-family:'Futura Medium'">Best Regards,</p>
                    <p style="font-family:'Futura Medium'">Cloud Services Team</p>
                    </body>
                    </html>
                """
                # Provide the contents of the email.

                send_mail_response = ses_client.send_email(
                    Source=sender_id,
                    Destination={
                        'ToAddresses': [self.success_operation_dl]
                    },
                    Message={
                        'Subject': {
                            'Data': "Action Required: Failed AWS@Shell account decommissioning notification"
                        },
                        'Body': {
                            'Text': {
                                'Data': body_text

                            },
                            'Html': {
                                'Data': body_html

                            }
                        }
                    }
                )
                print(send_mail_response)
            return send_mail_response

        except Exception as exception:
            print(str(exception))
            return exception


def lambda_handler(event, context):
    """
            This is the entry point of the module
            :param event:
            :param context:
            :return:
    """
    try:
        result_values = {}
        result_values.update(event)
        send_mail_object = SendDecomMail(event, context)
        response_output = send_mail_object.send_email_to_users()
        if isinstance(response_output, Exception):
            print("Error while sending Email, Refer Cloudwatch Logs")
            return response_output
        print("send_templated_email_to_users response", response_output)
        return result_values
    except Exception as exception:
        print("Send Mail Error >>" + str(exception))
        return exception

