"""
This module is used to templatize mail to all stakeholders based on different actions
performed for account management activities
"""
import json
import logging
import boto3
import ast

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
LOGGER.addHandler(CH)


class SendTemplatedMail(object):
    """
        This class is used to send mails based on templates created in Automation account
        This class uses already created templates and will not create new template
        To create new template use CreateTemplate Lambda and for any updates use UpdateTemplate
        Lambda
    """

    def __init__(self, event, context):
        self.event = {}
        self.context = context
        LOGGER.info("Event: %s" % self.event)
        LOGGER.info("Context: %s" % self.context)
        try:
            """Parallel step function input is converted to single input."""
            if type(event) == list:
                temp_event = {}
                for every_dict in event:
                    temp_event.update(every_dict)
                self.event = temp_event
                print(" Converted list of dict to a single dict",self.event)
                email_parameter = []
                for event_type in event:
                    if type(event_type) == dict and "emailParameter" in event_type.keys():
                        print('eve emailParameters >' + str(event_type['emailParameter']))
                        email_parameter.extend(event_type['emailParameter'])
                        new_event = event_type
                event = new_event
            else:
                self.event = event
                print("Received a single event intput from the stepfunction", self.event)

            self.request_number = event['ResourceProperties']['RequestNo']
            self.request_type = event['RequestType']
            print(f"printing request type {self.request_type}")
            session_client = boto3.Session()
            self.ssm_client = session_client.client('ssm')
            sender_id_response = self.ssm_client.get_parameter(Name="sender_id")
            self.sender_id = sender_id_response['Parameter']['Value']
            failure_id_response = self.ssm_client.get_parameter(Name="failure_operation_dl")
            self.failure_operation_dl = failure_id_response['Parameter']['Value']
            success_id_response = self.ssm_client.get_parameter(Name="success_operation_dl")
            self.success_operation_dl = success_id_response['Parameter']['Value']
            acnts_table_response = self.ssm_client.get_parameter(Name="accountDetailTableName")
            self.acnts_table_name = acnts_table_response['Parameter']['Value']

            resource_properties = event['ResourceProperties']
            self.account_name = resource_properties['AccountName']
            self.budget_value = resource_properties['Budget']
            self.requestor_email = resource_properties['RequestorEmail']
            self.custodian_user = resource_properties['CustodianUser']
            self.subscription_name = event['subscription_name']
            self.email_parameter = event['emailParameter']
            if 'default_vpc_deletion_status' in event.keys():
                self.default_vpc_delete_status = event['default_vpc_deletion_status']
            else:
                self.default_vpc_delete_status = ""
            if 'dlForNewAccount' in event.keys():
                self.dl_for_new_account = event['dlForNewAccount']
            if 'accountNumber' in event.keys():
                self.account_number = event['accountNumber']
            self.account_name = resource_properties['AccountName']
            self.budget_value = resource_properties['Budget']
            # From Yml Config File
            self.admin_users = resource_properties['SupportDL']
            self.ses_client = boto3.client('ses')
            self.shell_extension = "@shell.com"
        except Exception as exception:
            self.reason_data = "Missing required property %s" % exception
            print("Exception in __init__()", exception)
            LOGGER.error(self.reason_data)
            raise exception

    """Get VPC IP Details and VPC Status"""

    def vpc_ip_details(self):
        try:
            session_client = boto3.Session()
            self.dd_client = session_client.client('dynamodb', region_name="us-east-1")
            get_response = self.dd_client.get_item(
                TableName=self.acnts_table_name,
                Key={
                    'AccountNumber': {"S": self.account_number}
                }
            )
            print("VPC Details", get_response)
            get_response_keys = get_response.keys()
            HTML_CIDR = ""

            """Put VPC Details/CIDR Range in HTML Table"""
            if "Item" in get_response_keys:
                get_item_response_keys = get_response['Item'].keys()
                if "CIDR" in get_item_response_keys and len(get_response['Item']['CIDR']['L']) > 0:
                    for ip_address in get_response['Item']['CIDR']['L']:
                        ip_address = ip_address['S']
                        ip_address = ast.literal_eval(str(ip_address))
                        HTML_CIDR = HTML_CIDR + """<tr>
                        <td width="50%">VPC Range - """ + ip_address['region'] + """</td>
                        <td width="50%">""" + ip_address['cidr'] + """</td>
                      </tr>"""
            return True, HTML_CIDR
        except Exception as e:
            print(str(e))
            return False, ""

    """Send Budget is changed email to the business user."""

    def send_budget_email(self):
        try:
            """Verify the email formath is correct"""
            receiver_name = self.requestor_email.replace(self.shell_extension, "").replace(".", " ").title()
            print("NAME>>>>>>>>", receiver_name, self.requestor_email,
                  self.dl_for_new_account, self.sender_id)

            # This address must be verified with Amazon SES.
            sender_id = self.sender_id

            """HTML Email body"""
            body_html = """
                        <p style="font-family:'Futura Medium'">Dear """ + receiver_name + """,</p>

                        <p style="font-family:'Futura Medium'">As requested, your monthly budget limit is set to <b>$""" + self.budget_value + """</b> for <b>""" + self.subscription_name + """</b>.</p>
                        <p style="font-family:'Futura Medium'">If you have any questions or comments regarding this email, then please contact us at """+self.sender_id+""".</p>
                        <p style="font-family:'Futura Medium'">Best Regards,<br>
                        Cloud Services Team</p>
                        <p style="font-family:'Futura Medium'"><a href=https://www.yammer.com/shell.com/#/threads/inGroup?type=in_group&feedId=13574864&view=all>AWS at Shell Yammer</a>, <a href=https://ideas.cloud.shell.com//>AWS User Voice Portal</a> and <a href=https://shell.service-now.com/sp?id=sc_cat_item_guide&sys_id=2a8fa788db605f40f16ef1951d96199b>Service Now</a>.</p>
                        """

            """Text Email body for NON-HTML Email providers"""
            body_text = """Dear """ + receiver_name + """,\nAs requested, your monthly budget limit is set to $""" \
                        + self.budget_value + """ for """ + self.subscription_name + """.\nIf you have any questions or comments regarding this email, then please contact us at """\
                        +self.sender_id+""".\nBest Regards,\nCloud Services Team\nAWS at Shell Yammer,  AWS User Voice Portal and Service Now.
                """

            """ send budget SES Email API Call"""
            send_mail_response = self.ses_client.send_email(
                Source=sender_id,
                Destination={
                    'ToAddresses': [self.dl_for_new_account],
                    'CcAddresses': [self.custodian_user]
                },
                Message={
                    'Subject': {
                        'Data': self.request_number+': AWS@Shell Monthly Budget Alert'

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
        except Exception as e:
            print(str(e))
            return str(e)

    """After account is created/updated email is send to the opration's team with the status of all the
    features created in the AVM"""

    def send_success_email_to_operation(self):
        try:
            body_msg = ""
            subject = ""
            vpc_status, vpc_row = self.vpc_ip_details()
            # print (vpc_status, vpc_row)
            feature_table = self.get_features_status()

            receiver_name = self.requestor_email.replace(self.shell_extension, "").replace(".", " ").title()
            # This address must be verified with Amazon SES.
            sender_id = self.sender_id

            if self.request_type == 'Create':
                body_msg =   "A New AWS@Shell account is ready now. "
                subject = self.request_number + " New AWS@Shell account creation successful"
            elif self.request_type == 'Update':
                body_msg = "Below AWS Account has been updated now."
                subject = self.request_number + " AWS@Shell account updation " + self.account_number + " successful"

            # The email body for recipients with non-HTML email clients.
            body_text = """
                Hello Team,

                """ + body_msg + """ Below are the account details:

                    * Subscription Name : """ + self.subscription_name + """
                    * Account Number : """ + self.account_number + """
                    * Account Name : """ + self.account_name + """
                    * Custodian Admin : """ + self.custodian_user + """
                    * Budget Limit : """ + self.budget_value + """
                 
                Features installed in the account:
                ------------------------------------------------------------

                    * Platform Roles Status: """ + str(self.role_status()) + """
                    * Budget Status: """ + str(self.budget_status()) + """
                    * Enterprise Support: """ + str(self.enterprise_status()) + """
                    * Tag AMI: """ + str(self.ami_tagging_status()) + """
                    * Domain Join Status: """ + str(self.domain_join_status()) + """
                    * Default VPC Deletion Status: """ + str(self.default_vpc_deletion_status()) + """
                    * Access Analyzer: """ + str(self.access_analyzer_status()) + """
                    * SNS Topic Status: """ + str(self.sns_topic_status()) + """
                    * Block Public Access Status: """ + str(self.public_access_block()) + """
                    * Enable EBS Encryption: """ + str(self.enable_ebs()) + """
                    * Agent Association Status: """ + str(self.all_agent_association_status()) + """

                In case of any feature’s installation fails, please check the Step Function execution and Cloud Watch Logs

                Best Regards,
                Cloud Services Team
                """

            # The HTML body of the email.
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
                    padding-left: 15px;
                    text-align: left;
                    }
                </style>
                </head>
                <body>
                <p style="font-family:'Futura Medium'">Hello Team,</p>
                <p style="font-family:'Futura Medium'">""" + body_msg + """Below are the account details:</p>

                <table style="width:100%">
                    <col style="width:50%">
                    <col style="width:50%">
                  <tr>
                    <td width="50%">Subscription Name</td>
                    <td width="50%">""" + self.subscription_name + """</td>
                  </tr>
                  <tr>
                    <td width="50%">Account Number</td>
                    <td width="50%">""" + self.account_number + """</td>
                  </tr>
                  <tr>
                    <td width="50%">Account Name</td>
                    <td width="50%">""" + self.account_name + """</td>
                  </tr>
                  <tr>
                    <td width="50%">Custodian Admin</td>
                    <td width="50%">""" + self.custodian_user + """</td>
                  </tr>
                  <tr>
                    <td width="50%">Budget Limit</td>
                    <td width="50%">""" + self.budget_value + """</td>
                  </tr>
                  """ + vpc_row + """
                </table>


                <p style="color:#21618C;font-family:'Futura Medium'">Features installed in the account:</h4>
                """ + feature_table + """

                <p style="font-family:'Futura Medium'">In case of any features installation fails,
                Please check the AWS Step Function’s (platform_AVMStatemachine) state machine flow diagram and CloudWatch logs for additional details</p>

                <p style="font-family:'Futura Medium'">Best Regards,</p>
                <p style="font-family:'Futura Medium'">Cloud Services Team</p>
                </body>
                </html>
                """
            # Provide the contents of the email.
            send_mail_response = self.ses_client.send_email(
                Source=sender_id,
                Destination={
                        'ToAddresses': [self.success_operation_dl]

                },
                Message={
                    'Subject': {
                        'Data': subject

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
            print(f"sending mail response----{send_mail_response}")
            return send_mail_response
        except Exception as e:
            print(str(e))
            return str(e)

    """Send Success Email to the business user"""

    def send_success_email_to_business_user(self):
        try:
            receiver_name = self.requestor_email.replace("@shell.com", "").replace(".", " ").title()
            print("NAME>>>>>>>>", receiver_name, self.requestor_email,
                  self.dl_for_new_account, self.sender_id)

            # This address must be verified with Amazon SES.
            sender_id = self.sender_id

            # The email body for recipients with non-HTML email clients.
            body_text = """Dear """ + receiver_name + """,
                            Your AWS account is ready now.Below are your account details:


                • Subscription Name : """ + self.subscription_name + """
                • Account Number : """ + self.account_number + """
                • Account Name : """ + self.account_name + """
                • Custodian Admin : """ + self.custodian_user + """
                • Budget Limit : """ + self.budget_value + """
                            Use Admin role to switch to your new account
                            Use AWS Login URL to login.
                            Regards,
                            Cloud Services Team
                            --
                            Please do not reply directly to this email. If you have any questions or comments regarding this email, please contact us at """ \
                        + self.sender_id + """ or yammer
                """

            # The HTML body of the email.
            body_html = """<h3>Dear """ + receiver_name + """,</h3>
                <p>Your AWS account is ready now.Below are your account details:</p>
                <ul>
                <li>Subscription Name : """ + self.subscription_name + """</li>
                <li>Account Number : """ + self.account_number + """</li>
                <li>Account Name : """ + self.account_name + """</li>
                <li>Custodian Admin : """ + self.custodian_user + """</li>
                <li>Budget Limit : """ + self.budget_value + """</li>
                </ul>
                <p>Use Admin role to switch to your new account</p>
                <p>Use <a href=http://aws.shell.com>AWS Login</a> URL to login.</p>

                <p>Regards,<br>
                Cloud Services Team</p>
                <p></p>
                <p>Please do not reply directly to this email. If you have any questions or comments regarding this
                email, please contact us at """ + self.sender_id + """,  <a href=https://hub.shell.com/>yammer</a>,
                <a href=https://hub.shell.com/>Idea one portal</a>,
                <a href=https://hub.shell.com/>Service Now</a>

                """

            # Provide the contents of the email.

            send_mail_response = self.ses_client.send_email(
                Source=sender_id,
                Destination={
                    'ToAddresses': [self.dl_for_new_account],
                    'CcAddresses': [self.custodian_user]
                },
                Message={
                    'Subject': {
                        'Data': 'Account Creation Success' + self.request_number

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
        except Exception as e:
            print(str(e))
            return str(e)

    """Send Account creation failure email to the operation's team"""

    def send_failure_to_create_account_email(self):
        try:

            # This address must be verified with Amazon SES.
            sender_id = self.sender_id

            # The email body for recipients with non-HTML email clients.
            body_text = """

                HELLO TEAM,

                An error occurred while creating or updating the AWS account """ + self.subscription_name + """>. Please check the Step Functions state machine flow diagram and CloudWatch logs to debug.

                Regards,
                Cloud Services Team
                """

            # The HTML body of the email.
            body_html = """<p style='font-family:futura Medium'>Hello Team,</p>
                <p style='font-family:futura Medium'>An error occurred during creation or updation of an AWS@Shell account  """ + self.subscription_name + """.
                 Please check the AWS Step Function’s (platform_AVMStatemachine) state machine flow diagram and CloudWatch logs for additional details.
                </p>
                <p style='font-family:futura Medium'>Please investigate and take appropriate action.</p>

                <p style='font-family:futura Medium'>Best Regards,</p>
                <p style='font-family:futura Medium'>Cloud Services Team</p>
                """
            # Provide the contents of the email.

            send_mail_response = self.ses_client.send_email(
                Source=sender_id,
                Destination={
                    'ToAddresses': [self.failure_operation_dl]
                },
                Message={
                    'Subject': {
                        'Data': self.request_number+": Failed AWS@Shell account creation/updation notification"

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
        except Exception as e:
            print(str(e))
            return str(e)

    """Not used"""

    def send_creating_account_failure_email(self):
        try:

            # This address must be verified with Amazon SES.
            sender_id = self.sender_id

            # The email body for recipients with non-HTML email clients.
            body_text = """

                HELLO TEAM,

                An error occurred during Creating/Updating the AWS account """ + self.subscription_name + """. Please check the Step Functions state machine flow diagram and CloudWatch logs to debug.

                Regards,
                Cloud Services Team
                """

            # The HTML body of the email.
            body_html = """<h3>Hello Team,</h3>
                <p></p>
                <p>An error occurred during Creating/Updating the AWS account """ + self.subscription_name + """.
                Please check the Step Functions state machine flow diagram and CloudWatch logs to debug.</p>

                <p>Regards,</p>
                <p>Cloud Services Team</p>
                <p>--</p>
                """
            # Provide the contents of the email.

            send_mail_response = self.ses_client.send_email(
                Source=sender_id,
                Destination={
                    'ToAddresses': [self.failure_operation_dl]
                },
                Message={
                    'Subject': {
                        'Data': 'Account creation failed' + self.request_number

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
        except Exception as e:
            print(str(e))
            return str(e)

    """During Account creation/updation the if Service Catalog parameters are not correct this email is sent to the
    operation team"""

    def send_verify_parameter_failure_email(self):
        try:

            # This address must be verified with Amazon SES.
            sender_id = self.sender_id

            # The email body for recipients with non-HTML email clients.
            body_text = """Hello Team\nThe following error occurred during creation or updation of the AWS@Shell account """ \
                        + self.subscription_name + """.\n• Error : """ + self.event["VerifiedParametersError"] + """\nBest Regards,\nCloud Services Team"""

            # The HTML body of the email.
            body_html = body_html = """<html>
                    <body>
                    <p style="font-family:'Futura Medium'">Hello Team,<p>
                    <p></p>
                    <p style="font-family:'Futura Medium'">The following error occurred during creation or updation of the AWS@Shell account """ + self.subscription_name + """.</p>
                    <ul>
                    <li style="font-family:'Futura Medium'">Error: """ + self.event["VerifiedParametersError"] + """</li>
                    </ul>
                    <p style="font-family:'Futura Medium'">Please check the AWS Step Function’s (platform_AVMStatemachine) state machine flow diagram and CloudWatch logs for additional details.</p>
                    <p style="font-family:'Futura Medium'">Best Regards,</p>
                    <p style="font-family:'Futura Medium'">Cloud Services Team</p>
                    </body>
                    </html>
                """
            # Provide the contents of the email.

            send_mail_response = self.ses_client.send_email(
                Source=sender_id,
                Destination={
                    'ToAddresses': [self.failure_operation_dl]
                },
                Message={
                    'Subject': {
                        'Data': self.request_number+': Failed AWS@Shell account creation/updation due to AWS Service Catalog parameter error'

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
        except Exception as e:
            print(str(e))
            return str(e)

    """IF the Account creation DL's are less then 10 this email is sent to the operation's team"""

    def send_fetch_dl_email(self):
        try:
            # This address must be verified with Amazon SES.
            sender_id = self.sender_id

            # The email body for recipients with non-HTML email clients.
            body_text = """Important Action Required\r\n AWS@Shell –  Free DL’s are less than 10.\r\n What’s happening?\r\n You are receiving this notification because the AWS DA2.0 “DL_Details” table has less the 10 available DL’s for Account Creation. \r\nWhat is expected from you?\r\n
Please get the DLs for Dedicated Accounts Project created in the format “GXITSOCloudServices-AWS-Shell-[Sequence Number]” and add the DLs to the “DL_Details” table in Master Account with “AccountID" """ + str(
                self.event["ResourceProperties"]["AWSAccountId"]) +""" for creating new Dedicated Accounts.\r\nBest Regards,\r\n
Cloud Services Team
"""

            # The HTML body of the email.
            body_html = """
             <html>
                                <head></head>
                                <body>
                                <p style="color:red;font-family:'Futura Medium'"><b>Important: Action Required</b></p>
								<p style="color:#1F497D;font-family:'Futura Medium'"><b>AWS@Shell –  Free DL’s are less than 10.</b></p>
								<p style="color:red;font-family:'Futura Medium'">What’s happening?</p>
                                <p style="font-family:'Futura Medium'">You are receiving this notification because the AWS@Shell “DL_Details” has less the 10 available DL’s for Account Creation.</p>
								<p style="color:red;font-family:'Futura Medium'">What is expected from you?</p>
								<p style="font-family:'Futura Medium'">
								   Please get the DLs for AWS@Shell service created in the format “GXITSOCloudServices-AWS-Shell-[Sequence Number]” and add the DLs to the “DL_Details” table in Master Account with “AccountID" """ + str(
                self.event["ResourceProperties"]["AWSAccountId"]) + """ for creating new AWS@Shell Accounts.
								</p>
                                <p style="font-family:'Futura Medium'">Best Regards,</p>
                                <p style="font-family:'Futura Medium'">Cloud Services Team</p>
                                </body>
                                </html>
                             """

            # Provide the contents of the email.
            send_mail_response = self.ses_client.send_email(
                Source=sender_id,
                Destination={
                    'ToAddresses': [self.success_operation_dl]
                },
                Message={
                    'Subject': {
                        'Data': 'Action Required: AWS@Shell Free DL’s are less than 10 '

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
        except Exception as e:
            print(str(e))
            return str(e)

    """During account creation/updation if all the roles are created successfully or not status."""

    def role_status(self):
        try:
            role_status = False
            if self.event['platform_service_cloudhealth_status'] == "True" and self.event[
                'platform_service_inflation_status'] == "True" and self.event[
                'platform_service_instance_status'] == "True" and self.event[
                'platform_service_readonly_status'] == "True" and self.event[
                'platform_service_back_up_status'] == "True":
                role_status = True
            return role_status
        except Exception as e:
            print(str(e))
            return False

    """VPC creation Status"""

    def vpc_creation_status(self):
        try:
            vpc_status = True
            for vpc_regions_status in self.event['vpc_provison_status']['vpc_status']:
                if (vpc_regions_status == False):
                    vpc_status = False
            return vpc_status
        except Exception as e:
            return False

    """Access Analyzer Status"""

    def access_analyzer_status(self):
        try:
            if self.event['Enable Analyzer Child'] == "PASSED":
                return True
            return False
        except Exception as e:
            print(str(e))
            return False

    """Public Access Bloced Status"""

    def public_access_block(self):
        try:
            if self.event['Public Access Block Configuration'] == "PASSED":
                return True
            return False
        except Exception as e:
            print(str(e))
            return False

    """Emable EBS Status"""

    def enable_ebs(self):
        try:
            if self.event['Enable EBS Encryption'] == "PASSED":
                return True
            return False
        except Exception as e:
            print(str(e))
            return False

    """Update S3 Policy Status"""

    # def update_s3_policy(self):
    #     try:
    #         if self.event['update_s3_policy'] == "PASSED":
    #             return True
    #         return False
    #     except Exception as e:
    #         print(str(e))
    #         return False

    # """Patching Window Status"""

    # def patch_window_status(self):
    #     try:
    #         if self.event['CreatedPatchWindow']:
    #             return True
    #         return False
    #     except Exception as e:
    #         print(str(e))
    #         return False

    """Budget Status"""

    def budget_status(self):
        try:
            if self.event['setBudget'] == 'PASSED':
                return True
            return False
        except Exception as e:
            print(str(e))
            return False

    """Enterprise Support Status"""

    def enterprise_status(self):
        try:
            if self.event['enableEnterpriseSupport'] == 'PASSED':
                return True
            return False
        except Exception as e:
            print(str(e))
            return False

    """AMI tagging Status"""

    def ami_tagging_status(self):
        try:
            if self.event['AMITaggingStatus']:
                return True
            return False
        except Exception as e:
            print(str(e))
            return False

    """Default VPC deletion Status"""

    def default_vpc_deletion_status(self):
        try:
            if self.event['default_vpc_deletion_status'] == 'SUCCESS':
                return True
            return False
        except Exception as e:
            print(str(e))
            return False

    """SNS topic Status"""

    def sns_topic_status(self):
        try:
            if self.event['Update SNS Topic'] == 'PASSED':
                return True
            return False
        except Exception as e:
            print(str(e))
            return False

    """Domain Join Status"""

    def domain_join_status(self):
        try:
            if (self.event['ResourceProperties']['AccountType'] == "private"):
                if self.event['create_association_winadjoin'] == "PASSED" and self.event[
                    'create_association_linuxadjoin'] == "PASSED":
                    return True
            else:
                return True
            return False
        except Exception as e:
            print(str(e))
            return False

    """All agents accosiation creation status"""

    def all_agent_association_status(self):
        try:
            if self.event['ResourceProperties']['AccountType'] == "public" and self.event[
                'cloudhealth_association_creation_pub_linux'] == "PASSED" and self.event[
                'cloudhealth_association_creation_pub_win'] == "PASSED" and self.event[
                'Cloudwatch_association_creation'] == "PASSED" and self.event[
                'Cloudwatch_association_creation_config_win'] == "PASSED" and self.event[
                'Cloudwatch_association_creation_config_linux'] == "PASSED" and self.event[
                'falcon_association_creation_pub_linux'] == "PASSED" and self.event[
                'falcon_association_creation_pub_win'] == "PASSED" and self.event[
                'flexera_association_creation_pub_linux'] == "PASSED" and self.event[
                'flexera_association_creation_pub_win'] == "PASSED" and self.event[
                'rapid7_association_creation_pub_linux'] == "PASSED" and self.event[
                'rapid7_association_creation_pub_win'] == "PASSED":
                return True
            elif self.event['ResourceProperties']['AccountType'] == "private" and self.event[
                'cloudhealth_association_creation_priv_linux'] == "PASSED" and self.event[
                'cloudhealth_association_creation_pvt_win'] == "PASSED" and self.event[
                'Cloudwatch_association_creation'] == "PASSED" and self.event[
                'Cloudwatch_association_creation_config_win'] == "PASSED" and self.event[
                'Cloudwatch_association_creation_config_linux'] == "PASSED" and self.event[
                'falcon_association_creation_priv_linux'] == "PASSED" and self.event[
                'falcon_association_creation_pvt_win'] == "PASSED" and self.event[
                'flexera_association_creation_priv_linux'] == "PASSED" and self.event[
                'flexera_association_creation_pvt_win'] == "PASSED" and self.event[
                'rapid7_association_creation_priv_linux'] == "PASSED" and self.event[
                'rapid7_association_creation_pvt_win'] == "PASSED":
                return True
            elif self.event['ResourceProperties']['AccountType'] == "hybrid" and self.event[
                'cloudhealth_association_creation_priv_linux'] == "PASSED" and self.event[
                'cloudhealth_association_creation_pvt_win'] == "PASSED" and self.event[
                'Cloudwatch_association_creation'] == "PASSED" and self.event[
                'Cloudwatch_association_creation_config_win'] == "PASSED" and self.event[
                'Cloudwatch_association_creation_config_linux'] == "PASSED" and self.event[
                'falcon_association_creation_priv_linux'] == "PASSED" and self.event[
                'falcon_association_creation_pvt_win'] == "PASSED" and self.event[
                'flexera_association_creation_priv_linux'] == "PASSED" and self.event[
                'flexera_association_creation_pvt_win'] == "PASSED" and self.event[
                'rapid7_association_creation_priv_linux'] == "PASSED" and self.event[
                'rapid7_association_creation_pvt_win'] == "PASSED":
                return True
            elif self.event['ResourceProperties']['AccountType'] == "Data-Management" and self.event[
                'cloudhealth_association_creation_pub_linux'] == "PASSED" and self.event[
                'cloudhealth_association_creation_pub_win'] == "PASSED" and self.event[
                'Cloudwatch_association_creation'] == "PASSED" and self.event[
                'Cloudwatch_association_creation_config_win'] == "PASSED" and self.event[
                'Cloudwatch_association_creation_config_linux'] == "PASSED" and self.event[
                'falcon_association_creation_pub_linux'] == "PASSED" and self.event[
                'falcon_association_creation_pub_win'] == "PASSED" and self.event[
                'flexera_association_creation_pub_linux'] == "PASSED" and self.event[
                'flexera_association_creation_pub_win'] == "PASSED" and self.event[
                'rapid7_association_creation_pub_linux'] == "PASSED" and self.event[
                'rapid7_association_creation_pub_win'] == "PASSED":
                return True
            elif self.event['ResourceProperties']['AccountType'] == "Migration" and self.event[
                'cloudhealth_association_creation_pub_linux'] == "PASSED" and self.event[
                'cloudhealth_association_creation_pub_win'] == "PASSED" and self.event[
                'Cloudwatch_association_creation'] == "PASSED" and self.event[
                'Cloudwatch_association_creation_config_win'] == "PASSED" and self.event[
                'Cloudwatch_association_creation_config_linux'] == "PASSED" and self.event[
                'falcon_association_creation_pub_linux'] == "PASSED" and self.event[
                'falcon_association_creation_pub_win'] == "PASSED" and self.event[
                'flexera_association_creation_pub_linux'] == "PASSED" and self.event[
                'flexera_association_creation_pub_win'] == "PASSED" and self.event[
                'rapid7_association_creation_pub_linux'] == "PASSED" and self.event[
                'rapid7_association_creation_pub_win'] == "PASSED":
                return True
            else:
                return False
        except Exception as e:
            print(str(e))
            return False

    """Create features status HTML table after account is created/updated when email is sent to the operation's team"""

    def get_features_status(self):
        try:
            feature_table = """<table style="width:100%">
                <col style="width:50%">
                <col style="width:50%">
                <tr>
                    <th width="50%">Feature</th>
                    <th width="50%">Status</th>
                </tr>
                <tr>
                    <td width="50%">Platform Roles Status</td>
                    <td width="50%">""" + str(self.role_status()) + """</td>
                </tr>
                <tr>
                    <td width="50%">Budget</td>
                    <td width="50%">""" + str(self.budget_status()) + """</td>
                </tr>
                <tr>
                    <td width="50%">Enterprise Support</td>
                    <td width="50%">""" + str(self.enterprise_status()) + """</td>
                </tr>
                <tr>
                    <td width="50%">Default VPC Deletion Status</td>
                    <td width="50%">""" + str(self.default_vpc_deletion_status()) + """</td>
                </tr>
                <tr>
                    <td width="50%">Tag AMI</td>
                    <td width="50%">""" + str(self.ami_tagging_status()) + """</td>
                </tr>
                <tr>
                    <td width="50%">Domain Join Status</td>
                    <td width="50%">""" + str(self.domain_join_status()) + """</td>
                </tr>
                <tr>
                    <td width="50%">Access Analyzer</td>
                    <td width="50%">""" + str(self.access_analyzer_status()) + """</td>
                </tr>
                <tr>
                    <td width="50%">SNS Topic Status</td>
                    <td width="50%">""" + str(self.sns_topic_status()) + """</td>
                </tr>
                <tr>
                    <td width="50%">Block Public Access Status</td>
                    <td width="50%">""" + str(self.public_access_block()) + """</td>
                </tr>
                <tr>
                    <td width="50%">Enable EBS Encryption</td>
                    <td width="50%">""" + str(self.enable_ebs()) + """</td>
                </tr>
                <tr>
                    <td width="50%">Agent Association Status</td>
                    <td width="50%">""" + str(self.all_agent_association_status()) + """</td>
                </tr>
            </table>
            """
            return feature_table
        except Exception as e:
            print(str(e))
            return ""

    def send_templated_email_to_users(self):
        """
        This function to send mail based on the result send by Step Function stages
        Already created Template is used to send mails
        :return:
        """
        print('EmailParameters >' + str(self.email_parameter))
        receiver_name = ''

        try:
            email_status = ""
            if 'accountSuccess' in self.email_parameter:
                print("accountSuccess")
                email_status = self.send_success_email_to_operation()
                """
                # email_status = self.send_success_email_to_business_user()
                """
            if 'accountFailure' in self.email_parameter:
                print("accountFailure")
                email_status = self.send_failure_to_create_account_email()

            if 'VerifiedParameterFailure' in self.email_parameter:
                print("verifyParameterFailure")
                email_status = self.send_verify_parameter_failure_email()

            """
            Fetch DL Email Template is moved to platform_fetch_dl Lambda Function
            Any Changes to the Template should be done in that DL
            if 'fetchDLFailure' in self.email_parameter:
                print("fetchDLFailure")
                email_status = self.send_fetch_dl_email()
            """
            if 'budgetMail' in self.email_parameter:
                print("budgetMail")
                email_status = self.send_budget_email()

            return email_status
        except Exception as exception:
            print(str(exception))
            return exception


def lambda_handler(event, context):
    try:
        result_values = {}
        send_template_object = SendTemplatedMail(event, context)
        response_output = send_template_object.send_templated_email_to_users()
        if isinstance(response_output, Exception):
            print("Error while sending Email, Refer Cloudwatch Logs")
            return response_output
        print("send_templated_email_to_users response", response_output)
        return result_values
    except Exception as exception:
        print("Send Mail Error >>" + str(exception))
        return exception
