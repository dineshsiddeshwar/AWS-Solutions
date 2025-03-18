import boto3
import json
import pytest 
from TestCases.aws_cft_tests import *
# Create CFT client
cft = boto3.client('cloudformation')


with open("../parameters.json") as json_data:
    parameters_data = json.load(json_data)
    print(parameters_data)

@pytest.mark.parametrize('stackset_name', ['platform-Auto-Tag-StackSet'])
def test_aws_cft_check_if_stackset_exist(stackset_name):
    assert aws_cft_check_if_stackset_exist(cft, stackset_name) == True



@pytest.mark.parametrize('stackset_name', ['platform-Auto-Tag-StackSet'])
def test_aws_cft_check_stackset_status(stackset_name):
    assert aws_cft_check_if_stackset_exist(cft, stackset_name) == True