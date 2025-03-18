import json, boto3
import sys

SUCCESS = 'SUCCESS'
FAILED = 'FAILED'
SSO_CLIENT = boto3.client('sso-admin')

def list_assignments(account_number, permission_sets_arn, target_permission_set):
    '''
    method : Lists the assignments for the given permission set arn
    param  : Account number
    param  : List of permission set arn's
    param  : Target permission set arn
    return : List of users with specific permission set arn
    '''
    try:
        resource_id = []
        print("Session opened for  SSO-Admin")
        response_sso = SSO_CLIENT.list_account_assignments(
            InstanceArn = permission_sets_arn['sso_instance_arn'],
            AccountId = account_number,
            PermissionSetArn = target_permission_set,
            MaxResults = 15)
        results_sso = response_sso['AccountAssignments']

        if response_sso['AccountAssignments']:
            while 'NextToken' in response_sso:
                response_sso = SSO_CLIENT.list_account_assignments(
                    InstanceArn = permission_sets_arn['sso_instance_arn'],
                    AccountId = account_number,
                    PermissionSetArn = target_permission_set,
                    NextToken=response_sso['NextToken'])
                results_sso.extend(response_sso['AccountAssignments'])
            response_sso = results_sso
        print(response_sso)
        for item in results_sso:
            resource_id.append(item['PrincipalId'])
            print("User list with resource ID's: '{0}'".format(resource_id))
        if resource_id == []:
            print("There are no users exist with '{0}'".format(target_permission_set))
            return resource_id,False
        return resource_id,True
    except Exception as ex:
        print("Error while retriving the Resource from the account: '{0}'".format(ex))
        return [],False


def marshal_permission_sets_arn(event):
    '''
    method : Retrieve ARNs of the permissions sets and dress in a dictionary
    param  : None
    returns: A dict of permission sets and thei ARNs
    '''
    try:
        return_dict = {}
        print("Inside the marshal_permission_sets_arn to get instance arn and admin permission set")
        return_dict['sso_instance_arn'] = str(event['SSMParameters']['sso_instance_arn'])
        return_dict['admin_permission_set_arn'] = str(event['SSMParameters']['admin_permission_set'])
        return return_dict
    except Exception as ex:
        print("Error while retriving the arn's from the parameter store: '{0}'".format(ex))
        exception = {'status' : 'Error while retriving the arn from the parameter store'}
        return exception


def remove_group_assignment(account_number, permission_sets_arn, target_principaltype, resource_id, target_permission_set):
    '''
    method : Fuction to remove a group/user for given principaltype, permissionset
    param  : Account number, permission set arns dictionary, principal type, resourceId with list of users to be removed
    return : Status of account assignment deletion
    '''
    try:
        print("inside remove group assignment. SSO_Instance_arn: '{0}'. SSO Permissions Set: '{1}'.".format(permission_sets_arn['sso_instance_arn'],target_permission_set))
        if resource_id != []:
            for items in resource_id:
                print("removing the user/group '{0}'".format(items))
                response_delete = SSO_CLIENT.delete_account_assignment(
                InstanceArn = permission_sets_arn['sso_instance_arn'],
                TargetId = account_number,
                TargetType = 'AWS_ACCOUNT',
                PermissionSetArn = target_permission_set,
                PrincipalType = target_principaltype,
                PrincipalId = items)
                print((response_delete))
            if response_delete.get('ResponseMetadata').get('HTTPStatusCode') != 200 :
                print("Something went wrong while removing user/group to the account '{0}'".format(account_number))
                return FAILED
        else:
            print("There are no user/group to be deleted")
            return SUCCESS
        print("Removed user/group access of user")
        return SUCCESS
    except Exception as exception:
        print("Adding user/group to account is failed '{0}'".format(exception))
        return FAILED


try:
    local_file_path = str(sys.argv[1])+"parameters.json"
    print("Parameters local file path: ", local_file_path)
    with open(local_file_path) as json_data:
        parameters_data = json.load(json_data)
    print(parameters_data)
    account_number = parameters_data['ProvisionedProduct']['AccountNumber']
    print("Account Number:", account_number)
    permission_sets_arn = marshal_permission_sets_arn(parameters_data)
    print("AWS Permission Set ARN:", permission_sets_arn)
    if parameters_data['RequestType'] == 'Create':
        print("Request type is Create!")
        user_id,list_assignments_status = list_assignments(account_number, permission_sets_arn, permission_sets_arn['admin_permission_set_arn'])
        if list_assignments_status == True:
            remove_group_assignment(account_number, permission_sets_arn, 'USER', user_id, permission_sets_arn['admin_permission_set_arn'])
        else:
            print("No admin users for removal")  
    elif parameters_data['RequestType'] == 'Update':
        print("Request type is Update!")
        user_id,admin_assignments_status = list_assignments(account_number, permission_sets_arn, permission_sets_arn['admin_permission_set_arn'])
        if admin_assignments_status == True:
            remove_group_assignment(account_number, permission_sets_arn, 'USER', user_id, permission_sets_arn['admin_permission_set_arn'])
        else:
            print("No admin users for removal") 
except Exception as ex:
    print(str(ex))