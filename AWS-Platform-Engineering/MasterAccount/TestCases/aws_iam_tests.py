def aws_iam_check_if_role_exist(iam_client, iamrole):
    try:
        response = iam_client.get_role(
            RoleName=iamrole
        )
        print(response['Role'])
        if response['Role']:
            return True
    except Exception as e:
        print("error occured while aws_iam_check_if_role_exist and error is {}".format(e))
        return False
    else:
         return False

def aws_iam_check_if_instance_profile_exist(iam_client, instance_profile):
    try:
        response = iam_client.get_instance_profile( InstanceProfileName=instance_profile)
        print(response['InstanceProfile'])
        if response['InstanceProfile']:
            return True
    except Exception as e:
        print("error occured while aws_iam_check_if_instance_profile_exist and error is {}".format(e))
        return False
    else:
         return False

def aws_iam_check_if_policy_exist(iam_client, policyname,accountNumber):
    try:
        PolicyArnValue  = "arn:aws:iam::"+accountNumber+":policy/"+policyname
        response = iam_client.get_policy(
            PolicyArn=PolicyArnValue
        )
        print(response['Policy'])
        if response['Policy']:
            return True
    except Exception as e:
        print("error occured while invoking aws_iam_check_if_policy_exist and error is {}".format(e))
        return False
    else:
         return False

def aws_iam_check_if_inline_policy_is_created(iam_client, role, inlinepolicyname):
    try:
        policies = inlinepolicyname.split(",")
        count = 0
        for i in policies:          
            response = iam_client.get_role_policy(
                RoleName=role,
                PolicyName=i
            )
            print(response)
            if response:
                count += 1
        if count > 0:
            return True
    except Exception as e:
        print("error occured while invoking aws_iam_check_if_inline_policy_is_created and error is {}".format(e))
        return False
    else:
        return False

def aws_iam_check_if_user_is_created(iam_client, username):
    try:
        response = iam_client.get_user(
            UserName=username
        )
        if response['User']:
            print(response['User'])
            return True
    except Exception as e:
        print("error occured while invoking aws_iam_check_if_user_is_created and error is {}".format(e))
        return False
    else:
         return False
         
    
def aws_iam_check_if_access_key_is_created(iam_client, username):
    try:
        response = iam_client.list_access_keys(
            UserName=username
        )
        if response['AccessKeyMetadata']:
            print(response['AccessKeyMetadata'])
            return True
    except Exception as e:
        print("error occured while invoking aws_iam_check_if_access_key_is_created and error is {}".format(e))
        return False
    else:
         return False

def aws_iam_check_if_user_policy_attachment_is_created(iam_client, username):
    try:
        response = iam_client.list_attached_user_policies(
            UserName=username
        )
        if len(response['AttachedPolicies']) > 0:
            print(response['AttachedPolicies'])
            return True
        else:
            return False
    except Exception as e:
        print("error occured while invoking aws_iam_check_if_user_policy_attachment_is_created and error is {}".format(e))
        return False

                