import boto3
import json
import pytest 
from TestCases.aws_sso_tests import *
# Create sso-admin client
ssoadmin = boto3.client('sso-admin')


with open("../parameters.json") as json_data:
    parameters_data = json.load(json_data)
    print(parameters_data)

@pytest.mark.parametrize('permission_set_arn', parameters_data['PermissionSets']['ListOfPermissionSetsArn'])
@pytest.mark.parametrize('instance_arn', parameters_data['PermissionSets']['instance_arn'])
def test_aws_sso_check_if_permission_set_exist(permission_set_arn,instance_arn):
    assert aws_sso_check_if_permission_set_exist(ssoadmin, permission_set_arn, instance_arn) == True


    




