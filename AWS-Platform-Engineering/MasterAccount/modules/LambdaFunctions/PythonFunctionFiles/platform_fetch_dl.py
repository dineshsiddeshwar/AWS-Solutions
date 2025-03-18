"""
This module is used to fetch DL from DynamoDB
"""
from botocore.exceptions import ClientError
import logging
import boto3
import requests
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


class FetchDL(object):
    """
    # Class: FetchDL
    # Description: Includes all the properties and methoda to fetch the DL from the
    #              DLDetails table so that the new child account can be created from
    #              these DLS
    """

    def __init__(self, event, context):
        self.event = event
        self.context = context
        self.res_dict={}
        logger.info("Event: %s" % self.event)
        logger.info("Context: %s" % self.context)
        try:
            # get relevant input params from event

            self.response_data = {}
            self.reason_data = ""
            self.dl_for_new_account = ""
            session_client = boto3.Session()
            self.ssm_client = session_client.client('ssm')
            self.dl_table_name = event['SSMParametres']['dlTableName']
            self.sts_client = session_client.client('sts')
            self.dd_client = session_client.client('dynamodb', region_name="us-east-1")
            self.ses_client = boto3.client('ses')
            self.success_operation_dl = event['SSMParametres']['success_operation_dl']
            self.sender_id = event['SSMParametres']['sender_id']
        except Exception as exception:
            self.reason_data = "Missing required property %s" % exception
            logger.error(self.reason_data)
            print("ERROR FetchDL", exception)
            self.res_dict['fetch_dl'] = "FAILED"
            self.res_dict['reason_data'] = self.reason_data
            self.event['PhysicalResourceId'] = self.context.log_stream_name
            self.send(self.event, self.context,"FAILED", self.res_dict, self.reason_data)



    def fetch_dl_name(self):
        """
        The following method fetches the DL from the DLDetails table.
        This DL is used to create the master account.
        """
        print("inside fetchDLName")
        res_dict = {}
        try:
            scan_response = self.dd_client.scan(TableName=self.dl_table_name)
            items_list = scan_response.get('Items')
            if self.verify_dl_usage(items_list) < 1:
                print("No free DLs left to create new Dedicated Account. Hence exiting!!!")
                self.res_dict['fetch_dl'] = "FAILED"
                self.res_dict['reason_data'] = "No DL Left in table"
                self.event['PhysicalResourceId']=self.context.log_stream_name
                self.send(self.event, self.context,"FAILED", self.res_dict, self.reason_data)
                print ("-----------------------------------------------------------------------")
                print (self.res_dict)
                print("-----------------------------------------------------------------------")
                return self.res_dict
            dl_mail_id = ""
            dl_fetched = False
            for item_list in items_list:
                is_used = (item_list.get('IsUsed')).get('BOOL')
                in_progress = (item_list.get('InProgress')).get('BOOL')
                dl_mail_id = (item_list.get('DLEmailId')).get('S')
                if is_used is False and in_progress is False:
                    self.dl_for_new_account = dl_mail_id
                    print("{} to be used for creation of new child account!".format(
                        dl_mail_id))
                    print("Putting lock on the DL to avoid usage by other accounts")
                    
                    item_list["InProgress"] = True

                    response = self.dd_client.update_item(
                        TableName=self.dl_table_name,
                            Key={'DLEmailId': {'S' : self.dl_for_new_account}},
                            UpdateExpression="SET InProgress=:b",
                            ExpressionAttributeValues={
                                 ':b': {"BOOL": True}},
                            ReturnValues="ALL_NEW")
 
                    print(f"InProgress set to True for DL {dl_mail_id}")
                    dl_fetched = True
                    print(f"DL fetched {dl_fetched}")
                    break
            self.res_dict['dlForNewAccount']=dl_mail_id

            return self.res_dict
        except Exception as exception:
            self.reason_data = "Fetch dl name %s" % exception
            logger.error(self.reason_data)
            print("ERROR fetchDLName", exception)
            self.res_dict['fetch_dl'] = "FAILED"
            self.res_dict['reason_data'] = self.reason_data
            self.event['PhysicalResourceId']=self.context.log_stream_name
            self.send(self.event, self.context,"FAILED", self.res_dict, self.reason_data)
            return self.res_dict


    def verify_dl_usage(self, items_list):
        print("inside verifyDLUsage")
        count = 0
        try:
            for item_list in items_list:
                is_used = (item_list.get('IsUsed')).get('BOOL')
                in_progress = (item_list.get('InProgress')).get('BOOL')

                if is_used is False and in_progress is False:
                    count += 1
            if count < 10:
                print(
                    "Only {} unused DLs left. Please add more DLs to the Table "
                    "for creating new Dedicated Accounts!!!".format(count))
                send_email_list = ["fetchDLFailure"]
                self.res_dict['emailParameter'] = send_email_list
                # Code to send the warning email to Operations Team to create more
                # DLs and Add to the table.
                self.send_fetch_dl_email()

            self.res_dict['verify_dl_usage'] = "PASSED"
            print("Count is", count)
            return count
        except Exception as exception:
            self.reason_data = "Verify DL Usage %s" % exception
            self.res_dict['verify_dl_usage'] = "FAILED"
            logger.error(self.reason_data)
            print("ERROR verifyDLUsage", exception)
            return exception

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
								   Please get the DLs for AWS@Shell service created in the format “GXITSOCloudServices-AWS-Shell-[Sequence Number]” and add the DLs to the “DL_Details” table in Master Account with AccountID \"""" + str(
                self.event["ResourceProperties"]["AWSAccountId"]) + """\" for creating new AWS@Shell Accounts.
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

    def send(self, event, context, response_status, response_data, reason_data):
        '''
        Send status to the cloudFormation
        Template.
        '''
        print("Inside send method")
        response_url = event['ResponseURL']

        response_body = {}
        response_body['Status'] = response_status
        response_body['Reason'] = reason_data + ' See the details in CloudWatch Log Stream: ' + \
                                  context.log_stream_name
        response_body['PhysicalResourceId'] = event['PhysicalResourceId']
        response_body['StackId'] = event['StackId']
        response_body['RequestId'] = event['RequestId']
        response_body['LogicalResourceId'] = event['LogicalResourceId']
        response_body['Data'] = response_data

        json_responsebody = json.dumps(response_body)

        print("Response body:{}".format(json_responsebody))

        headers = {
            'content-type': '',
            'content-length': str(len(json_responsebody))
        }

        try:
            response = requests.put(response_url,
                                    data=json_responsebody,
                                    headers=headers)
            print("Status code:{} ".format(response.reason))
        except Exception as exception:
            print("send(..) failed executing requests.put(..):{} ".format(str(exception)))
            self.reason_data = "Error in sending response to Service Catalog %s" % exception
            logger.error(self.reason_data)
            self.res_dict['fetch_dl'] = False
            self.res_dict['reason_data'] = self.reason_data


def lambda_handler(event, context):
    """
    This is the entry point of the module
    :param event:
    :param context:
    :return:
    """
    result_value = {}
    try:

        result_value.update(event)
        print("The recieved event is",json.dumps(event))
        print("Received a {} Request".format(event['RequestType']))
        fetch_dl = FetchDL(event, context)
        output_value = fetch_dl.fetch_dl_name()
        print("Output of the function : " + str(output_value))
        result_value['fetch_dl'] = "PASSED"
        result_value.update(output_value)
        return result_value
    except Exception as exception:
        print("Error in Lambda Handler", exception)
        result_value['fetch_dl'] = "FAILED"
        result_value['Error']=str(exception)
        return (result_value)
