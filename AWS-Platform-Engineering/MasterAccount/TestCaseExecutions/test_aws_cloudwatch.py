import boto3
import json
import pytest 
from TestCases.aws_cloudwatch_tests import *
# Create CloudWatch Logs client
logs_client = boto3.client('logs')
cloudwatch_client = boto3.client('cloudwatch')

with open("../parameters.json") as json_data:
    parameters_data = json.load(json_data)
    print(parameters_data)

@pytest.mark.parametrize("filter_name", parameters_data['CloudWatch']['ListOfMetricFilterNames'])
def test_aws_cw_logs_check_if_metric_filter_is_created(filter_name):    
    assert aws_cw_logs_check_if_metric_filter_is_created(logs_client, filter_name) == True

@pytest.mark.parametrize("alarm_name", parameters_data['CloudWatch']['ListOfAlarmNames'])
def test_aws_cw_check_if_alarm_is_created(alarm_name):    
    assert aws_cw_check_if_alarm_is_created(cloudwatch_client, alarm_name) == True

@pytest.mark.parametrize("log_group_name", parameters_data['CloudWatch']['ListOfLogGroupNames'])
def test_aws_cw_check_if_log_group_is_created(log_group_name):    
    assert aws_cw_check_if_log_group_is_created(logs_client, log_group_name) == True