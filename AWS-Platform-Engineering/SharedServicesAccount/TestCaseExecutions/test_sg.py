import boto3
import json
import pytest 
from TestCases.aws_sg_tests import *

with open("../parameters.json") as json_data:
    parameters_data = json.load(json_data)
    aws_sg = parameters_data.get('aws_security_group', {})

#Testing if Shared VPC is created
@pytest.mark.parametrize('region', aws_sg)
def test_aws_check_if_sg_exists(region):
    client= boto3.client('ec2', region_name=region)
    assert aws_check_if_sg_exists(client, aws_sg[region]) == True