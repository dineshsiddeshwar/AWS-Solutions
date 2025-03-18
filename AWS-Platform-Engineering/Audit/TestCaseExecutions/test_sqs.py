import boto3
import json
import pytest 
from TestCases.aws_sqs_tests import *
# Create Lambda client
sqs_client = boto3.client('sqs',region_name='us-east-1')

with open("../parameters.json") as json_data:
    parameters_data = json.load(json_data)
    print(parameters_data)




@pytest.mark.parametrize('queue_name', parameters_data['sqs']['queue_name'])
def test_aws_lambda_check_if_function_exist(queue_name):
    account_id = parameters_data['account_id']
    assert aws_sqs_check_if_queue_exist(sqs_client, queue_name, account_id) == True
