import boto3
import json
import pytest 
from TestCases.aws_iam_tests import *
# Create IAM client
iam = boto3.client('iam')


with open("../parameters.json") as json_data:
    parameters_data = json.load(json_data)
    print(parameters_data)

@pytest.mark.parametrize('role', parameters_data['IAM']['ListOfPlatformIAMRoles'])
def test_aws_iam_check_if_role_exist(role):
    assert aws_iam_check_if_role_exist(iam, role) == True

def test_aws_iam_check_if_instance_profile_exist():
    assert aws_iam_check_if_instance_profile_exist(iam, parameters_data['IAM']['PlatformInstanceProfile']) == True

@pytest.mark.parametrize("policy",parameters_data['IAM']['ListOfPlatformIAMPolicies'])
def test_aws_iam_check_if_policy_exist(policy):
    account_id = parameters_data['account_id']
    assert aws_iam_check_if_policy_exist(iam, account_id, policy) == True



