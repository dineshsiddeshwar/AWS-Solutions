import boto3
import json
import pytest 
from TestCases.aws_sns_tests import *
# Create SNS client
sns_client = boto3.client('sns')

with open("../parameters.json") as json_data:
    parameters_data = json.load(json_data)
    print(parameters_data)

@pytest.mark.parametrize('topic_name', parameters_data['SNS']['ListOfTopicNames'])
def test_aws_sns_check_if_topic_is_created(topic_name):
    assert aws_sns_check_if_topic_is_created(sns_client, topic_name, parameters_data['MasterAccount']['Id'])  == True

@pytest.mark.parametrize('topic_name', parameters_data['SNS']['ListOfSubscriptionNames'])
def test_aws_sns_check_if_subscription_is_created(topic_name):
    assert aws_sns_check_if_subscription_is_created(sns_client, topic_name, parameters_data['MasterAccount']['Id'])  == True