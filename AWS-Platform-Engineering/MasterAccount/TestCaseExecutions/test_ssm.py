import boto3
import json
import pytest 
from TestCases.aws_ssm_tests import *
# Create SSM client
ssm_client = boto3.client('ssm')

with open("../parameters.json") as json_data:
    parameters_data = json.load(json_data)
    print(parameters_data)

@pytest.mark.parametrize('parameter', parameters_data['SSM']['ListOfParameters'])
def test_aws_ssm_check_if_paraeter_is_created(parameter):
    assert aws_ssm_check_if_paraeter_is_created(ssm_client, parameter) == True
