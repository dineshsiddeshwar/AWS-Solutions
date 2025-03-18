import json
import boto3
import logging
import re

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
LOGGER.addHandler(CH)
policy_actions = ['UpdateAssumeRolePolicy','UpdateRole','CreateRole','DetachRolePolicy']

SUCCESS = "SUCCESS"
FAILED = "FAILED"



def check_if_platform_policy_exists(role, policy):
    '''
    This function checks if platform admin restriction policy is attached or not
    '''
    try:
        iam_client = boto3.client('iam')
        policies = []
        policy_response = iam_client.list_attached_role_policies(
            RoleName=role,
            MaxItems=15)
        for policy in policy_response["AttachedPolicies"]:
            policies.append(policy["PolicyName"])
        while policy_response['IsTruncated']:
            policy_response = iam_client.list_attached_role_policies(
            RoleName=role,
            Marker=policy_response['Marker'],
            MaxItems=15)
            for policy in policy_response["AttachedPolicies"]:
                policies.append(policy["PolicyName"])
        if policy in policies:
            return True
        else:
            return False
    except Exception as e:
        LOGGER.error("Something is wrong in checking  restrcition :{0}".format(e))
        return False 

      

def attach_admin_restrict_policy(role_name, iam_client):
    '''
    This fucntion attaches admin restriction policy
    '''
    try:
        sts_client = boto3.client('sts')
        accounts_id = sts_client.get_caller_identity()['Account']
        LOGGER.info("Recieved the OIDC role name {0}".format(role_name))
        ssm_client = boto3.client('ssm')
        account_type_response = ssm_client.get_parameter(Name='/Platform-Tag/platform_AccountType')
        account_type = account_type_response['Parameter']['Value']
        if account_type == 'private' or account_type == 'hybrid':
            admin_policy_arn = "arn:aws:iam::" + str(accounts_id) + ":policy/platform_admin_restriction_private_us-east-1"
        else:
            admin_policy_arn = "arn:aws:iam::" + str(accounts_id) + ":policy/platform_admin_restriction_public_us-east-1"
        LOGGER.info("Attaching policy......")
        policy_name = admin_policy_arn.split('/')[1]
        get_role_respone = iam_client.get_role(RoleName=role_name)
        if 'Tags' in get_role_respone['Role'].keys():
            role_tags = get_role_respone['Role']['Tags']
            tag_present = True
        else:
            tag_present = False
        if tag_present:
            count = 0
            for tag in role_tags:
                if tag['Key'] == 'platform_monitored' and tag['Value'] == 'no':
                    count +=1
            if count != 1:
                get_role_policy_response = check_if_platform_policy_exists(role_name, policy_name)
                if get_role_policy_response == False:
                    attach_policy_response = iam_client.attach_role_policy(
                                            PolicyArn=admin_policy_arn,
                                            RoleName=role_name )
                    if attach_policy_response['ResponseMetadata']['HTTPStatusCode'] == 200:
                        LOGGER.info("Attached admin restriction policy to role {0}".format(role_name))
                        return SUCCESS
                    else:
                        return FAILED
                else:
                    LOGGER.info("Platform Admin Restriction  policy Already exists......")
                    return SUCCESS
            else:
                LOGGER.info("Its not a platform Monitored role and has been excluded from attaching restriction policy based on exception......")
                return SUCCESS
        else:
            LOGGER.info("No Tags are present......")
            get_role_policy_response = check_if_platform_policy_exists(role_name, policy_name)
            if get_role_policy_response == False:
                attach_policy_response = iam_client.attach_role_policy(
                                        PolicyArn=admin_policy_arn,
                                        RoleName=role_name )
                if attach_policy_response['ResponseMetadata']['HTTPStatusCode'] == 200:
                    LOGGER.info("Attached admin restriction policy to role {0}".format(role_name))
                    return SUCCESS
                else:
                    return FAILED
            else:
                LOGGER.info("Platform Admin Restriction  policy Already exists......")
                return SUCCESS
    except Exception as e:
        LOGGER.error("Something is wrong:{0}".format(e))
        return FAILED 


