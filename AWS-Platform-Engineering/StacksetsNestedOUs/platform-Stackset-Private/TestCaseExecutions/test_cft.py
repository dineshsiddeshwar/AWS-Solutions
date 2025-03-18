import boto3
import pytest 
from TestCases.aws_cft_tests import *
# Create CFT client
cft = boto3.client('cloudformation')

@pytest.mark.parametrize('stackset_name', ['Nested-OU-Platform-Private'])
def test_aws_cft_check_if_stackset_exist(stackset_name):
    assert aws_cft_check_if_stackset_exist(cft, stackset_name) == True

@pytest.mark.parametrize('stackset_name', ['Nested-OU-Platform-Private'])
def test_aws_cft_check_stackset_status(stackset_name):
    assert aws_cft_check_if_stackset_exist(cft, stackset_name) == True