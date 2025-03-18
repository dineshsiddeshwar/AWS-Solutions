import boto3
import json
import pytest 
from TestCases.aws_organizations_tests import *
# Create IAM client
organizations = boto3.client('organizations')


with open("../parameters.json") as json_data:
    parameters_data = json.load(json_data)
    print(parameters_data)

@pytest.mark.parametrize('ou_id', parameters_data['NestedOUs']['ListOfOUs'])
def test_aws_organizations_check_if_ou_exist(ou_id):
    assert aws_organizations_check_if_ou_exist(organizations, ou_id) == True




