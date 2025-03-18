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


def get_policy_content(policy_id):
    """
    This module is for getting the content of main policy
    """
    try:
        LOGGER.info("Inside get policy content :- ")
        org_response = org_client.describe_policy(PolicyId=policy_id)
        policy = json.loads(org_response['Policy']['Content'])
        return policy
    except Exception as exception:
        print("Error in Lambda Handler", exception)
        return False


def create_attach_policy(policy,accountid,name):
    """
        This module will create and attach the policy to exception account
    """
    try:
        LOGGER.info("Inside create Attach policy :- ")
        LOGGER.info("Creating the policy :- ")
        org_create_response = org_client.create_policy(
                                            Content=json.dumps(policy),
                                            Description='This policy is for exception',
                                            Name=name,
                                            Type='SERVICE_CONTROL_POLICY',
                                            Tags=[
                                                {
                                                    'Key': 'platform_donotdelete',
                                                    'Value': 'yes'
                                                }])
        LOGGER.info("Response of Creating the policy {0} ".format(org_create_response))
        if org_create_response['Policy']['PolicySummary']:
            org_attach_response = org_client.attach_policy(
                                            PolicyId=org_create_response['Policy']['PolicySummary']['Id'],
                                            TargetId=accountid)
            if org_attach_response['ResponseMetadata']['HTTPStatusCode'] == 200:
                policy_status = SUCCESS
            else:
                policy_status = FAILED
        else:
            LOGGER.error("SOmething went wrong in creating the policy....")
            policy_status = FAILED
        return policy_status,org_create_response['Policy']['PolicySummary']['Id']
    except Exception as exception:
        print("Error in Lambda Handler", exception)
        return FAILED

def lambda_handler(event, context):
    """
    This lambda handler will check the status of the provisioned product
    """
    try:
        LOGGER.info("Recieved the event :- ".format(event))
        modified_event = {}
        modified_event.update(event)
        policy_name = 'platform_service_whitelisting_'+ event["AccountType"] + '_' +  event["RequestNumber"] + '_' + event["accountNumber"]
        LOGGER.info("Policy will be created with the name :-  {0}".format(policy_name))
        LOGGER.info("Actions {0} will be allowed :-  {0}".format(event["actions"]))
        list_actions = event["actions"].split(",")
        print(list_actions)
        LOGGER.info("Acount Type is :-  {0}".format(event["AccountType"]))
        param_name = "platform_service_whitelist_policy_" + event["AccountType"]
        ssm_response = ssm_client.get_parameter(Name=param_name)
        policy_id = ssm_response['Parameter']['Value']
        policy_content = get_policy_content(policy_id)
        if policy_content:
            for statement in  policy_content['Statement']:
                if statement['Sid'] == 'platformServiceWhitelist':
                    for action in list_actions:
                        statement['NotAction'].append(action)
                    create_attach_status,id = create_attach_policy(policy_content,event["accountNumber"],policy_name)
                    break
                else:
                    LOGGER.info("Something went wrong. Mannual Intervention required")
                    create_attach_status = FAILED
        else:
            LOGGER.error("FAILED to fetch content. Mannual Intervention required")
            create_attach_status = FAILED
        modified_event.update({"Create_attach_status": create_attach_status})
        modified_event.update({"policy_id": id})
        return modified_event
    except Exception as exception:
        print("Error in Lambda Handler", exception)
        modified_event.update({"Create_attach_status": FAILED})
        return modified_event