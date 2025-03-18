import boto3
import logging
import time

#Cloudwatch LOGGER variables
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
LOGGER.addHandler(CH)

SUCCESS = 'SUCCESS'
FAILED = 'FAILED'
SSO_CLIENT = boto3.client('sso-admin')


def get_ssm_parameter(parameter_name):
    '''
    method : Retrieve the Permission set ARN
    param  : Permission set name stored in parameter store
    return : Arn of the parametr store
    '''
    try:
        LOGGER.info("Retrieving the arn for: '{0}'".format(parameter_name))
        ssm_param_client = boto3.client('ssm')
        retries = 0
        get_param_status = 'False'
        while retries < 4 and get_param_status == 'False':
            response = ssm_param_client.get_parameter(
                Name=parameter_name,WithDecryption=True)
            temp_res_code = response['ResponseMetadata']['HTTPStatusCode']
            if temp_res_code == 200:
                get_param_status = 'True'
                response_parameter = response['Parameter']
                parameter_value = response_parameter['Value']
                return parameter_value
            else:
                time_to_sleep = 2 ** retries
                retries += 1
                time.sleep(time_to_sleep)
    except Exception as ex:
        LOGGER.error("ARN retrival from the parameter store failed.")
        return ex


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
        LOGGER.info("Session opened for  SSO-Admin")
        response_sso = SSO_CLIENT.list_account_assignments(
            InstanceArn = permission_sets_arn['sso_instance_arn'],
            AccountId = account_number,
            PermissionSetArn = target_permission_set,
            MaxResults = 15)
        results_sso = response_sso['AccountAssignments']
        #pagination
        if response_sso['AccountAssignments']:
            while 'NextToken' in response_sso:
                response_sso = SSO_CLIENT.list_account_assignments(
                    InstanceArn = permission_sets_arn['sso_instance_arn'],
                    AccountId = account_number,
                    PermissionSetArn = target_permission_set,
                    NextToken=response_sso['NextToken'])
                results_sso.extend(response_sso['AccountAssignments'])
            response_sso = results_sso
        LOGGER.info(response_sso)
        #Create the list of users/groups with the given permission set arn
        for item in results_sso:
            resource_id.append(item['PrincipalId'])
            LOGGER.info("User list with resource ID's: '{0}'".format(resource_id))
        if resource_id == []:
            LOGGER.info("There are no users exist with '{0}'".format(target_permission_set))
            return resource_id,False
        return resource_id,True
    except Exception as ex:
        LOGGER.error("Error while retriving the Resource from the account: '{0}'".format(ex))
        return [],False


def marshal_permission_sets_arn():
    '''
    method : Retrieve ARNs of the permissions sets and dress in a dictionary
    param  : None
    returns: A dict of permission sets and thei ARNs
    '''
    try:
        return_dict = {}
        LOGGER.info("Inside the marshal_permission_sets_arn")
        return_dict['sso_instance_arn'] = str(get_ssm_parameter('sso_instance_arn'))
        return_dict['sso_irm_permission_set_arn'] = str(get_ssm_parameter('irm_permission_set'))
        return_dict['irm_group_arn'] = str(get_ssm_parameter('platform_irm_group'))
        return_dict['admin_permission_set_arn'] = str(get_ssm_parameter('admin_permission_set'))
        return_dict['aws_readonly_permission_set_arn'] = str(get_ssm_parameter('platform_readonly_permission_set'))
        return_dict['platform_readonly_group_arn'] = str(get_ssm_parameter('platform_readonly_group'))
        return_dict['itom_readonly_group_arn'] = str(get_ssm_parameter('itom_readonly_group'))
        return_dict['itom_readonly_permission_set_arn'] = str(get_ssm_parameter('itom_readonly_permission_set'))
        return return_dict
    except Exception as ex:
        LOGGER.error("Error while retriving the arn's from the parameter store: '{0}'".format(ex))
        exception = {'status' : 'Error while retriving the arn from the parameter store'}
        return exception


def add_group_assignment(account_number, permission_sets_arn, principaltype_target, target_permission_set, target_principalid):
    '''
    method : Fuction to assign a group with the permission set for given principaltype, permissionset, principalid
    param  : Account number, permission set arns dictionary, principal type, principal ID
    return : Status of account assignment creation
    '''
    try:
        LOGGER.info("Inside add group assignment. SSO_Instance_arn: '{0}'. SSO Permissions Set: '{1}'. SSO Principal ID: '{2}'".format(permission_sets_arn['sso_instance_arn'], target_permission_set, target_principalid))
        response = SSO_CLIENT.create_account_assignment(
            TargetId = account_number,
            InstanceArn =  permission_sets_arn['sso_instance_arn'],
            TargetType ='AWS_ACCOUNT',
            PermissionSetArn = target_permission_set,
            PrincipalType = principaltype_target,
            PrincipalId = target_principalid)
        LOGGER.info(response)
        if response.get('ResponseMetadata').get('HTTPStatusCode') != 200 :
            LOGGER.info("Something went wrong while adding user/group to the account '{0}'".format(account_number))
            return FAILED
        return SUCCESS
    except Exception as exception:
        LOGGER.error("Add user/group to new account is failed '{0}'".format(exception))
        return FAILED


