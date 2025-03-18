import boto3
import logging
import json

LOGGER = logging.getLogger('logging')
LOGGER.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
LOGGER.addHandler(CH)



def get_ssm_param(parametre_name):
    """
    param: parametre_name
    return: parameter value for the given param name
    """
    try:
        ssm_client = boto3.client("ssm")
        parameter = ssm_client.get_parameter(
        Name=parametre_name,
            WithDecryption=True
        )
        if parameter:
            return parameter['Parameter']['Value']
    except Exception as ex:
        LOGGER.error("Encountered error while getting parameters".format(ex))

def send_email(event,error):
    """This module will be responsible for sending success email"""
    try:
       LOGGER.info("Sending Failure email.") 
       ses_client = boto3.client('ses')
       titan_dl_str = get_ssm_param("tital_dl")
       sender_id = get_ssm_param("sender_id")
    #    body = "<html> <head> <style> table { font-family: Futura Medium, sans-serif; border-collapse: collapse; width: 100%; text-align: left; } td { border:1px solid #1f1f1f; text-align: left; padding: 10px; } th { border: 1px solid #1f1f1f; border-collapse: collapse; text-align: left; padding: 10px; background-color: #FFFF33; } tr:nth-child(even) { background-color: #aaaa; } pre {font-family: Futura Medium, sans-serif; size=1px} </style></head><pre>Dear Titans, </pre> <br> <pre>As per your request " + event["reqno"] + " , There is a failure in  allowing the specified ( " + event["actions"] + " ) actions.<br> Please check ASAP</pre> <br>"
    #    Error = " <br/>Error Message :- <br/>" + error + "<br/>"
    #    strTable = "</table><br><pre>Thanks,</pre><br><pre>AWS Platform Engineering team.</pre><br><br><br><footer>**This is an auto generated mail by the AWS Platform Engineering Team.</footer></html>"
    #    strTable = body+Error+strTable
       body_html =  """<p style="font-family:'Futura Medium'">Dear Titans, </p>
                    <p style="font-family:'Futura Medium'">As per the request """ + event["RequestNumber"] + """, There is a failure in  allowing the specified ( """ + event["actions"] + """ ) actions. Please check ASAP. <br> Account Number :- """ + event['accountNumber']+ """</p>
                    <P></p>
                    <p style="font-family:'Futura Medium'">Below Reasons might be the cause for Failures :- <br></p>
                    <p style="font-family:'Futura Medium'">""" + error + """ </p>
                    <p style="font-family:'Futura Medium'">Best Regards,</p>
                    <p style="font-family:'Futura Medium'">Cloud Services Team</p>
                    <p style="font-family:'Futura Medium'"><a href=https://www.yammer.com/shell.com/#/threads/inGroup?type=in_group&feedId=13574864&view=all>AWS at Shell Yammer</a>, <a href=https://ideas.cloud.shell.com//>AWS User Voice Portal</a> and <a href=https://servicenow.shell.com/sp?id=sc_cat_item_guide&sys_id=ae72bdb6db9bec5079c7d18c68961929>Service Now</a>.</p>
                """
       body_text = """Dear Titans, \n As per your request """ + event["RequestNumber"] + """ ,There is a failure in  allowing the specified Actions ( """ + event["actions"] + """ ) actions.""" \
            + """.\n Please check ASAP""" + " " + "\n Error Message :- " + error \
                    + """\nBest Regards,\n AWS Platform Engineering team"""
       
       send_mail_response = ses_client.send_email(
            Source= sender_id,
            Destination={
                'ToAddresses': [titan_dl_str]
            },
            Message={
                'Subject': {
                    'Data': '[ ACTION REQUIRED ] - ' + event["RequestNumber"] + ' : Service / Action Allow Listing FAILED'
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
       if send_mail_response['MessageId']:
           status = 'SUCCESS'
       else:
           status = 'FAILED'
       return status
    except Exception as exception:
        print("Error in Sending an email", exception)
        return 'FAILED'    

    
def lambda_handler(event, context):
    """
    This module is meant for sending success final email
    """
    try:
        LOGGER.info("Received the event : - ".format(event))
        modified_event = {}
        modified_event.update(event)
        LOGGER.info("Checking for the error in the event!!!")
        if "Create_attach_status" in event.keys() and event['Create_attach_status'] == "FAILED":
            LOGGER.info("Failure happened in Creation of policy stage...")
            error_message = "Stage :- Creation Of SCP <br><br> 1. The issue might in appending the actions mentioned <br> 2. The action prefix provided might not be present."
        elif 'Account_movement' in event.keys() and ( event['Account_movement'] == "FAILED" or event['Account_movement'] == "Skipped" ):
            error_message = "Stage :- Account Movement <br><br> 1. Account might have moved to Root OU <br> 2. Account might be in Error or Tainted state before Moving <br> 3. There might be update in service catalog Form <br> 4. Account was not found while searching in provisioned product list"
        elif 'Update_service_policy' in event.keys() and event['Update_service_policy'] == "FAILED":
            error_message = "Stage :- Updating Existing SCP policy <br><br> 1. Could not find the Existing Service whitelist policy <br> 2. Account Might not be Present in Exception OU <br> 3. There might be no existing Service whitelisting policy attached. Hence Mannual Intervention required "
        elif 'Exception_validation' in event.keys() and event['Exception_validation'] == "FAILED":
            error_message = "Stage :- Validating Existing Account OU <br><br> 1. Could not find the Account in Exception OU. Hence Mannual Intervention required "
        elif 'Update_DB' in event.keys() and event['Update_DB'] == "FAILED":
            error_message = "Stage :- Updating Dynamo DB Table <br><br> 1. There might be update in Event recieved. Hence Mannual Intervention required <br> 2. Previous RITM might not be there Our DynamoDB. "
        elif 'provision_product_status' in event.keys() and ( event['provision_product_status'] == "ERROR" or event['provision_product_status'] == "TAINTED" ):
            error_message = "Stage :- Checking Provision Product Status <br><br> 1. The Product went into Taineted or Error State. Hence Mannual Intervention required <br> 2. There might be update in service catalog Form <br> 3. Control Tower Product might went into TAINTED State. <br> 4. There might be update in service catalog Form <br> 5. There Might be Default VPCs in the account which caused the failure <br><br> Note:- Account Might Got moved to Exception OU."
        elif 'check_ou_status' in event.keys() and event['check_ou_status'] == "FAILED":
            error_message = "Stage :- Checking Account Movement <br><br> 1. Due to some error in Control Tower product AVM might be failed and Account is not moved to exception OU. Hence Mannual Intervention required <br>"
        else:
            error_message = "There is an some issue for the account  - " + event['accountNumber'] + " while automating Service whitelisting."
        send_status = send_email(event,error_message)
        modified_event.update({'send_failure_status': send_status})
        return modified_event
    except Exception as exception:
        print("Error in Lambda Handler", exception)
        return event