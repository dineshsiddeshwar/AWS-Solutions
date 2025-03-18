def aws_iam_check_if_role_exist(iam, iamrole):
    try:
        response = iam.get_role(
            RoleName=iamrole
        )
        print(response['Role'])
    except Exception as e:
        print("error occured while aws_iam_check_if_role_exist and error is {}".format(e))
        return False
    else:
        return True
    
def aws_iam_check_if_IOTRole_role_exist(iam, IsIOTAccount, iamrole):
    try:
        if IsIOTAccount == 'No':
            return True
            
        response = iam.get_role(
            RoleName=iamrole
        )
        print(response['Role'])
    except Exception as e:
        print("error occured while aws_iam_check_if_role_exist and error is {}".format(e))
        return False
    else:
        return True


def aws_iam_check_if_instance_profile_exist(iam, instanceprofile):
    try:
        response = iam.get_instance_profile( InstanceProfileName=instanceprofile)
        print(response['InstanceProfile'])
    except Exception as e:
        print("error occured while aws_iam_check_if_instance_profile_exist and error is {}".format(e))
        return False
    else:
         return True

def aws_iam_check_if_policy_exist(iam, accountNumber, policyname):
    try:
        PolicyArnValue  = "arn:aws:iam::"+accountNumber+":policy/"+policyname
        response = iam.get_policy(
            PolicyArn=PolicyArnValue
        )
        print(response['Policy'])
    except Exception as e:
        print("error occured while invoking aws_iam_check_if_policy_exist and error is {}".format(e))
        return False
    else:
         return True