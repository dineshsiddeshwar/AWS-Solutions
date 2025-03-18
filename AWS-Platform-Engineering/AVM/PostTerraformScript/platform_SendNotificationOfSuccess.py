import boto3
import json
import sys

class SendResponseOfRequests(object):

    def __init__(self, event):
        session_client = boto3.session.Session()
        self.ses_client = session_client.client('ses', region_name="us-east-1")

    def send_Processed_email(self, event):
        try:
            print("Sending email now....")
            body_text = """
                Hello Team,
                
                A new AWS@Shell account creation request is processed now. Below are the processed details and results.    
                    * Account Request Type : """ + event['RequestType'] + """      
                    * Account Number : """ + event['ProvisionedProduct']['AccountNumber'] + """
                    * Account Name : """ + event['ProvisionedProduct']['Name'] + """
                    * Account Creation Status : """ + event['ProvisionedProduct']['StatusAfterCreate'] + """
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

                In case of account request processing status like failure or error, please check the Step Function execution and Cloud Watch Logs.
                
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
                  <tr bgcolor="Tomato">
                    <td width="50%">Account Property Names</td>
                    <td width="50%">Account Values</td>
                  </tr>
                  <tr>
                    <td width="50%">Account Request Type</td>
                    <td width="50%">""" + event['RequestType'] + """</td>
                  </tr>
                  <tr bgcolor="yellow">
                    <td width="50%">Account Number</td>
                    <td width="50%">""" + event['ProvisionedProduct']['AccountNumber'] + """</td>
                  </tr>
                  <tr>
                    <td width="50%">Account Name</td>
                    <td width="50%">""" + event['ProvisionedProduct']['Name'] + """</td>
                  </tr>
                  <tr bgcolor="yellow">
                    <td width="50%">Account Creation Status</td>
                    <td width="50%">""" + event['ProvisionedProduct']['StatusAfterCreate'] + """</td>
                  </tr>
                  <tr>
                    <td width="50%">Sold to Code</td>
                    <td width="50%">""" + event['RequestEventData']['SoldToCode'] + """</td>
                  </tr>
                  <tr bgcolor="yellow">
                    <td width="50%">North Virginia VPC Size (Private account)</td>
                    <td width="50%">""" + event['RequestEventData']['NVirginia'] + """</td>
                  </tr>
                  <tr>
                    <td width="50%">Ireland VPC Size (Private account)</td>
                    <td width="50%">""" + event['RequestEventData']['Ireland'] + """</td>
                  </tr>
                  <tr bgcolor="yellow">
                    <td width="50%">Singapore VPC Size (Private account)</td>
                    <td width="50%">""" + event['RequestEventData']['Singapore'] + """</td>
                  </tr>                  
                  <tr>
                    <td width="50%">Custodian Admin Email</td>
                    <td width="50%">""" + event['RequestEventData']['CustodianUser'] + """</td>
                  </tr>
                  <tr bgcolor="yellow">
                    <td width="50%">Custodian User First Name</td>
                    <td width="50%">""" + event['RequestEventData']['CustodianUserFirstName'] + """</td>
                  </tr>
                  <tr>
                    <td width="50%">Custodian User Last Name</td>
                    <td width="50%">""" + event['RequestEventData']['CustodianUserLastName'] + """</td>
                  </tr>
                  <tr bgcolor="yellow">
                    <td width="50%">Requester Email Id </td>
                    <td width="50%">""" + event['RequestEventData']['RequestorEmail'] + """</td>
                  </tr>
                  <tr>
                    <td width="50%">Application Support DL</td>
                    <td width="50%">""" + event['RequestEventData']['SupportDL'] + """</td>
                  </tr>
                  <tr bgcolor="yellow">
                    <td width="50%">Apex ID</td>
                    <td width="50%">""" + event['RequestEventData']['ApexID'] + """</td>
                  </tr>
                  <tr>
                    <td width="50%">Environment</td>
                    <td width="50%">""" + event['RequestEventData']['Environment'] + """</td>
                  </tr>
                  <tr bgcolor="yellow">
                    <td width="50%">Budget Limit</td>
                    <td width="50%">""" + event['RequestEventData']['Budget'] + """</td>
                  </tr>
                  <tr>
                    <td width="50%">Line Of Business</td>
                    <td width="50%">""" + event['RequestEventData']['LOB'] + """</td>
                  </tr>
                  <tr bgcolor="yellow">
                    <td width="50%">Snow Request No</td>
                    <td width="50%">""" + event['RequestEventData']['RequestNo'] + """</td>
                  </tr>
                  <tr>
                    <td width="50%">Apex Environment</td>
                    <td width="50%">""" + event['RequestEventData']['Apex_Environment'] + """</td>
                  </tr>
                  <tr bgcolor="yellow">
                    <td width="50%">Apex ID Name</td>
                    <td width="50%">""" + event['RequestEventData']['Apex_ID_Name'] + """</td>
                  </tr>
                  <tr>
                    <td width="50%">Account Name Given</td>
                    <td width="50%">""" + event['RequestEventData']['AccountName'] + """</td>
                  </tr>
                  <tr bgcolor="yellow">
                    <td width="50%">Business Contributors</td>
                    <td width="50%">""" + event['RequestEventData']['BusinessContributors'] + """</td>
                  </tr>
                  <tr>
                    <td width="50%">Business Operators</td>
                    <td width="50%">""" + event['RequestEventData']['BusinessOperators'] + """</td>
                  </tr>
                  <tr bgcolor="yellow">
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
                  </tr>
                  <tr bgcolor="yellow">
                    <td width="50%">Work Load Type</td>
                    <td width="50%">""" + event['RequestEventData']['WorkLoadType'] + """</td>
                  </tr>
                </table>

                <p style="font-family:'Futura Medium'">In case of account request processing status like failure or error, please check the Step Function execution and Cloud Watch Logs</p>
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

try:
    local_file_path = str(sys.argv[1])+"parameters.json"
    print("Parameters local file path: ", local_file_path)
    with open(local_file_path) as json_data:
        parameters_data = json.load(json_data)
    print(parameters_data)
    if parameters_data :
      TagAMI = SendResponseOfRequests(parameters_data)
      print("object is created for class SendResponseOfRequests..")
      SendConsolidatedEmail = TagAMI.send_Processed_email(parameters_data)
      if SendConsolidatedEmail :
          print("Email sent...")
      else:
          print("failed to send email...")
except Exception as ex:
    print("There is an error %s", str(ex))