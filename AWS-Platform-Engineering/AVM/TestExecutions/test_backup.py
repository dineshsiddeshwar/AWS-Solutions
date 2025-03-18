import boto3
import json
import pytest 
import random
import os
from TestCases.aws_backup_tests import *

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
def test_aws_check_if_backup_vault_created(region):
    backup = assumeRoleSession.client('backup', region_name=region)
    assert aws_check_if_backup_vault_created(backup, "platform_backupvault") == True

@pytest.mark.parametrize('region', regions)
def test_aws_check_if_backup_sns_topic_created(region):
    snsclient = assumeRoleSession.client('sns', region_name=region)
    assert aws_check_if_backup_sns_topic_created(snsclient,region,parameters_data['ProvisionedProduct']['AccountNumber'], "platform_back_up_topic") == True

@pytest.mark.parametrize('region', regions)
def test_aws_check_if_backup_vault_notifications_created(region):
    backup = assumeRoleSession.client('backup', region_name=region)
    assert aws_check_if_backup_vault_notifications_created(backup,"platform_backupvault") == True