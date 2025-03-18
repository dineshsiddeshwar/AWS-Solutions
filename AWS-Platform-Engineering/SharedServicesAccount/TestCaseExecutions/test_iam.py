import boto3
import json
import pytest 
from TestCases.aws_iam_tests import *
# Create IAM client
# regions = ['us-east-1','eu-west-1','ap-southeast-1']

with open("../parameters.json") as json_data:
    parameters_data = json.load(json_data)
    aws_iam_roles = parameters_data.get('aws_iam_role', {})
    aws_iam_instance_profile = parameters_data.get('aws_iam_instance_profile', {})
    aws_iam_policy = parameters_data.get('aws_iam_policy', {})


iam = boto3.client('iam')
@pytest.mark.parametrize('role', aws_iam_roles)
def test_aws_iam_check_if_role_exist(role):
    assert aws_iam_check_if_role_exist(iam, role) == True

def test_aws_iam_check_if_instance_profile_exist():
    assert aws_iam_check_if_instance_profile_exist(iam, aws_iam_instance_profile) == True

@pytest.mark.parametrize("policy",aws_iam_policy)
def test_aws_iam_check_if_policy_exist(policy):
    account_id = parameters_data['account_id']
    assert aws_iam_check_if_policy_exist(iam, account_id, policy) == True