def lambda_handler(event, context):
    try:
        repos_trusted = []
        removal_org_candidates = []
        if event['detail']['eventName'] in policy_actions:
            role_name = event['detail']['requestParameters']['roleName']
            client = boto3.client('iam')
            sts_client = boto3.client('sts')
            account_id = sts_client.get_caller_identity()['Account']
            print("account id is : ", account_id)
            response = client.get_role(
                RoleName=role_name)
            role_response = response['Role']['AssumeRolePolicyDocument']['Statement']
            for item in role_response:
                temp_dict = item
                print(temp_dict)
                if 'Principal' in temp_dict:
                    federate = temp_dict['Principal']['Federated'].split('/')
                    print(federate)
                    #to create SSM parameter store in mvp2 or AVM Update.
                    if (federate[1] == 'token.actions.githubusercontent.com') or ("oidc.eks" in federate[1] and "amazonaws.com" in federate[1]):
                        LOGGER.info("It is a githubusercontent or EKS federate and initiating trsuted org verification.")
                        LOGGER.info("Attaching platform ADmin restriction policy....")
                        status = attach_admin_restrict_policy(role_name, client)
                        LOGGER.info("Attached platform Admin restriction policy.... and the status is {}".format(status))
                    else:
                        LOGGER.info("This role is not related to OIDC provider. Exiting..!")
                        return 
                    if ('StringEquals' in temp_dict['Condition'].keys()) and ('token.actions.githubusercontent.com:sub' in temp_dict['Condition']['StringEquals'].keys()):
                        print("Condition has StringEquals for github oidc.......")
                        matchCondition = "StringEquals"
                        temp_list = temp_dict['Condition']['StringEquals']['token.actions.githubusercontent.com:sub']
                    elif ('StringLike' in temp_dict['Condition'].keys()) and ('token.actions.githubusercontent.com:sub' in temp_dict['Condition']['StringLike'].keys()):
                        print("Condition has StringLike for github oidc.......")
                        matchCondition = "StringLike"
                        temp_list = temp_dict['Condition']['StringLike']['token.actions.githubusercontent.com:sub']
                    elif ('StringLike' in temp_dict['Condition'].keys()) and ("oidc.eks" in federate[1] and "amazonaws.com" in federate[1]):
                        print("Condition has StringLike for eks oidc.......")
                        matchCondition = "StringLike"
                        for eksitem in temp_dict['Condition']['StringLike'].keys():
                            if ":sub" in eksitem:
                                temp_list = temp_dict['Condition']['StringLike'][eksitem]
                                ekssubkey =  eksitem
                                break
                    elif ('StringEquals' in temp_dict['Condition'].keys()) and ("oidc.eks" in federate[1] and "amazonaws.com" in federate[1]):
                        print("Condition has StringEquals for eks oidc.......")
                        matchCondition = "StringEquals"
                        for eksitem in temp_dict['Condition']['StringEquals'].keys():
                            if ":sub" in eksitem:
                                temp_list = temp_dict['Condition']['StringEquals'][eksitem]
                                ekssubkey =  eksitem
                                break
                    else:
                        print("Did not match the existing conditions..")
                        return
                    if temp_list:
                        if type(temp_list) == str:
                            print("temp_list is string..")
                            if (federate[1] == 'token.actions.githubusercontent.com'):
                                print("Its github oidc connect..")
                                temp_str = temp_list.split(":")
                                temp_str.pop(0)
                                if len(temp_str)>0:
                                    temp_str = temp_str[0].split("/")
                                    #to create SSM parameter store in mvp2 or AVM Update
                                    if temp_str[0] in ['sede-open', 'sede-res','sede-x','shellagilehub','sdu-rds'] and account_id in temp_dict['Principal']['Federated']:
                                        LOGGER.info("The role is compliant with prescribed github org")
                                        repos_trusted.append(temp_str[0])
                                    else:
                                        LOGGER.info("The role is not compliant with prescribed github org")
                                        temp_dict['Condition'][matchCondition]['token.actions.githubusercontent.com:sub'] = []
                                        assume_role_document = json.dumps(response['Role']['AssumeRolePolicyDocument'])
                                        response = client.update_assume_role_policy(PolicyDocument= str(assume_role_document),RoleName=role_name)
                                        print("role updated successfully for Assume Role Policy Document statement..: ", temp_dict)
                            elif ("oidc.eks" in federate[1] and "amazonaws.com" in federate[1]): 
                                print("Its eks oidc connect..")
                                if account_id not in temp_dict['Principal']['Federated']:
                                    temp_dict['Condition'][matchCondition][ekssubkey] = []
                                    assume_role_document = json.dumps(response['Role']['AssumeRolePolicyDocument'])
                                    response = client.update_assume_role_policy(PolicyDocument= str(assume_role_document),RoleName=role_name)
                                    print("role updated successfully for Assume Role Policy Document statement..: ", temp_dict)
                            else:
                                print("Not falls in scoped remediations....")
                        else:
                            print("temp_list is list..")
                            if (federate[1] == 'token.actions.githubusercontent.com'):
                                print("Its github oidc connect..")
                                for item in temp_list:
                                    temp_str = item.split(":")
                                    temp_str.pop(0)
                                    if len(temp_str)>0:
                                        temp_str = temp_str[0].split("/")
                                        #to create SSM parameter store in mvp2 or AVM Update
                                        if temp_str[0] in ['sede-open', 'sede-res','sede-x','shellagilehub','sdu-rds'] and account_id in temp_dict['Principal']['Federated']:
                                            LOGGER.info("The role is compliant with prescribed github org")
                                            repos_trusted.append(temp_str[0])
                                        else:
                                            LOGGER.info("The role is not compliant with prescribed github org")
                                            removal_org_candidates.append(item)
                            elif ("oidc.eks" in federate[1] and "amazonaws.com" in federate[1]): 
                                print("Its eks oidc connect..")
                                if account_id not in temp_dict['Principal']['Federated']:
                                    temp_dict['Condition'][matchCondition][ekssubkey] = []
                                    assume_role_document = json.dumps(response['Role']['AssumeRolePolicyDocument'])
                                    response = client.update_assume_role_policy(PolicyDocument= str(assume_role_document),RoleName=role_name)
                                    print("role updated successfully for Assume Role Policy Document statement..: ", temp_dict)
                            else:
                                print("Not falls in scoped remediations....")
                        if removal_org_candidates:
                            for item in removal_org_candidates:
                                if item in temp_list and type(temp_list) != str :
                                    temp_list.remove(item)
                            assume_role_document = json.dumps(response['Role']['AssumeRolePolicyDocument'])
                            response = client.update_assume_role_policy(
                                PolicyDocument= str(assume_role_document),
                                RoleName=role_name)
                        print("role updated successfully for Assume Role Policy Document statement..: ", temp_dict)
        else:
            LOGGER.info("Not necessarily a role with OIDC or different.")
            return
    except Exception as e:
        LOGGER.error("Something is wrong:{0}".format(e))
        return