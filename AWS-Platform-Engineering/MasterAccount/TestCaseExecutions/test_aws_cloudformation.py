import boto3
import json
import pytest 
from TestCases.aws_cloudformation_tests import *
# Create IAM client
cf_client = boto3.client('cloudformation')

with open("../parameters.json") as json_data:
    parameters_data = json.load(json_data)
    print(parameters_data)

@pytest.mark.parametrize('stackname', parameters_data['CloudFormation']['ListOfCFStackNames'])
def test_aws_check_if_cloudformation_stack_exist(stackname):
    assert aws_check_if_cloudformation_stack_exist(cf_client, stackname) == True
