import boto3
import json
import pytest 
from TestCases.aws_ram_tests import *

regions = ['us-east-1','eu-west-1','ap-southeast-1']

with open("../parameters.json") as json_data:
    parameters_data = json.load(json_data)
    aws_ram_principal_association = parameters_data.get('aws_ram_principal_association', {})

#Testing if RAM resource share principals exists
@pytest.mark.parametrize('principal', aws_ram_principal_association)
def test_aws_check_if_ram_resource_share_principals_exists(principal):
    for region in regions:
        ram_client= boto3.client('ram', region_name=region)
        assert aws_check_if_ram_resource_share_principals_exists(ram_client,aws_ram_principal_association[principal]) == True

#Testing if RAM resource share exists
def test_aws_check_if_ram_resource_share_exists():
    for region in regions:
        ram_client= boto3.client('ram', region_name=region)
        assert aws_check_if_ram_resource_share_exists(ram_client) == True

#Testing if RAM resource association with resolver rule exists
def test_aws_check_if_ram_resource_association_exists():
    for region in regions:
        ram_client= boto3.client('ram', region_name=region)
        assert aws_check_if_ram_resource_association_exists(ram_client) == True
