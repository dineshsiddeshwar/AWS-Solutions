import boto3
import json
import pytest 
from TestCases.aws_s3_tests import *
# Create S3 client
s3_client = boto3.client('s3')

with open("../parameters.json") as json_data:
    parameters_data = json.load(json_data)
    print(parameters_data)

@pytest.mark.parametrize('bucket_name', parameters_data['S3']['ListOfBuckets'])
def test_aws_s3_check_if_bucket_exist(bucket_name):
    assert aws_s3_check_if_bucket_exist(s3_client, bucket_name) == True

@pytest.mark.parametrize('bucket_name', parameters_data['S3']['ListOfBucketsWithBlockPublicAccess'])
def test_aws_s3_check_if_bucket_is_having_public_access_block(bucket_name):
    assert aws_s3_check_if_bucket_is_having_public_access_block(s3_client, bucket_name) == True

@pytest.mark.parametrize('bucket_name', parameters_data['S3']['ListOfBucketsWithOwnershipControls'])
def test_aws_s3_check_if_bucket_is_having_ownership_controls(bucket_name):
    assert aws_s3_check_if_bucket_is_having_ownership_controls(s3_client, bucket_name) == True

@pytest.mark.parametrize('bucket_name', parameters_data['S3']['ListOfBucketsWithNotificationConfiguration'])
def test_aws_s3_check_if_bucket_is_having_notification_configuration(bucket_name):
    assert aws_s3_check_if_bucket_is_having_notification_configuration(s3_client, bucket_name) == True
