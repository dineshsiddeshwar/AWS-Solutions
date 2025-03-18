import boto3
import json
import pytest 
from TestCases.aws_vpc_tests import *
# Create EC2 client
ec2_client = boto3.client('ec2')

with open("../parameters.json") as json_data:
    parameters_data = json.load(json_data)
    print(parameters_data)

@pytest.mark.parametrize('vpc_name', parameters_data['VPC']['ListOfVPCNames'])
def test_aws_check_if_vpc_is_created(vpc_name):
    assert aws_check_if_vpc_is_created(ec2_client, vpc_name) == True

@pytest.mark.parametrize('vpc_name', parameters_data['VPC']['ListOfVPCNames'])
def test_aws_check_if_internet_gateway_is_created(vpc_name):
    assert aws_check_if_internet_gateway_is_created(ec2_client, vpc_name) == True

@pytest.mark.parametrize('vpc_name', parameters_data['VPC']['ListOfVPCNames'])
def test_aws_check_if_subnets_are_created(vpc_name):
    assert aws_check_if_subnets_are_created(ec2_client, vpc_name) == True

@pytest.mark.parametrize('vpc_name', parameters_data['VPC']['ListOfVPCNames'])
def test_aws_check_if_routetable_created(vpc_name):
    assert aws_check_if_routetable_created(ec2_client, vpc_name) == True

@pytest.mark.parametrize('vpc_name', parameters_data['VPC']['ListOfVPCNames'])
def test_aws_check_if_routetable_is_associated(vpc_name):
    assert aws_check_if_routetable_is_associated(ec2_client, vpc_name) == True

@pytest.mark.parametrize('vpc_name', parameters_data['VPC']['ListOfVPCNames'])
def test_aws_check_if_flowlogs_is_enabled(vpc_name):
    assert aws_check_if_flowlogs_is_enabled(ec2_client, vpc_name) == True

@pytest.mark.parametrize('sg_name', parameters_data['VPC']['ListOfSecurityGroupNames'])
def test_aws_check_if_security_group_is_created(sg_name):
    assert aws_check_if_security_group_is_created(ec2_client, sg_name) == True

@pytest.mark.parametrize('elastic_ip_name', parameters_data['VPC']['ListOfElasticIPNames'])
def test_aws_check_if_elatic_ip_is_associated(elastic_ip_name):
    assert aws_check_if_elatic_ip_is_associated(ec2_client, elastic_ip_name) == True

@pytest.mark.parametrize('nat_gateway_name', parameters_data['VPC']['ListOfNatGateWayNames'])
def test_aws_check_if_nat_gateway_is_created(nat_gateway_name):
    assert aws_check_if_nat_gateway_is_created(ec2_client, nat_gateway_name) == True
