import boto3
import json
import pytest 
from TestCases.aws_backup_tests import *
# Create Backup client
backup_client = boto3.client('backup')

with open("../parameters.json") as json_data:
    parameters_data = json.load(json_data)
    print(parameters_data)

@pytest.mark.parametrize("plan", parameters_data['Backup']['ListOfBackupReportPlans'])
def test_aws_backup_check_if_report_plan_exist(plan):
    assert aws_backup_check_if_report_plan_exist(backup_client, plan) == True


