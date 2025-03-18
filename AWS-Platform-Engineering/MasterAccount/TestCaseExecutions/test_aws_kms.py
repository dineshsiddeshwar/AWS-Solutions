import boto3
import json
import pytest 
from TestCases.aws_kms_tests import *
# Create DynamoDB client
kms_client = boto3.client('kms')

with open("../parameters.json") as json_data:
    parameters_data = json.load(json_data)
    print(parameters_data)

@pytest.mark.parametrize('alias', parameters_data['KMS']['ListOfKMSAliases'])
def test_aws_kms_check_if_alias_exist(alias):
    assert aws_kms_check_if_alias_exist(kms_client, alias) == True

@pytest.mark.parametrize('alias', parameters_data['KMS']['ListOfKMSAliases'])
def test_aws_kms_check_if_key_exist(alias):
    assert aws_kms_check_if_key_exist(kms_client, alias) == True

@pytest.mark.parametrize('alias', parameters_data['KMS']['ListOfKMSAliases'])
def test_aws_kms_check_if_key_policy_created(alias):
    assert aws_kms_check_if_key_policy_created(kms_client, alias) == True