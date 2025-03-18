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

SUCCESS = "SUCCESS"
FAILED = "FAILED"

SESSION = boto3.Session()
STS_CLIENT = SESSION.client('sts')
ssm_client = SESSION.client('ssm')


def delete_old_item(ritm):
    """This Module will delete the old RITM when Renwal request recieved"""
    try:
        LOGGER.info("Inside Delete old RITM")
        dynamo_client = boto3.client('dynamodb')
        db_res = dynamo_client.delete_item(
                                    TableName='SCP_Exception_Management',
                                    Key={
                                        'RequestNumber': {
                                            'S': ritm
                                        }})
        if db_res:
            return SUCCESS
        else:
            return FAILED
    except Exception as ex:
        LOGGER.error("Encountered error while Delete an item".format(ex))
        return FAILED


def update_dynamo_db(event, ou_name):
    """This module will update dynamo DB table"""
    try:
        
        LOGGER.info("Updating Dynamo DB table..")
        dynamo_client = boto3.client('dynamodb')
        table_item = {
                'RequestNumber':{"S": event['RequestNumber']},
                'Request_type': {"S": event['RequestType']},
                'AccountNumber': {"S": event['accountNumber']},
                'AccountName': {"S": event['accountName']},
                'AccountType':{"S": event['AccountType']},
                'Current_OU':{"S": ou_name},
                'ExceptionPolicyId': {"S": event['policy_id']},
                'Action_allowed': {"S": event['actions']},
                'Old_Exception_Request_numuber':{"S": event['old_ritm']},
                'RequestedDate':{"S": str(event['Requested_date'])},
                'Expiry_date': {"S": event['Due_date']},
                'Requestor_name': {'S': event['requestorName']}
                }
        dynamo_response = dynamo_client.put_item(
            TableName= 'SCP_Exception_Management',
            Item=table_item
            )
        if dynamo_response['ResponseMetadata']['HTTPStatusCode'] == 200:
            if event['RequestType'] == 'Renewal':
                LOGGER.info("Delete the older RITM from the DB")
                delete_status = delete_old_item(event['old_ritm'])
                return delete_status
            else:
                return SUCCESS
        else:
            LOGGER.info("Something went wrong in Updating table")
            return FAILED
    except Exception as ex:
        LOGGER.error("Encountered error while updating DB".format(ex))
        return FAILED


def get_old_details(ritm):
    """This module will give you account type and policy id and actions"""
    try:
        LOGGER.info("Getting Details from DB")
        db_client = boto3.client('dynamodb')
        db_response = db_client.get_item(
                                    TableName='SCP_Exception_Management',
                                    Key={
                                        'RequestNumber': {
                                            'S': ritm
                                        }
                                    },
                                    AttributesToGet=['AccountType','ExceptionPolicyId','Action_allowed']
                                )
        atype = db_response['Item']['AccountType']['S']
        id = db_response['Item']['ExceptionPolicyId']['S']
        actions = db_response['Item']['Action_allowed']['S']
        temp_dict = {"AccountType": atype,"policy_id":id,"actions":actions}
        return temp_dict
    except Exception as ex:
        LOGGER.error("Encountered error while getting custoain Email ID".format(ex))    
        return {}


def get_ou_name_org(id):
    """This module will return OU name"""
    try:
        LOGGER.info("Inside get ou name")
        org_client = boto3.client('organizations')
        org_response =  org_client.list_parents(
                            ChildId=id,
                            MaxResults=10)
        ou_id = org_response['Parents'][0]['Id']
        name_response = org_client.describe_organizational_unit(OrganizationalUnitId=ou_id)
        ou_name = name_response['OrganizationalUnit']['Name']
        return ou_name
    except Exception as ex:
        LOGGER.error("Encountered error while getting OU name".format(ex))    
        return ''

def lambda_handler(event, context):
    """
    This lambda handler will Update the Dynamo DB table
    """
    try:
        LOGGER.info("Recieved the event :- ".format(event))
        modified_event = {}
        modified_event.update(event)
        if event['RequestType'] == 'Renewal':
            get_old_dict = get_old_details(event['old_ritm'])
            if get_old_dict == {}:
                modified_event.update({"Update_DB": FAILED})
                return modified_event
            else:
                event.update(get_old_dict)
        LOGGER.info("Actions {0} is  allowed :-  {0}".format(event["actions"]))
        list_actions = event["actions"].split(",")
        LOGGER.info("Acount Type is :-  {0}".format(event["AccountType"]))
        get_ou_name = get_ou_name_org(event["accountNumber"])
        modified_event.update({"Current_OU": get_ou_name})
        update_status = update_dynamo_db(event, get_ou_name)
        modified_event.update({"Update_DB": update_status})
        return modified_event
    except Exception as exception:
        print("Error in Lambda Handler", exception)
        modified_event.update({"Update_DB": FAILED})
        return modified_event