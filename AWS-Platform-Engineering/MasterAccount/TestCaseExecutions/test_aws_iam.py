import boto3
import json
import pytest 
from TestCases.aws_iam_tests import *
# Create IAM client
iam_client = boto3.client('iam')

with open("../parameters.json") as json_data:
    parameters_data = json.load(json_data)
    print(parameters_data)

@pytest.mark.parametrize('role', parameters_data['IAM']['ListOfMasterAccountIAMRoles'])
def test_aws_iam_check_if_role_exist(role):
    assert aws_iam_check_if_role_exist(iam_client, role) == True

@pytest.mark.parametrize('instance_profile', parameters_data['IAM']['ListOfInstanceProfiles'])
def test_aws_iam_check_if_instance_profile_exist(instance_profile):
    assert aws_iam_check_if_instance_profile_exist(iam_client, instance_profile) == True
    
@pytest.mark.parametrize('policy', parameters_data['IAM']['ListOfMasterAccountIAMPolicies'])
def test_aws_iam_check_if_policy_exist(policy):
    assert aws_iam_check_if_policy_exist(iam_client, policy,parameters_data['MasterAccount']['Id']) == True

dict = parameters_data['IAM']['ListOfRolesWithInlinePolicies']
list = [(k, v) for k, v in dict.items()]

@pytest.mark.parametrize("role, inlinepolicyname", list)
def test_aws_iam_check_if_inline_policy_is_created(role, inlinepolicyname):
    assert aws_iam_check_if_inline_policy_is_created(iam_client, role, inlinepolicyname) == True

@pytest.mark.parametrize("username", parameters_data['IAM']['ListOfUsers'])
def test_aws_iam_check_if_user_is_created(username):
    assert aws_iam_check_if_user_is_created(iam_client, username) == True

@pytest.mark.parametrize("username", parameters_data['IAM']['ListOfUsers'])
def test_aws_iam_check_if_access_key_is_created(username):
    assert aws_iam_check_if_access_key_is_created(iam_client, username) == True

@pytest.mark.parametrize("username", parameters_data['IAM']['ListOfUsers'])
def test_aws_iam_check_if_user_policy_attachment_is_created(username):
    assert aws_iam_check_if_user_policy_attachment_is_created(iam_client, username) == True

