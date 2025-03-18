import boto3
import json
import pytest 
import os
from TestCases.aws_sso_tests import *

ParameterJsonPath = (os.getcwd()).replace("/TestExecutions", "/parameters.json")
print("AVM Parameters Json Path ", ParameterJsonPath)

with open(ParameterJsonPath) as json_data:
    parameters_data = json.load(json_data)
    print(parameters_data)

def test_aws_check_if_sso_permissionset_assigned_to_default_groups_irm():
    sso_client = boto3.client('sso-admin')
    assert aws_check_if_sso_permissionset_assigned_to_default_groups(sso_client, parameters_data['ProvisionedProduct']['AccountNumber'], parameters_data['SSMParameters']['sso_instance_arn'], parameters_data['SSMParameters']['irm_permission_set'], parameters_data['SSMParameters']['platform_irm_group']) == True

def test_aws_check_if_sso_permissionset_assigned_to_default_groups_platform():
    sso_client = boto3.client('sso-admin')
    assert aws_check_if_sso_permissionset_assigned_to_default_groups(sso_client, parameters_data['ProvisionedProduct']['AccountNumber'], parameters_data['SSMParameters']['sso_instance_arn'], parameters_data['SSMParameters']['platform_readonly_permission_set'],parameters_data['SSMParameters']['platform_readonly_group']) == True

def test_aws_check_if_sso_permissionset_assigned_to_default_groups_itom():
    sso_client = boto3.client('sso-admin')
    assert aws_check_if_sso_permissionset_assigned_to_default_groups(sso_client, parameters_data['ProvisionedProduct']['AccountNumber'], parameters_data['SSMParameters']['sso_instance_arn'], parameters_data['SSMParameters']['itom_readonly_permission_set'],parameters_data['SSMParameters']['itom_readonly_group']) == True