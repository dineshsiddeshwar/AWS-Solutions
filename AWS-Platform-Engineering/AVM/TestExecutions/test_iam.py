import boto3
import json
import pytest
import random
import os
from TestCases.aws_iam_tests import *


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

iam = assumeRoleSession.client('iam')

ListOfPlatformIAMRoles = ['platform_service_cloudhealth','platform_service_inflation', 'platform_service_instance', 'platform_service_readonly', 'platform_backup', 'ServiceNow_ITOM_Discovery_Child_Role', 'platform_SnowOrganizationAccountAccessRole', 'Platform_Flexera_AwsConnect_Role']
@pytest.mark.parametrize('role', ListOfPlatformIAMRoles)
def test_aws_iam_check_if_role_exist(role):
    assert aws_iam_check_if_role_exist(iam, role) == True

def test_aws_iam_check_if_instance_profile_exist():
    assert aws_iam_check_if_instance_profile_exist(iam, "platform_service_instance") == True

def test_aws_iam_check_if_IOTRole_role_exist():
    assert aws_iam_check_if_IOTRole_role_exist(iam, parameters_data['RequestEventData']['IsIOTAccount'], "business_cdf-execution-role") == True

ListOfPlatformIAMPolicies = ['platform_cloud_health_policy', 'platform_inflation_policy', 'platform_inflation_policy_2', 'platform_iam_pass_role_policy', 'platform_sts_full_access', 'platform_ec2instance_policy', 'ServiceNow_ITOM_Discovery_Child_Policy']
@pytest.mark.parametrize('policy', ListOfPlatformIAMPolicies)
def test_aws_iam_check_if_policy_exist(policy):
    assert aws_iam_check_if_policy_exist(iam, parameters_data['ProvisionedProduct']['AccountNumber'], policy) == True


