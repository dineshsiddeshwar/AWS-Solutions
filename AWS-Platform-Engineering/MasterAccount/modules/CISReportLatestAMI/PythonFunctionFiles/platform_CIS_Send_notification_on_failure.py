"""
This module is used to send notifications on CIS Report failure for the latest AMI
"""

import boto3
class SendEmailnotification(object):
    """
    # Class: Send Mail Notification
    # Description: Send email on faiulre to get CIS Score report for the latest AMI
    """

    def __init__(self, event, context):
        self.event = event
        self.context = context
        try:
            # get relevant input params from event
            global session
            session = boto3.session.Session()
            self.ses_client = boto3.client('ses')
            ssm_client = session.client('ssm')
            self.ami_id = event['ami_id']
            self.ami_name = event['ami_name']
            self.instanceid = event['Instance_ID']
            master_response = ssm_client.get_parameter(Name='master_account')
            self.master_account = master_response['Parameter']['Value']
            sender_id_response = ssm_client.get_parameter(Name='sender_id')
            self.sender_id = sender_id_response['Parameter']['Value']
            admin_dl_response = ssm_client.get_parameter(Name='admin_dl')
            self.admin_dl = admin_dl_response['Parameter']['Value']
        except Exception as exception:
            self.reason_data = "Missing required property %s" % exception
            print("ERROR Self GetCISReport", exception)

    def send_email_notification(self):
        """
        The following method is used to send email notifications
        on faliure to update CIS score in Dynamo DB.
        """
        res_dict = {}
        try:
            # This address must be verified with Amazon SES.
            sender_id = self.sender_id

            # The email body for recipients with non-HTML email clients.
            body_text = "Hello Team,\r\n Please check the instance of id=" + \
                        str(self.instanceid) + " launched with the latest AMI-" + \
                        str(self.ami_id) + " in the Account-" + str(self.master_account) + \
                        " for which CIS Score Report Analysis failed."

            # The HTML body of the email.
            body_html = """
            <html>
            <head></head>
            <body>
            <h2>Hello Team,</h2>
            <p>Please check the instance of id =""" + str(self.instanceid) + """ 
            launched with the latest AMI-""" + str(self.ami_id) + """ in the 
            Account-""" + str(self.master_account) + """ for which CIS Score 
            Report Analysis failed.</p>
            <p>Regards,</p>
            <p>DA2 Team</p>
            </body>
            </html>
            """
            try:
                # Provide the contents of the email.
                mail_response = self.ses_client.send_email(
                    Source=sender_id,
                    Destination={
                        'ToAddresses': [self.admin_dl]
                    },
                    Message={
                        'Subject': {
                            'Data': 'CIS Report Alert!!!'

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
                print("Email sent! Message ID:")
                print(mail_response['ResponseMetadata']['RequestId'])

                res_dict['ami_id'] = self.ami_id
                res_dict['ami_name'] = self.ami_name
                res_dict['Instance_ID'] = self.instanceid
                res_dict['RequestId'] = mail_response['ResponseMetadata']['RequestId']
                res_dict['MailStatus'] = 'Success'
                return res_dict
            except Exception as exception:
                print(exception.response['Error']['Message'])
                res_dict['ami_id'] = self.ami_id
                res_dict['ami_name'] = self.ami_name
                res_dict['Instance_ID'] = self.instanceid
                res_dict['MailStatus'] = 'Failed'
                return res_dict
        except Exception as exception:
            self.reason_data = "SendEmailnotification %s" % exception
            print("ERROR Send email notification", exception)
            return exception
def lambda_handler(event, context):
    """
    This is lambda handler calls the function to send email notifications
    """
    try:
        result_value = {}
        result_value.update(event)
        print("Received an event {}".format(event))
        send_email = SendEmailnotification(event, context)
        output_value = send_email.send_email_notification()
        print("Output of the function : " + str(output_value))
        result_value.update(output_value)
        return result_value
    except Exception as exception:
        print("Error in Lambda Handler", exception)
        return exception
