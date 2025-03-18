import boto3
import json
import pytest 
from TestCases.aws_lambda_tests import *
# Create Lambda client
lambda_client = boto3.client('lambda',region_name='us-east-1')

with open("../parameters.json") as json_data:
    parameters_data = json.load(json_data)
    print(parameters_data)


@pytest.mark.parametrize('function_name', parameters_data['Lambda']['function_name'])
def test_aws_lambda_check_if_function_exist(function_name):
    assert aws_lambda_check_if_function_exist(lambda_client, function_name) == True