def aws_sso_check_if_permission_set_exist(ssoadmin, permission_set_arn, instance_arn):
    try:
        response = ssoadmin.describe_permission_set(
            InstanceArn=instance_arn,
            PermissionSetArn=permission_set_arn
        )
        print(response['PermissionSet']['Name'])
    except Exception as e:
        print("error occured while aws_sso_check_if_permission_set_exist and error is {}".format(e))
        return False
    else:
        return True

