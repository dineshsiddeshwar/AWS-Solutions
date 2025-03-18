import boto3
import json
import pytest 
from TestCases.aws_s3_tests import *
s3_client = boto3.client('s3')


with open("../parameters.json") as json_data:
    parameters_data = json.load(json_data)
    print(parameters_data)

#test.mark.parametrize("account_id,policy",[(parameters_data['account_id'],parameters_data['IAM']['ListOfPlatformIAMPolicies'])])

@pytest.mark.parametrize('bucket_name', parameters_data['S3']['bucket_name'])
def test_aws_check_if_emr_block_public_enabled(bucket_name):
    account_id = parameters_data['account_id']
    assert aws_check_if_s3_block_public_enabled(s3_client,account_id,bucket_name) == True
