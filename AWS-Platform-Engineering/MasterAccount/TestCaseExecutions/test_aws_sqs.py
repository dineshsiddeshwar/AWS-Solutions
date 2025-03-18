import boto3
import json
import pytest 
from TestCases.aws_sqs_tests import *
# Create SQS client
sqs_client = boto3.client('sqs')

with open("../parameters.json") as json_data:
    parameters_data = json.load(json_data)
    print(parameters_data)

@pytest.mark.parametrize('queue_name', parameters_data['SQS']['ListOfQueueNames'])
def test_aws_sqs_check_if_queue_is_created(queue_name):
    assert aws_sqs_check_if_queue_is_created(sqs_client, queue_name)  == True
