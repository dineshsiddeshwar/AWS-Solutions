def aws_check_if_sso_permissionset_assigned_to_default_groups(SSO_CLIENT, account_number, sso_instance_arn,target_permission_set,groupPrincipalId):
    try:
        resource_id = []
        response_sso = SSO_CLIENT.list_account_assignments(
            InstanceArn = sso_instance_arn,
            AccountId = account_number,
            PermissionSetArn = target_permission_set,
            MaxResults = 15)
        results_sso = response_sso['AccountAssignments']
        if response_sso['AccountAssignments']:
            while 'NextToken' in response_sso:
                response_sso = SSO_CLIENT.list_account_assignments(
                    InstanceArn = sso_instance_arn,
                    AccountId = account_number,
                    PermissionSetArn = target_permission_set,
                    NextToken=response_sso['NextToken'])
                results_sso.extend(response_sso['AccountAssignments'])
        for item in results_sso:
            resource_id.append(item['PrincipalId'])
        if resource_id == []:
            return False
        if groupPrincipalId in resource_id:
            return True
        else:
            return False
    except Exception as e:
        print("error occured while aws_check_if_sso_permissionset_assigned_to_default_groups and error is {}".format(e))
        return False