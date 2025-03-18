import boto3
import logging
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication
from email import encoders
import os
import base64
#CLouwatch logger variables
logger = logging.getLogger()
logger.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
logger.addHandler(CH)


SUCCESS = "SUCCESS"
FAILED = "FAILED"

def get_secret():
    try:
        
        secretarn = ""
        session_client = boto3.session.Session()
        sm_client = session_client.client('secretsmanager', region_name='us-east-1')
        sm_response = sm_client.get_secret_value( SecretId=secretarn)
        if sm_response:
            if "SecretString" in sm_response:
                secret = sm_response['SecretString']
                return secret
            else:
                decoded_secret = base64.b64decode(sm_response['SecretBinary'])
                return decoded_secret
    except Exception as ex:
        print("something went wrong in retirving secret")
        raise ex


def send_email(content, text, name, accountid):
    """
    This function will send an approval email
    """
    try:
        print("Inside sending an email")
        ses_client = boto3.client('ses',region_name='us-east-1')
        with open("/tmp/"+name, 'w') as file:
            file.write(content)
        file.close()
        sender = ''
        receiver = ['xyz@gmail.com']
        sourceArn = 'arn:aws:ses:us-east-1:XXX:identity/XXX.com'
        msg = MIMEMultipart('mixed')
        msg['From'] = sender
        msg['To'] = ','.join(receiver)
        msg['Subject'] = "[IMPORTANT] - "+accountid+" -  Action Required for EC2 Isolation"
        msg_body = MIMEMultipart('alternative')
        char_set = 'utf-8'
        htmlpart = MIMEText(text.encode(char_set),'html',char_set)
        msg_body.attach(htmlpart)

        attachment = MIMEApplication(open("/tmp/"+name, 'rb').read())
        attachment.add_header('Content-Disposition','attachment', filename=os.path.basename("/tmp/"+name))

        msg.attach(attachment)
        msg.attach(msg_body)
        ses_response = ses_client.send_raw_email(
                                Source=sender,
                                Destinations=receiver,
                                RawMessage={
                                    'Data': msg.as_string()
                                },
                                SourceArn=sourceArn
                                )
        if ses_response:
            os.remove("/tmp/"+name)
            return ses_response['MessageId']
    except Exception as ex:
        logger.error("There is something went wrong in sending email {}".format(ex))
        raise ex



def frame_html_text(instanceid,accountid,region):
    """
    This function return html content
    """
    try:
        html_text = f'''
        <p>Dear Approvers,</p>
        <p>This email is regarding the request we recieved from the IR team to isolate the your EC2 Instance. Below are the Details. Please check and Provide your approval.</p>
        <p><span style="text-decoration: underline;"><strong>Details:</strong></span></p>
        <p>Account Number:- <strong>{accountid}</strong></p>
        <p>Instance ID:- <strong>{instanceid}</strong></p>
        <p>Region:- <strong>{region}</strong></p>
        <p><span style="text-decoration: underline;"><strong>Approval/Rejection Process:-</strong></span></p>
        <p>Please Open the attached HTML file and Enter your Email Address and Provide your Decision ( Approve or Reject).</p>
        <p>Please Do not use any other HTML file ( If you have any in your local) apart from attached for the approval.</p>
        <p><span style="text-decoration: underline;"><strong>Note:-&nbsp;</strong></span></p>
        <p>As this is an Automation, your Approval will trigger the Automation in the Backend. Hence Requesting you to Submit your Decision Only Once.</p>
        <p>If you have any queries, Please reach out to <a href="mailto:dsiddeshwar.cw@solventum.com">dsiddeshwar.cw@solventum.com</a>&nbsp;And Do not reply to this email.</p>
        <p>&nbsp;</p>
        <p>Thanks and regards,</p>
        <p>Security engineering team</p>
        <p><strong>***This is an Automated email***</strong></p>
        '''
        return html_text
    except Exception as ex:
        print(ex)
        raise ex



def frame_html_content(lambdaname,instanceid,accountid,region):
    """
    This function return html content
    """
    try:
        temp_user = get_secret()
        user = json.loads(temp_user)
        secret_key = user['secretKey']
        access_key = user['accessKey']
        html_content = f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Approval Page</title>
            <script src="https://sdk.amazonaws.com/js/aws-sdk-2.978.0.min.js"></script>
        </head>
        <body>
            <h2>Decision Required</h2>
            <p>Please approve or reject the request:</p>
            <form id="approvalForm">
                <label for="email">Email:</label><br>
                <input type="email" id="email" name="email"><br><br>
                <input type="hidden" id="region" value={region}>
                <input type="hidden" id="instanceid" value={instanceid}>
                <input type="hidden" id="accountid" value={accountid}>
                <label for="decision">Decision:</label>
                <select id="decision" name="decision">
                    <option value="approve">Approve</option>
                    <option value="reject">Reject</option>
                </select>
                <br>
                <button type="submit">Submit</button>
            </form>
            
            <div id="message"></div> 
            
            <script>
                document.getElementById("approvalForm").addEventListener("submit", function(event) {{
                    event.preventDefault();
                    var region = document.getElementById("region").value;
                    var instanceId = document.getElementById("instanceid").value;
                    var accountId = document.getElementById("accountid").value;
                    var decision = document.getElementById("decision").value;
                    var email = document.getElementById("email").value;
                    approveOrReject(region, instanceid, accountid, decision, email);
                }});

                function approveOrReject(region, instanceId, accountId, decision, email) {{
                    
                    
                    var data = JSON.stringify({{
                        region: region,
                        instanceId: instanceId,
                        accountId: accountId,
                        decision: decision,
                        email: email
                    }});
                    AWS.config.update({{
                    accessKeyId: '{access_key}',
                    secretAccessKey: '{secret_key}',
                    region: 'us-east-1' // Change to your AWS region
                    }});
                    var lambda = new AWS.Lambda();
                    lambda.invoke({{
                        FunctionName: '{lambdaname}', // Replace with your Lambda function name
                        Payload: data // Pass any payload if needed
                    }}, function(err, data) {{
                        if (err) {{
                            console.error('Error:', err);
                            alert('Something went wrong. Please reach out to security Engineering team. Please close the tab. Thank you!');
                        }} else {{
                            console.log('Success:', data);
                            alert('Response is captured. Please close the tab and Do not click Anything Again. Thank you!!');
                        }}
                    }});
                    
                }}
            </script>
        </body>
        </html>
        '''
        return html_content
    except Exception as ex:
        print(ex)
        raise ex

def lambda_handler(event, context):
    """
    This lambda function sends email for the approval
    """
    try:
        print("Insider lambda handler")
        function = os.environ.get('FUNCTIONNAME')
        lambdaname = function.split(":")[6]
        print("lambda Name:- ",lambdaname)
        instanceid = event['instanceId']
        region = event['region']
        accountid = event['accountId']
        name = accountid+"_"+region+"_"+instanceid+".html"
        html_content = frame_html_content(lambdaname,instanceid,accountid,region)
        html_text = frame_html_text(instanceid,accountid,region)
        message_id = send_email(html_content,html_text, name, accountid)
        logger.info("Message sent:- {}".format(message_id))
        return message_id
    except Exception as ex:
        logger.error("There is something went wrong in lambda handler.:- {}".format(ex))
        raise ex