import boto3
import json
import pytest 
from TestCases.aws_vpc_tests import *

with open("../parameters.json") as json_data:
    parameters_data = json.load(json_data)
    aws_vpc = parameters_data.get('aws_vpc', {})
    aws_subnet = parameters_data.get('aws_subnet', {})

#Testing if Shared VPC is created
@pytest.mark.parametrize('region', aws_vpc)
def test_aws_check_if_vpc_exists(region):
    client= boto3.client('ec2', region_name=region)
    assert aws_check_if_vpc_exists(client, aws_vpc[region][0]) == True

#Testing if Shared VPC Subnets are created
@pytest.mark.parametrize('region', aws_subnet)

def test_aws_check_if_subnet_exists(region):
    client= boto3.client('ec2', region_name=region)
    print("Checking for Subnet Region - ", region)
    for i in aws_subnet[region]:
        print("Checking for Subnet - ", i)
        assert aws_check_if_subnet_exists(client, aws_subnet[region][i]) == True

#Testing if Shared VPC Flowlogs are created
@pytest.mark.parametrize('region', aws_vpc)
def test_aws_check_if_flowlog_exists(region):
    client= boto3.client('ec2', region_name=region)
    assert aws_check_if_flowlog_created(client) == True