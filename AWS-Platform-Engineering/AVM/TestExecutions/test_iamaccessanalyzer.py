import boto3
import json
import pytest 
import random
import os
from TestCases.aws_iamaccessanalyzer_tests import *

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
def test_aws_iam_check_if_analyzer_enabled(region):
    iamaccessanalyzer = assumeRoleSession.client('accessanalyzer', region_name=region)
    iamaccessanalyzer_name = "platform_analyzer_"+ region
    assert aws_iam_check_if_analyzer_enabled(iamaccessanalyzer, iamaccessanalyzer_name) == True