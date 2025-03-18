import boto3
import json
import pytest 
import random
import os
from TestCases.aws_securityhub_tests import *

ParameterJsonPath = (os.getcwd()).replace("/TestExecutions", "/parameters.json")
print("AVM Parameters Json Path ", ParameterJsonPath)

with open(ParameterJsonPath) as json_data:
    parameters_data = json.load(json_data)
    print(parameters_data)

account_number = str(parameters_data['ProvisionedProduct']['AccountNumber'])
secondaryRoleArn = "arn:aws:iam::{}:role/AWSControlTowerExecution".format(account_number)
secondarySessionName = "SecondarySession-" + str(random.randint(1, 100000))
session = boto3.session.Session()
sts_client = session.client('sts')
secondaryRoleCreds = sts_client.assume_role(RoleArn=secondaryRoleArn, RoleSessionName=secondarySessionName)
credentials = secondaryRoleCreds.get('Credentials')
accessKeyID = credentials.get('AccessKeyId')
secretAccessKey = credentials.get('SecretAccessKey')
sessionToken = credentials.get('SessionToken')
assumeRoleSession = boto3.session.Session(accessKeyID, secretAccessKey, sessionToken)

regions_str = parameters_data['SSMParameters']['whitelisted_regions_private'] if "Private" in parameters_data['ProvisionedProduct']['OU'] or "Hybrid" in parameters_data['ProvisionedProduct']['OU'] else parameters_data['SSMParameters']['whitelisted_regions_public']
regions = regions_str.split(',')
print("Regions allowed", regions)

@pytest.mark.parametrize('region', regions)
def test_aws_check_if_securityhub_insights_enabled(region):
    if region != "us-west-1":
        securityhub_client = assumeRoleSession.client('securityhub', region_name=region)
        assert aws_check_if_securityhub_insights_enabled(securityhub_client) == True

@pytest.mark.parametrize('region', regions)
def test_aws_check_if_securityhub_CIS_standards_control_Refined(region):
    if region != "us-west-1":
        securityhub_client = assumeRoleSession.client('securityhub', region_name=region)
        assert aws_check_if_securityhub_CIS_standards_control_Refined(securityhub_client,region, parameters_data['ProvisionedProduct']['AccountNumber'], "1.14") == True

@pytest.mark.parametrize('region', regions)
def test_aws_check_if_securityhub_AWS_standards_control_Refined_IAM(region):
    if region != "us-west-1":
        securityhub_client = assumeRoleSession.client('securityhub', region_name=region)
        assert aws_check_if_securityhub_AWS_standards_control_Refined(securityhub_client,region, parameters_data['ProvisionedProduct']['AccountNumber'], "IAM.6") == True

@pytest.mark.parametrize('region', regions)
def test_aws_check_if_securityhub_AWS_standards_control_Refined_ELB(region):
    if region != "us-west-1":
        securityhub_client = assumeRoleSession.client('securityhub', region_name=region)
        assert aws_check_if_securityhub_AWS_standards_control_Refined(securityhub_client,region, parameters_data['ProvisionedProduct']['AccountNumber'], "ELB.3") == True

@pytest.mark.parametrize('region', regions)
def test_aws_check_if_securityhub_AWS_standards_control_Refined_SSM(region):
    if region != "us-west-1":
        securityhub_client = assumeRoleSession.client('securityhub', region_name=region)
        assert aws_check_if_securityhub_AWS_standards_control_Refined(securityhub_client,region, parameters_data['ProvisionedProduct']['AccountNumber'], "SSM.1") == True