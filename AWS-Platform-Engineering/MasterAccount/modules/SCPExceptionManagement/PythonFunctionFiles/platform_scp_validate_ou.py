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

   
    
def lambda_handler(event, context):
    """
    This module just validate if the account is in Exception OU.
    """
    try:
        org_client = boto3.client('organizations')
        ssm_client = boto3.client('ssm')
        org_dict = {}
        modified_event = {}
        modified_event.update(event)
        #organizations_unit = {"private_OU":"","public_OU":"","hybrid_OU":"","private_exc_OU":"","public_exc_OU":""}
        LOGGER.info("Recieved the event :- ".format(event))
        org_response =  org_client.list_parents(
                            ChildId=event['accountNumber'],
                            MaxResults=10)
        ou_id = org_response['Parents'][0]['Id']
        LOGGER.info("The account {0} present in the OU {1}:- ".format(event['accountNumber'],ou_id))
        ssm_response = ssm_client.get_parameters(
                Names=["platform_private_exception_ou_id", "platform_public_exception_ou_id",
                       "platform_hybrid_ou_id", "platform_private_ou_id","platform_public_ou_id"],
                WithDecryption=True)
        for values in ssm_response['Parameters']:
                if values['Name'] == 'platform_private_exception_ou_id':
                    organizations_unit = values['Value']
                    org_dict.update({organizations_unit:"private_exc_OU"})
                elif values['Name'] == 'platform_public_exception_ou_id':
                    organizations_unit = values['Value']
                    org_dict.update({organizations_unit:"public_exc_OU"})
                elif values['Name'] == 'platform_hybrid_ou_id':
                    organizations_unit = values['Value']
                    org_dict.update({organizations_unit:"hybrid_OU"})
                elif values['Name'] == 'platform_private_ou_id':
                    organizations_unit = values['Value']
                    org_dict.update({organizations_unit:"private_OU"})
                elif values['Name'] == 'platform_public_ou_id':
                    organizations_unit = values['Value']
                    org_dict.update({organizations_unit:"public_OU"})
        print(org_dict)
        if ou_id in org_dict.keys():
            LOGGER.info("The account {0} is in {1} :- ".format(event['accountNumber'],org_dict[ou_id]))  
            if "private" in org_dict[ou_id]:
                account_type = "private"
            elif "public" in org_dict[ou_id]:
                account_type = "public"
            elif "hybrid" in org_dict[ou_id]:
                account_type = "hybrid"
        if org_dict[ou_id] == "private_exc_OU" or org_dict[ou_id] == "public_exc_OU":
            LOGGER.info("The account {0} is already in Exception OU :- ".format(event['accountNumber']))
            Exception_account = 'SUCCESS'
        else:
            LOGGER.info("The account {0} is not in Exception OU :- ".format(event['accountNumber']))
            Exception_account = 'FAILED'
        temp_dict = {"Exception_validation": Exception_account}
        modified_event.update(temp_dict)
        return modified_event
    except Exception as exception:
        print("Error in Lambda Handler", exception)
        event.update({"Exception_validation": "FAILED","Error_message": str(exception)})
        return event