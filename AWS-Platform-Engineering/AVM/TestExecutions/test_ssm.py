import boto3
import json
import pytest 
import random
import os
from TestCases.aws_ssm_tests import *

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
def test_aws_check_if_ssm_associations_created_djl(region):
    if "Private" in parameters_data['ProvisionedProduct']['OU'] or "Hybrid" in parameters_data['ProvisionedProduct']['OU']:
        ssm_client = assumeRoleSession.client('ssm', region_name=region)
        assert aws_check_if_ssm_associations_created(ssm_client, "platform-Domainjoinmain-Linux") == True

@pytest.mark.parametrize('region', regions)
def test_aws_check_if_ssm_associations_created_djw(region):
    if "Private" in parameters_data['ProvisionedProduct']['OU'] or "Hybrid" in parameters_data['ProvisionedProduct']['OU']:
        ssm_client = assumeRoleSession.client('ssm', region_name=region)
        assert aws_check_if_ssm_associations_created(ssm_client, "platform-Domainjoinmain-Windows") == True

@pytest.mark.parametrize('region', regions)
def test_aws_check_if_ssm_associations_created_djaws(region):
    if ("Private" in parameters_data['ProvisionedProduct']['OU'] or "Hybrid" in parameters_data['ProvisionedProduct']['OU']) and (parameters_data['RequestEventData']['IsRESPCAccount'] == 'Yes'):
        ssm_client = assumeRoleSession.client('ssm', region_name=region)
        assert aws_check_if_ssm_associations_created(ssm_client, "platform-AWS-managed-AD-domainjoin") == True

@pytest.mark.parametrize('region', regions)
def test_aws_check_if_ssm_associations_created_chl(region):
    ssm_client = assumeRoleSession.client('ssm', region_name=region)
    assert aws_check_if_ssm_associations_created(ssm_client, "platform_InstallCloudhealthagent-Linux") == True

@pytest.mark.parametrize('region', regions)
def test_aws_check_if_ssm_associations_created_chw(region):
    ssm_client = assumeRoleSession.client('ssm', region_name=region)
    assert aws_check_if_ssm_associations_created(ssm_client, "platform_InstallCloudhealthagent-Windows") == True

@pytest.mark.parametrize('region', regions)
def test_aws_check_if_ssm_associations_created_cwl(region):
    ssm_client = assumeRoleSession.client('ssm', region_name=region)
    assert aws_check_if_ssm_associations_created(ssm_client, "platform_AmazonCloudWatch-Linux") == True

@pytest.mark.parametrize('region', regions)
def test_aws_check_if_ssm_associations_created_cww(region):
    ssm_client = assumeRoleSession.client('ssm', region_name=region)
    assert aws_check_if_ssm_associations_created(ssm_client, "platform_AmazonCloudWatch-windows") == True

@pytest.mark.parametrize('region', regions)
def test_aws_check_if_ssm_associations_created_fl(region):
    ssm_client = assumeRoleSession.client('ssm', region_name=region)
    assert aws_check_if_ssm_associations_created(ssm_client, "platform_InstallFlexeraAgent-Linux") == True

@pytest.mark.parametrize('region', regions)
def test_aws_check_if_ssm_associations_created_fw(region):
    ssm_client = assumeRoleSession.client('ssm', region_name=region)
    assert aws_check_if_ssm_associations_created(ssm_client, "platform_InstallFlexeraAgent-Windows") == True

@pytest.mark.parametrize('region', regions)
def test_aws_check_if_ssm_associations_created_crl(region):
    ssm_client = assumeRoleSession.client('ssm', region_name=region)
    assert aws_check_if_ssm_associations_created(ssm_client, "platform_InstallFalconAgent-Linux") == True

@pytest.mark.parametrize('region', regions)
def test_aws_check_if_ssm_associations_created_crw(region):
    ssm_client = assumeRoleSession.client('ssm', region_name=region)
    assert aws_check_if_ssm_associations_created(ssm_client, "platform_InstallFalconAgent-Windows") == True

@pytest.mark.parametrize('region', regions)
def test_aws_check_if_ssm_associations_created_rl(region):
    ssm_client = assumeRoleSession.client('ssm', region_name=region)
    assert aws_check_if_ssm_associations_created(ssm_client, "platform_InstallRapid7agent-Linux") == True

@pytest.mark.parametrize('region', regions)
def test_aws_check_if_ssm_associations_created_rw(region):
    ssm_client = assumeRoleSession.client('ssm', region_name=region)
    assert aws_check_if_ssm_associations_created(ssm_client, "platform_InstallRapid7agent-Windows") == True

@pytest.mark.parametrize('region', regions)
def test_aws_check_if_ssm_associations_created_ssm(region):
    ssm_client = assumeRoleSession.client('ssm', region_name=region)
    assert aws_check_if_ssm_associations_created(ssm_client, "platform_update_ssm_agent") == True


@pytest.mark.parametrize('region', regions)
def test_aws_check_if_ssm_associations_created_ssm(region):
    ssm_client = assumeRoleSession.client('ssm', region_name=region)
    assert aws_check_if_ssm_associations_created(ssm_client, "platform_Linux_association") == True

@pytest.mark.parametrize('region', regions)
def test_aws_check_if_ssm_associations_created_ssm(region):
    ssm_client = assumeRoleSession.client('ssm', region_name=region)
    assert aws_check_if_ssm_associations_created(ssm_client, "platform_Windows_association") == True

ssm_parameters_list = ['/Platform-Tag/platform_STC', '/Platform-Tag/platform_LOB', '/Platform-Tag/platform_IsRESPCAccount', '/Platform-Tag/platform_Apexid', '/Platform-Tag/platform_RequestNo', '/Platform-Tag/platform_Custodian', '/Platform-Tag/platform_DL', '/Platform-Tag/platform_AccountType', '/Platform-Tag/platform_WhitelistedRegions', '/Platform-Tag/platform_Tenancy', '/Platform-Tag/platform_DataClassification', '/Platform-Tag/platform_BIA', '/Platform-Tag/platform_SOX', '/Platform-Backup-Tag/platform_Backup', 'platform_ami_owner_account',  'platform_ami_owner_account', 'platform_TOE_Complaint_OS_list', 'platform_whitelisted_regions', 'platform_account_type']
@pytest.mark.parametrize('ssm_parameter', ssm_parameters_list)
def test_aws_check_if_ssm_parameters_exists(ssm_parameter):
    ssm_client = assumeRoleSession.client('ssm', region_name='us-east-1')
    assert aws_check_if_ssm_parameters_exists(ssm_client, ssm_parameter) == True