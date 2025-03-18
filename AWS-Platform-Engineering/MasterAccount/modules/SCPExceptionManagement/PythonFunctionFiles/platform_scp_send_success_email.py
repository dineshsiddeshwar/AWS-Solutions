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


def get_custodian(accountid):
    """this module will return custodian email id"""
    try:
        LOGGER.info("Getting custodian Email id from DB")
        db_client = boto3.client('dynamodb')
        db_response = db_client.get_item(
                                    TableName='Account_Details',
                                    Key={
                                        'AccountNumber': {
                                            'S': accountid
                                        }
                                    },
                                    AttributesToGet=['CustodianUser']
                                )
        custodian_id = db_response['Item']['CustodianUser']['S']
        return custodian_id
    except Exception as ex:
        LOGGER.error("Encountered error while getting custoain Email ID".format(ex))    
        return False


def send_renwal_email(event):
    """This module will be responsible for sending success email"""
    try:
       LOGGER.info("Sending renwal email.") 
       ses_client = boto3.client('ses')
       titan_dl_str = get_ssm_param("tital_dl")
       sender_id = get_ssm_param("sender_id")
       requestor_email = event['requestorName']
       custodian_id = get_custodian(event["accountNumber"])
    #    body = "<html> <head> <style> table { font-family: Calibri, sans-serif; border-collapse: collapse; width: 100%; text-align: left; } td { border:1px solid #1f1f1f; text-align: left; padding: 10px; } th { border: 1px solid #1f1f1f; border-collapse: collapse; text-align: left; padding: 10px; background-color: #FFFF33; } tr:nth-child(even) { background-color: #aaaa; } pre {font-family: Calibri, sans-serif; size=1px} </style></head><pre>Dear Requestor, </pre> <br> <pre>As per your request " + event["reqno"] + " ,  we have extended your previous exemption. " + event["oldritm"] + "till " + event ["DueDate"] + "<br> Please check and Confirm the ticket closure.</pre> <br>"
    #    footer = " <br/><br/> **This is an auto generated mail by the AWS Platform Engineering Team. <br/><br/>"
    #    strTable = "</table><br><br><pre>Thanks,</pre><br><pre>AWS Platform Engineering team.</pre><br><br><br><footer>**This is an auto generated mail by the AWS Platform Engineering Team.</footer></html>"
    #    strTable = body+strTable+footer
       body_html =  """<p style="font-family:'Futura Medium'">Dear """ + requestor_email + """, </p>
                    <p style="font-family:'Futura Medium'">As per the request """ + event["RequestNumber"] + """, We have extended your previous exception request  """ + event["old_ritm"] + """ till """ + event ["Due_date"] + """ to the account """ + event["accountNumber"] + """ <br> Please check and Confirm the ticket closure.</p>
                    <P></p>
                    <p style="font-family:'Futura Medium'">If you have any questions or comments regarding this email, then please contact us at GX-IDSO-ETSOM-DP-CLOUD-AWS-DEVOPS@shell.com</p>
                    <P></p>
                    <p style="font-family:'Futura Medium'">Best Regards,</p>
                    <p style="font-family:'Futura Medium'">Cloud Services Team</p>
                    <p style="font-family:'Futura Medium'"><a href=https://www.yammer.com/shell.com/#/threads/inGroup?type=in_group&feedId=13574864&view=all>AWS at Shell Yammer</a>, <a href=https://ideas.cloud.shell.com//>AWS User Voice Portal</a> and <a href=https://servicenow.shell.com/sp?id=sc_cat_item_guide&sys_id=ae72bdb6db9bec5079c7d18c68961929>Service Now</a>.</p>
                """
       body_text = """Dear Requestor, \n As per your request """ + event["RequestNumber"] + """ , we have extended your previous exemption """ + event["old_ritm"] + """ till """ + event ["Due_date"]  \
            + """.\n Please check and Confirm the ticket closure. """ + " "\
                    + """\nBest Regards,\n AWS Platform Engineering team"""
       
       send_mail_response = ses_client.send_email(
            Source= sender_id,
            Destination={
                'ToAddresses': [requestor_email],
                'CcAddresses': [titan_dl_str,custodian_id]
            },
            Message={
                'Subject': {
                    'Data': event["RequestNumber"] + ': Service / Action Successfully Extended'
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



def send_email(event):
    """This module will be responsible for sending success email"""
    try:
       LOGGER.info("Sending email.") 
       ses_client = boto3.client('ses')
       titan_dl_str = get_ssm_param("tital_dl")
       sender_id = get_ssm_param("sender_id")
       requestor_email = event['requestorName']
       custodian_id = get_custodian(event["accountNumber"])
    #    body = "<html> <head> <style> table { font-family: Calibri, sans-serif; border-collapse: collapse; width: 100%; text-align: left; } td { border:1px solid #1f1f1f; text-align: left; padding: 10px; } th { border: 1px solid #1f1f1f; border-collapse: collapse; text-align: left; padding: 10px; background-color: #FFFF33; } tr:nth-child(even) { background-color: #aaaa; } pre {font-family: Calibri, sans-serif; size=1px} </style></head><pre>Dear Requestor, </pre> <br> <pre>As per your request " + event["reqno"] + " , we have allowed the specified ( " + event["actions"] + " ) actions. Please check and Confirm the ticket closure.</pre> <br>"
    #    footer = " <br/><br/> **This is an auto generated mail by the AWS Platform Engineering Team. <br/><br/>"
    #    strTable = "</table><br><br><pre>Thanks,</pre><br><pre>AWS Platform Engineering team.</pre><br><br><br><footer>**This is an auto generated mail by the AWS Platform Engineering Team.</footer></html>"
    #    strTable = body+strTable+footer
       body_html =  """<p style="font-family:'Futura Medium'">Dear """ + requestor_email + """, </p>
                    <p style="font-family:'Futura Medium'">As per the request """ + event["RequestNumber"] + """, we have Allowed the specified ( """ + event["actions"] + """ ) actions to the account - """ + event["accountNumber"]+ """. Please check and Confirm the ticket closure.</p>
                    <P></p>
                    <p style="font-family:'Futura Medium'">If you have any questions or comments regarding this email, then please contact us at GX-IDSO-ETSOM-DP-CLOUD-AWS-DEVOPS@shell.com</p>
                    <P></p>
                    <p style="font-family:'Futura Medium'">Best Regards,</p>
                    <p style="font-family:'Futura Medium'">Cloud Services Team</p>
                    <p style="font-family:'Futura Medium'"><a href=https://www.yammer.com/shell.com/#/threads/inGroup?type=in_group&feedId=13574864&view=all>AWS at Shell Yammer</a>, <a href=https://ideas.cloud.shell.com//>AWS User Voice Portal</a> and <a href=https://servicenow.shell.com/sp?id=sc_cat_item_guide&sys_id=ae72bdb6db9bec5079c7d18c68961929>Service Now</a>.</p>
                """
       body_text = """Dear Requestor, \n As per your request """ + event["RequestNumber"] + """ , we have allowed the specified ( """ + event["actions"] + """ ) actions.""" \
            + """.\n Please check and Confirm the ticket closure. """ + " "\
                    + """\nBest Regards,\n AWS Platform Engineering team"""
       
       send_mail_response = ses_client.send_email(
            Source= sender_id,
            Destination={
                'ToAddresses': [requestor_email],
                'CcAddresses': [titan_dl_str,custodian_id]
            },
            Message={
                'Subject': {
                    'Data': event["RequestNumber"] + ': Service / Action Successfully Allowed'
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
        LOGGER.info("Checking if failure email triggered")
        if "send_failure_status" in event.keys() and event['send_failure_status'] == "SUCCESS":
            LOGGER.info("Failure email is already triggered hence skipping")
            modified_event.update({'send_status': "SKIPPED"})
        else:
            if event['RequestType'] == 'New':
                LOGGER.info("Forming the success email content....")
                send_status = send_email(event)
                modified_event.update({'send_status': send_status})
            else:
                LOGGER.info("Forming the success email content....")
                send_status = send_renwal_email(event)
                modified_event.update({'send_status': send_status})
        return modified_event
    except Exception as exception:
        print("Error in Lambda Handler", exception)
        return event