import boto3
import json
import pytest 
from TestCases.aws_athena_query_tests import *
# Create Athena client
athena_client = boto3.client('athena')

with open("../parameters.json") as json_data:
    parameters_data = json.load(json_data)
    print(parameters_data)

@pytest.mark.parametrize('query_name', parameters_data['Athena']['ListOfAthenaNamedQueries'])
def test_aws_athena_check_if_named_query_exist(query_name):
    assert aws_athena_check_if_named_query_exist(athena_client, query_name) == True