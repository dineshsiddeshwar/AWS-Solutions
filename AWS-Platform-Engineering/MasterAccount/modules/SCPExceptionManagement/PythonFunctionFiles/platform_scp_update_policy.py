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
org_client = boto3.client('organizations')


def update_existing_policy(content,id,name):
    """
        This module will create and attach the policy to exception account
    """
    try:
        LOGGER.info("Inside Update Attach policy :- ")
        LOGGER.info("Update the policy :- ")
        org_update_response = org_client.update_policy(
                                        PolicyId=id,
                                        Name=name,
                                        Description="Existing policy for exemption",
                                        Content=json.dumps(content))
        LOGGER.info("Response of Creating the policy {0} ".format(org_update_response))
        if org_update_response['Policy']['PolicySummary']:
            policy_status = SUCCESS        
        else:
            LOGGER.error("SOmething went wrong in creating the policy....")
            policy_status = FAILED
        return policy_status
    except Exception as exception:
        print("Error in Lambda Handler", exception)
        return FAILED

def validate_create_service_whitelist_policy(id,list_actions):
    """
    This module will check ec2:* in the statment of the policy just to make sure its a service whitelisting policy
    """
    try:
        LOGGER.info("Inside Validation function :- ")
        validation_status = False
        org_response = org_client.describe_policy(PolicyId=id)
        policy = json.loads(org_response['Policy']['Content'])
        for statement in policy['Statement']:
            if 'NotAction' in statement.keys():
                if  "ec2:*" in statement['NotAction']:
                    validation_status = True
                    for action in list_actions:
                        statement['NotAction'].append(action)
                    break
        return validation_status,policy
    except Exception as exception:
        print("Error in Lambda Handler", exception)
        return False

def get_policy(accountid,list_actions):
    """
    This module will give existing policy id
    """
    try:
        LOGGER.info("Inside get policy ID :- ")
        org_response = org_client.list_policies_for_target(Filter='SERVICE_CONTROL_POLICY',TargetId=accountid)
        for policy in org_response['Policies']:
            if 'Service' in policy['Name'] or 'service' in policy['Name'] or 'SERVICE' in policy['Name']:
                policy_id = policy['Id']
                validation_status,policy_content = validate_create_service_whitelist_policy(policy_id,list_actions)
                if validation_status:
                    update_status = update_existing_policy(policy_content,policy_id,policy['Name'])
                else:
                    update_status = FAILED
                    LOGGER.info("Could not find the NotAction List in the policy Hence mannual intervention required..")
                break
            else:
                LOGGER.info("There is no existing policy attached. Hence mannual intervention requried..")
                update_status = FAILED
        return update_status,policy_id
    except Exception as exception:
        print("Error in Getting the policy", exception)
        return FAILED

def lambda_handler(event, context):
    """
    This lambda handler will check the status of the provisioned product
    """
    try:
        LOGGER.info("Recieved the event :- ".format(event))
        modified_event = {}
        modified_event.update(event)
        LOGGER.info("Actions {0} will be allowed :-  {0}".format(event["actions"]))
        list_actions = event["actions"].split(",")
        LOGGER.info("Acount Type is :-  {0}".format(event["AccountType"]))
        policy_status,id = get_policy(event["accountNumber"],list_actions)
        modified_event.update({"Update_service_policy": policy_status})
        modified_event.update({"policy_id": id})
        return modified_event
    except Exception as exception:
        print("Error in Lambda Handler", exception)
        modified_event.update({"Update_service_policy": FAILED})
        return modified_event