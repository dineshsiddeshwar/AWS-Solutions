import boto3
import json
import pytest 
from TestCases.aws_r53_tests import *

regions = ['us-east-1','eu-west-1','ap-southeast-1']

#Testing if Resolver Endpoint Exists
def test_aws_check_if_resolver_endpoint_exists():
    for region in regions:
        r53_client= boto3.client('route53resolver', region_name=region)
        assert aws_check_if_resolver_endpoint_exists(r53_client) == True
#Testing if Resolver Rule Exists
def test_aws_check_if_resolver_rule_exists():
    for region in regions:
        r53_client= boto3.client('route53resolver', region_name=region)
        assert aws_check_if_resolver_rule_exists(r53_client) == True
#Testing if Resolver Rule Association Exists
def test_aws_check_if_resolver_rule_associations_exists():
    for region in regions:
        r53_client= boto3.client('route53resolver', region_name=region)
        assert aws_check_if_resolver_rule_associations_exists(r53_client) == True
