# This lambda was updated as part of RARS Migration from 1.0 to 2.0
from ast import Return
from cgi import print_directory
import boto3
import json
import datetime
import base64
import requests
from botocore.exceptions import ClientError

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication


class SendResponseOfRequests(object):

    def __init__(self, event, context):
        self.exception = []
        self.event = event
        self.context = context
        session_client = boto3.session.Session()
        self.sqs_client = session_client.client('sqs', region_name="us-east-1")
        self.ses_client = session_client.client('ses', region_name="us-east-1")
        self.secretManager_client = session_client.client('secretsmanager', region_name="us-east-1")

   ## Not used code.
    def GetQueueURL(self):
        try:
            queue_url = self.sqs_client.get_queue_url(QueueName="platform_snow_response_box.fifo").get('QueueUrl')
        except Exception as exception:
            print("Exception in Lambda Handler", exception)
        return queue_url

     ## Not used code.
    def CheckAndRetrieveMessage(self):
        try:
            print("Inside check and retrieve SQS message...!!")
            queueurl = self.GetQueueURL()
            print("Got queue URL : {}".format(queueurl))
            response = self.sqs_client.receive_message( QueueUrl=queueurl, AttributeNames=['All'], MaxNumberOfMessages=1)
            print("Send result: {}".format(response))
            if response and response['Messages']:
                print("There is message found in queue...!!")
                entries = [{'Id': msg['MessageId'], 'ReceiptHandle': msg['ReceiptHandle']} for msg in response['Messages']]
                delete_response = self.sqs_client.delete_message_batch( QueueUrl=queueurl, Entries=entries)
                if len(delete_response['Successful']) != len(entries):
                    print("The queue message not deleted hence exits..!!")
                    exit()
                else:
                    print("The queue message is deleted successfully..!!")
                return response['Messages']
            else:
                print("There is no message found in queue hence now it ends the run...!!")
        except Exception as exception:
            print("Exception in Lambda Handler", exception)

    def get_secret(self):
        secret_name = "IntegrationCreds-RARS"
        try:
            get_secret_value_response = self.secretManager_client.get_secret_value( SecretId=secret_name)
        except ClientError as e:
            if e.response['Error']['Code'] == 'DecryptionFailureException':
                raise e
            elif e.response['Error']['Code'] == 'InternalServiceErrorException':
                raise e
            elif e.response['Error']['Code'] == 'InvalidParameterException':
                raise e
            elif e.response['Error']['Code'] == 'InvalidRequestException':
                raise e
            elif e.response['Error']['Code'] == 'ResourceNotFoundException':
                raise e
        else:
            if 'SecretString' in get_secret_value_response:
                secret = get_secret_value_response['SecretString']
                return secret
            else:
                decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
                return decoded_binary_secret

    def get_SIMAAS_BearerToken(self, url, client_id, client_secret,username,password):
        try:
            payload='client_id='+client_id+'&client_secret='+client_secret+'&grant_type=password'+'&username='+username+'&password='+password
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            response = requests.request("POST", url, headers=headers, data=payload)
            bearer_token = json.loads(response.text)
        except Exception as exception:
            print("Exception while getting SIMAAS Bearer token and error is {}".format(exception))
        else:
            if bearer_token :
                print("bearer token has been returned...")
                return bearer_token
            else :
                print("No bearer token has been returned...")

    def send_Snow_Resonse (self, event):
        try:
            if event['ProvisionedProductList'][0]['StatusAfterUpdate'] == "AVAILABLE":
                statecode = "3"
                close_notes = "Account request is processed with success status.."
            else:
                statecode = "-5"
                close_notes = "Account request is processed with failed status.."
            api_data = json.loads(self.get_secret())
            if api_data :
                print("retrieved AWS secret manager data..")
                Bearer_token_data = self.get_SIMAAS_BearerToken(api_data['SIMAAS_URL'], api_data['SIMAAS_client_id'], api_data['SIMAAS_client_secret'],api_data['SIMAAS_username'],api_data['SIMAAS_password'])
                if Bearer_token_data :
                    print("SIMAAS bearer toaken is retrieved ...")
                    dynamicnowdata = datetime.datetime.now().strftime("%Y-%m-%d %I:%M:%S")
                    print("dynamic now date is framed..")
                    print("State code is:{}".format(statecode))
                    payload = json.dumps({
                            "u_supplier_reference": event['RequestEventData']['RequestTaskNo'],
                            "ice4u_target_id": event['RequestEventData']['RequestTaskNo'],
                            "u_work_notes": close_notes,
                            "u_close_notes": close_notes,
                            "u_state": statecode,
                            "u_short_description": event['ProvisionedProductList'][0]['AccountNumber'],
                            "u_description": event['ProvisionedProductList'][0]['Name'],
                            "u_due_date": dynamicnowdata,
                            "u_comments": close_notes
                        })
                    headers = { 'Authorization': 'Bearer '+Bearer_token_data['access_token'] , 'Content-Type': 'application/json'}
                    response = requests.request("POST", api_data['RARS_URL'], headers=headers, data=payload)
                    print(response.status_code)
                else:
                    print("Failed to get SIMAAS bearer toaken...")
            else:
                print("failed at getting required secrets from AWS secret manager..")
        except Exception as exception:
            print("Exception while sending response to Snow and error is {}".format(exception))
        else:
            if response.status_code :
                print("RARS API response status has been returned and value is:{}".format(response.status_code))
                return response.status_code
            else :
                print("No status code has been returned...")  

    def send_Processed_email(self, event):
        try:
            #cloud_health_dl =  "GXSITIIDSOOICOICOEFinOps@shell.com"
            print("Sending email now....")
            # The email body for recipients with non-HTML email clients.
            body_text = """
                Hello Team,
                
                A new AWS@Shell account creation request is processed now. Below are the processed details and results.          
                    * Account Number : """ + event['ProvisionedProductList'][0]['AccountNumber'] + """
                    * Account Name : """ + event['ProvisionedProductList'][0]['Name'] + """
                    * Account Creation Status : """ + event['ProvisionedProductList'][0]['StatusAfterUpdate'] + """
                    * Sold to Code : """ + event['RequestEventData']['SoldToCode'] + """
                    * North Virginia VPC Size (Private account) : """ + event['RequestEventData']['NVirginia'] + """
                    * Ireland VPC Size (Private account) : """ + event['RequestEventData']['Ireland'] + """
                    * Singapore VPC Size (Private account) : """ + event['RequestEventData']['Singapore'] + """                    
                    * Custodian Admin Email : """ + event['RequestEventData']['CustodianUser'] + """
                    * Custodian User First Name : """ + event['RequestEventData']['CustodianUserFirstName'] + """
                    * Custodian User Last Name : """ + event['RequestEventData']['CustodianUserLastName'] + """
                    * Requester Id : """ + event['RequestEventData']['RequestorEmail'] + """
                    * Application Support DL : """ + event['RequestEventData']['SupportDL'] + """
                    * Apex ID : """ + event['RequestEventData']['ApexID'] + """
                    * Environment : """ + event['RequestEventData']['Environment'] + """
                    * Budget Limit : """ + event['RequestEventData']['Budget'] + """
                    * Line Of Business : """ + event['RequestEventData']['LOB'] + """
                    * Snow Request No : """ + event['RequestEventData']['RequestNo'] + """
                    * Apex Environment : """ + event['RequestEventData']['Apex_Environment'] + """
                    * Apex ID Name : """ + event['RequestEventData']['Apex_ID_Name'] + """
                    * Account Name Given : """ + event['RequestEventData']['AccountName'] + """
                    * Work Load Type : """ + event['RequestEventData']['WorkLoadType'] + """
                    * Business Contributors : """ + event['RequestEventData']['BusinessContributors'] + """
                    * Business Operators : """ + event['RequestEventData']['BusinessOperators'] + """
                    * Business Limited Operators : """ + event['RequestEventData']['BusinessLimitedOperators'] + """
                    * Business Read Only Access : """ + event['RequestEventData']['BusinessReadOnly'] + """
                    * Business Custom : """ + event['RequestEventData']['BusinessCustom'] + """

                Features installed in the account:
                Please, follow the below SOP for more information on user access management.
                AWS@Shell User Access Management in ServiceNow: https://shell2.service-now.com/kb_view.do?sysparm_article=KB0311805
                To login to your account follow the below steps:
                    • When using Shell network: https://aws.shell.com
                          -> Select the login type as Single Sign-On (for AWS@Shell Accounts)
                          -> Click AWS Login
                          -> Navigates to the Single Sign-On page
                    • When using MacBook: https://sso.shell.com/idp/startSSO.ping?PartnerSpId=https%3A%2F%2Fus-east-1.signin.aws.amazon.com%2Fplatform%2Fsaml%2Fd-9067751237
                Useful links to get you started:
                    • Enterprise Cloud Platform Portal: https://eu001-sp.shell.com/sites/AAFAA2713
                    • AWS@Shell All You Will Ever Need To Know: https://devkit.shell.com/content/tools/AWS_at_shell_landing_page
                    • AWS@Shell Support Model: https://eu001-sp.shell.com/:w:/r/sites/AAFAA5187/L3/IB-Cloud%20CoE/AWS%20DA%202.0/General/AWS@Shell%20Support%20Model.docx?d=w89545071d19e4fa1b4c7e23d9b8f7d4a&csf=1&web=1&e=QpAJrg
                    • AWS@Shell Service Description Document: https://eu001-sp.shell.com/:w:/r/sites/AAFAA5187/L3/IB-Cloud%20CoE/AWS%20DA%202.0/General/AWS@Shell%20Service%20Description%20Document.docx?d=w6e68807292ac42d19037d7f32e54da6a&csf=1&web=1&e=y0Lgd2
                    • AWS Official Support Engagement: https://eu001-sp.shell.com/:b:/r/sites/AAFAA5187/L3/IB-Cloud%20CoE/AWS%20DA%202.0/General/AWS%20Support%20Engagement.pdf?csf=1&web=1&e=9S3kng
                    • Quick Reference Guides: https://eu001-sp.shell.com/:f:/r/sites/AAFAA5187/L3/IB-Cloud%20CoE/AWS%20DA%202.0/QRGs?csf=1&web=1&e=246jtB

                The Enterprise Cloud Platform Portal is your one-stop-shop for information. AWS@Shell is offered as a val platform, but assistance is available. Please find details
                of the Onboarding & User Success team on the portal. They are on hand to help accelerate your AWS@Shell journey.
                
                Kindly check that your account has been provisioned successfully and let us know if you have any concern or else confirm us to ticket closure.
                
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
                <p style="font-family:'Futura Medium'">A new AWS@Shell account creation request is processed now. Below are the processed details and results.</p>
                
                <table style="width:100%">
                    <col style="width:50%">
                    <col style="width:50%">
                  <tr bgcolor="yellow">
                    <td width="50%">Account Property Names</td>
                    <td width="50%">Account Values</td>
                  </tr>
                  <tr>
                    <td width="50%">Account Number</td>
                    <td width="50%">""" + event['ProvisionedProductList'][0]['AccountNumber'] + """</td>
                  </tr>
                  <tr>
                    <td width="50%">Account Name</td>
                    <td width="50%">""" + event['ProvisionedProductList'][0]['Name'] + """</td>
                  </tr>
                  <tr>
                    <td width="50%">Account Creation Status</td>
                    <td width="50%">""" + event['ProvisionedProductList'][0]['StatusAfterUpdate'] + """</td>
                  </tr>
                  <tr>
                    <td width="50%">Sold to Code</td>
                    <td width="50%">""" + event['RequestEventData']['SoldToCode'] + """</td>
                  </tr>
                  <tr>
                    <td width="50%">North Virginia VPC Size (Private account)</td>
                    <td width="50%">""" + event['RequestEventData']['NVirginia'] + """</td>
                  </tr>
                  <tr>
                    <td width="50%">Ireland VPC Size (Private account)</td>
                    <td width="50%">""" + event['RequestEventData']['Ireland'] + """</td>
                  </tr>
                  <tr>
                    <td width="50%">Singapore VPC Size (Private account)</td>
                    <td width="50%">""" + event['RequestEventData']['Singapore'] + """</td>
                  </tr>                  
                  <tr>
                    <td width="50%">Custodian Admin Email</td>
                    <td width="50%">""" + event['RequestEventData']['CustodianUser'] + """</td>
                  </tr>
                  <tr>
                    <td width="50%">Custodian User First Name</td>
                    <td width="50%">""" + event['RequestEventData']['CustodianUserFirstName'] + """</td>
                  </tr>
                  <tr>
                    <td width="50%">Custodian User Last Name</td>
                    <td width="50%">""" + event['RequestEventData']['CustodianUserLastName'] + """</td>
                  </tr>
                  <tr>
                    <td width="50%">Requester Email Id </td>
                    <td width="50%">""" + event['RequestEventData']['RequestorEmail'] + """</td>
                  </tr>
                  <tr>
                    <td width="50%">Application Support DL</td>
                    <td width="50%">""" + event['RequestEventData']['SupportDL'] + """</td>
                  </tr>
                  <tr>
                    <td width="50%">Apex ID</td>
                    <td width="50%">""" + event['RequestEventData']['ApexID'] + """</td>
                  </tr>
                  <tr>
                    <td width="50%">Environment</td>
                    <td width="50%">""" + event['RequestEventData']['Environment'] + """</td>
                  </tr>
                  <tr>
                    <td width="50%">Budget Limit</td>
                    <td width="50%">""" + event['RequestEventData']['Budget'] + """</td>
                  </tr>
                  <tr>
                    <td width="50%">Line Of Business</td>
                    <td width="50%">""" + event['RequestEventData']['LOB'] + """</td>
                  </tr>
                  <tr>
                    <td width="50%">Snow Request No</td>
                    <td width="50%">""" + event['RequestEventData']['RequestNo'] + """</td>
                  </tr>
                  <tr>
                    <td width="50%">Apex Environment</td>
                    <td width="50%">""" + event['RequestEventData']['Apex_Environment'] + """</td>
                  </tr>
                  <tr>
                    <td width="50%">Apex ID Name</td>
                    <td width="50%">""" + event['RequestEventData']['Apex_ID_Name'] + """</td>
                  </tr>
                  <tr>
                    <td width="50%">Account Name Given</td>
                    <td width="50%">""" + event['RequestEventData']['AccountName'] + """</td>
                  </tr>
                  <tr>
                    <td width="50%">Business Contributors</td>
                    <td width="50%">""" + event['RequestEventData']['BusinessContributors'] + """</td>
                  </tr>
                  <tr>
                    <td width="50%">Business Operators</td>
                    <td width="50%">""" + event['RequestEventData']['BusinessOperators'] + """</td>
                  </tr>
                  <tr>
                    <td width="50%">Business Limited Operators</td>
                    <td width="50%">""" + event['RequestEventData']['BusinessLimitedOperators'] + """</td>
                  </tr>
                  <tr>
                    <td width="50%">Business Read Only Access</td>
                    <td width="50%">""" + event['RequestEventData']['BusinessReadOnly'] + """</td>
                  </tr>
                  <tr>
                    <td width="50%">Business Custom</td>
                    <td width="50%">""" + event['RequestEventData']['BusinessCustom'] + """</td>
                  <tr>
                    <td width="50%">Work Load Type</td>
                    <td width="50%">""" + event['RequestEventData']['WorkLoadType'] + """</td>
                  </tr>
                </table>

                <p><b>Features installed in the account:</b></p>
                <p>Please follow the below SOP for more information on user access management.</p>
                <a href='https://shell2.service-now.com/kb_view.do?sysparm_article=KB0311805'>End User - AWS@Shell User Access Management (service-now.com)</a>
                <p>To login to your Account follow the below steps:-</p>
                <ol>
                     <li><b>When using Shell network - </b><a href='https://aws.shell.com/'>AWS Shell Console</a>- > Select the login type as Single Sign On (For AWS@Shell Accounts)-> Click AWS Login-> Navigates to the Single Sign-On page.
                     </li>
                     <li><b>When using MacBook - </b><a href='https://sso.shell.com/idp/startSSO.ping?PartnerSpId=https%3A%2f%2fus-east-1.signin.aws.amazon.com%2fplatform%2fsaml%2fd-9067751237'>  https://sso.shell.com/idp/startSSO.ping?PartnerSpId=https%3A%2f%2fus-east-1.signin.aws.amazon.com%2fplatform%2fsaml%2fd-9067751237
                     </a>
                     </li>
                </ol>
                <p><b>Useful links to get you started:</b></p>
                <ul>
                    <li>Link to the Enterprise Cloud Platform Portal: 
                        <a href='https://eu001-sp.shell.com/sites/AAFAA2713/'>Enterprise Cloud Platform Portal
                        </a>
                    </li>
                    <li>
                        Link to the AWS@Shell Support Model:
                        <a href="https://eu001-sp.shell.com/:w:/r/sites/AAFAA5187/L3/IB-Cloud%20CoE/AWS%20DA%202.0/General/AWS@Shell%20Support%20Model.docx?d=w89545071d19e4fa1b4c7e23d9b8f7d4a&csf=1&web=1&e=QpAJrg"> AWS@Shell Support Model
                        </a>
                    </li>
                    <li>
                        Link to the AWS Support Engagement:
                        <a href="https://eu001-sp.shell.com/:b:/r/sites/AAFAA5187/L3/IB-Cloud%20CoE/AWS%20DA%202.0/General/AWS%20Support%20Engagement.pdf?csf=1&web=1&e=9S3kng"> AWS Support Engagement
                        </a>
                    </li>
                    <li>
                        Link to the AWS@Shell Service Description Document:
                        <a href="https://eu001-sp.shell.com/:w:/r/sites/AAFAA5187/L3/IB-Cloud%20CoE/AWS%20DA%202.0/General/AWS@Shell%20Service%20Description%20Document.docx?d=w6e68807292ac42d19037d7f32e54da6a&csf=1&web=1&e=y0Lgd2">  AWS@Shell Service Description Document
                        </a>
                    </li>
                    <li>
                        Link for Quick Reference Guides:
                        <a href="https://eu001-sp.shell.com/:f:/r/sites/AAFAA5187/L3/IB-Cloud%20CoE/AWS%20DA%202.0/QRGs?csf=1&web=1&e=246jtB">   QRGs
                        </a>
                    </li>

                </ul>
                <p>
                    The <a href='https://eu001-sp.shell.com/sites/AAFAA2713/'>Enterprise Cloud Platform Portal</a>Enterprise Cloud Platform Portal is your one-stop-shop for information. AWS@Shell is offered as a self-service platform, but assistance is available. Please find details of the Onboarding & User Success team on the portal. They are on hand to help accelerate your AWS@Shell journey.
                </p>
                <p><b>Kindly check that your account has been provisioned successfully and let us know if you have any concern or else confirm us to ticket closure.</b></p>
                
                <p style="font-family:'Futura Medium'">Best Regards,</p>
                <p style="font-family:'Futura Medium'">Cloud Services Team</p>
                </body>
                </html>
                """
            # Provide the contents of the email.
            send_mail_response = self.ses_client.send_email(
                Source="SITI-CLOUD-SERVICES@shell.com",
                Destination={
                    'ToAddresses': ["GX-SITI-CPE-Team-Titan@shell.com", event['RequestEventData']['CustodianUser'], "GXSITIIDSOOICOICOEFinOps@shell.com"]
                },
                Message={
                    'Subject': {
                        'Data': event['RequestNo']+": New AWS@Shell account creation request processed"

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

def lambda_handler(event, context):
    try:
        print("inside the handler..")
        print("Event recieved from sqs queue.. and below is the event")
        print(event['Records'][0]['body'])
        if isinstance(event['Records'][0]['body'], str):
            event = json.loads(event['Records'][0]['body'])
            print("Type after conversion is at below...")
            print(type(event))
        else:
            event = json.loads(event['Records'][0]['body'])
            print("Type after conversion is at below...")
            print(type(event))
            
        sendqueueObject = SendResponseOfRequests(event, context)
        print("object is created for class SendResponseOfRequests..")
        ResponseToSnow = sendqueueObject.send_Snow_Resonse(event)
        if ResponseToSnow :
            print("response is sent back to snow and now sending eamil...")
        else:
            print("failed to send response to snow...")
        SendConsolidatedEmail = sendqueueObject.send_Processed_email(event)
        if SendConsolidatedEmail :
            print("Email sent...")
        else:
            print("failed to send email...")
    except Exception as exception:
        print(exception)