def remove_group_assignment(account_number, permission_sets_arn, target_principaltype, resource_id, target_permission_set):
    '''
    method : Fuction to remove a group/user for given principaltype, permissionset
    param  : Account number, permission set arns dictionary, principal type, resourceId with list of users to be removed
    return : Status of account assignment deletion
    '''
    try:
        LOGGER.info("inside remove group assignment. SSO_Instance_arn: '{0}'. SSO Permissions Set: '{1}'.".format(permission_sets_arn['sso_instance_arn'],target_permission_set))
        if resource_id != []:
            for items in resource_id:
                LOGGER.info("removing the user/group '{0}'".format(items))
                response_delete = SSO_CLIENT.delete_account_assignment(
                InstanceArn = permission_sets_arn['sso_instance_arn'],
                TargetId = account_number,
                TargetType = 'AWS_ACCOUNT',
                PermissionSetArn = target_permission_set,
                PrincipalType = target_principaltype,
                PrincipalId = items)
                LOGGER.info((response_delete))
            if response_delete.get('ResponseMetadata').get('HTTPStatusCode') != 200 :
                LOGGER.info("Something went wrong while removing user/group to the account '{0}'".format(account_number))
                return FAILED
        else:
            LOGGER.info("There are no user/group to be deleted")
            return SUCCESS
        LOGGER.info("Removed user/group access of user")
        return SUCCESS
    except Exception as exception:
        LOGGER.error("Adding user/group to account is failed '{0}'".format(exception))
        return FAILED


def lambda_handler(event, context):
    '''
    Description: Fucntion to Remove admin access when account is created and add IRM group with IRM access and  Give readonly access to platform group
    Authors    : Dinesh/Nikhil
    PBI number : 461287 and 460294
    returns    : event
    '''
    try:
        LOGGER.info("Received a '{0}' Request".format(event['RequestType']))
        
        #marshalling permission set arn and event parameters
        permission_sets_arn = marshal_permission_sets_arn()

        modified_event = event
        temp_event = {}

        account_number = event['accountNumber']

        #checking fot the request type
        if event['RequestType'] == 'Create':
            LOGGER.info("Request type is Create!")
            #check for admin access users and remove the users
            user_id,list_assignments_status = list_assignments(account_number, permission_sets_arn, permission_sets_arn['admin_permission_set_arn'])
            if list_assignments_status == True:
                remove_admin_access_status = remove_group_assignment(account_number, permission_sets_arn, 'USER', user_id, permission_sets_arn['admin_permission_set_arn'])
            else:
                remove_admin_access_status = SUCCESS
                LOGGER.info("No admin users for removal")
            assignment_status = add_group_assignment(account_number, permission_sets_arn, 'GROUP', permission_sets_arn['sso_irm_permission_set_arn'], permission_sets_arn['irm_group_arn'])
            LOGGER.info("Adding platform IRM group is completed with the status {0}".format(assignment_status))
            group_assignment_status = add_group_assignment(account_number, permission_sets_arn, 'GROUP', permission_sets_arn['aws_readonly_permission_set_arn'], permission_sets_arn['platform_readonly_group_arn'])
            LOGGER.info("Adding platform ReadOnly group is completed with the status {}".format(group_assignment_status))
            itom_group_assignment_status = add_group_assignment(account_number, permission_sets_arn, 'GROUP', permission_sets_arn['itom_readonly_permission_set_arn'], permission_sets_arn['itom_readonly_group_arn'])
            LOGGER.info("Adding ITOM ReadOnly group is completed with the status {}".format(itom_group_assignment_status))
        elif event['RequestType'] == 'Update':
            LOGGER.info("Request type is Update!")
            #check for admin access users and remove the users
            user_id,admin_assignments_status = list_assignments(account_number, permission_sets_arn, permission_sets_arn['admin_permission_set_arn'])
            if admin_assignments_status == True:
                remove_admin_access_status = remove_group_assignment(account_number, permission_sets_arn, 'USER', user_id, permission_sets_arn['admin_permission_set_arn'])
            else:
                remove_admin_access_status = SUCCESS
                LOGGER.info("No admin users for removal")
                
            irm_users,irm_assignment_status = list_assignments(account_number, permission_sets_arn, permission_sets_arn['sso_irm_permission_set_arn'])
            if irm_assignment_status == False:
                assignment_status = add_group_assignment(account_number, permission_sets_arn, 'GROUP', permission_sets_arn['sso_irm_permission_set_arn'], permission_sets_arn['irm_group_arn'])
            else:
                assignment_status = SUCCESS
                LOGGER.info("Platform_IRM already exits")

            ro_group,ro_assignment_status = list_assignments(account_number, permission_sets_arn, permission_sets_arn['aws_readonly_permission_set_arn'])
            if ro_assignment_status == False or permission_sets_arn['platform_readonly_group_arn'] not in ro_group:
                 group_assignment_status = add_group_assignment(account_number, permission_sets_arn, 'GROUP', permission_sets_arn['aws_readonly_permission_set_arn'], permission_sets_arn['platform_readonly_group_arn'])
            else:
                group_assignment_status = SUCCESS
                LOGGER.info("ReadOnly platform group already exits")

            itom_group,itom_assignment_status = list_assignments(account_number, permission_sets_arn, permission_sets_arn['itom_readonly_permission_set_arn'])
            if itom_assignment_status == False or permission_sets_arn['itom_readonly_group_arn'] not in itom_group:
                 itom_group_assignment_status = add_group_assignment(account_number, permission_sets_arn, 'GROUP', permission_sets_arn['itom_readonly_permission_set_arn'], permission_sets_arn['itom_readonly_group_arn'])
            else:
                itom_group_assignment_status = SUCCESS
                LOGGER.info("ReadOnly ITOM group already exits")
        
        temp_event = {
                        "admin_removal_status" : remove_admin_access_status,
                        "irm_group_assignment_status" : assignment_status,
                        "readonly_group_assignment_status" : group_assignment_status,
                        "itom_readonly_assignment_status" : itom_group_assignment_status}
        modified_event.update(temp_event)
        return modified_event
    except Exception as ex:
        LOGGER.error("lambda has failed:'{0}'".format(ex))
        return event