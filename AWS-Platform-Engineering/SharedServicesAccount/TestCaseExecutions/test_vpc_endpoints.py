import boto3
import json
import pytest 
from TestCases.aws_vpc_endpoints_tests import *

regions = ['us-east-1','eu-west-1','ap-southeast-1']

with open("../parameters.json") as json_data:
    parameters_data = json.load(json_data)
    aws_vpce = parameters_data.get('aws_vpc_endpoint', {})
    aws_hosted_zone=parameters_data.get('aws_route53_zone', {})

#Testing if Shared VPC is created
@pytest.mark.parametrize('servicename', aws_vpce)
def test_aws_check_if_vpc_endpoint_exists(servicename):
    for region in regions:
        ec2_client= boto3.client('ec2', region_name=region)
        assert aws_check_if_vpc_endpoint_exists(ec2_client,region, servicename) == True
@pytest.mark.parametrize('servicename', aws_hosted_zone)
def test_aws_check_if_hosted_zone_exists(servicename):
    for region in regions:
        r53_client= boto3.client('route53', region_name=region)
        assert aws_check_if_hosted_zone_exists(r53_client,servicename,region) == True