import boto3
import json
import pytest 
from TestCases.aws_dynamodb_tests import *
# Create DynamoDB client
dynamodb_client = boto3.client('dynamodb')

with open("../parameters.json") as json_data:
    parameters_data = json.load(json_data)
    print(parameters_data)

@pytest.mark.parametrize('table_name', parameters_data['DynamoDB']['ListOfTableNames'])
def test_aws_dynamodb_check_if_table_exist(table_name):
    assert aws_dynamodb_check_if_table_exist(dynamodb_client, table_name) == True