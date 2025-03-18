import boto3
import pytest
import json
from TestCases.aws_SCP_test import *

with open("../parameters.json") as json_data:
    parameters_data = json.load(json_data)
    print(parameters_data)

organizations_client = boto3.client('organizations')

list = [(k, v) for k, v in parameters_data['OU_NAMES_AND_SCP_NAMES'].items()]      
print(list)
@pytest.mark.parametrize('ou_id, ou_scp_details', list)
def test_aws_scp_is_created_and_attached(ou_id, ou_scp_details):
    assert aws_organizations_check_if_scp_is_created_and_attached(organizations_client, ou_id, ou_scp_details) == True

