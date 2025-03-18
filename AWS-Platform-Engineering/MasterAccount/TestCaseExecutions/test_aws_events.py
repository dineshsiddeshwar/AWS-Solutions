import boto3
import json
import pytest 
from TestCases.aws_events_tests import *
# Create IAM client
events_client = boto3.client('events')
scheduler_client = boto3.client('scheduler')

with open("../parameters.json") as json_data:
    parameters_data = json.load(json_data)
    print(parameters_data)

@pytest.mark.parametrize("rule", parameters_data['Events']['ListOfEventRules'])
def test_aws_events_check_if_rule_exist(rule):
    assert aws_events_check_if_rule_exist(events_client, rule) == True

@pytest.mark.parametrize("rule", parameters_data['Events']['ListOfEventRules'])
def test_aws_events_check_if_target_exist(rule):
    assert aws_events_check_if_target_exist(events_client, rule) == True

dict = parameters_data['Events']['ListOfEventSchedules']
list = [(k, v) for k, v in dict.items()]
@pytest.mark.parametrize("group ,schedulename", list)
def test_aws_events_check_if_scheduler_exist(group,schedulename):
    assert aws_events_check_if_scheduler_exist(scheduler_client, group,schedulename) == True

@pytest.mark.parametrize("bus", parameters_data['Events']['ListOfEventBus'])
def test_aws_events_check_if_bus_exist(bus):
    assert aws_events_check_if_bus_exist(events_client, bus) == True

@pytest.mark.parametrize("bus", parameters_data['Events']['ListOfEventBusPolicy'])
def test_aws_events_check_if_bus_policy_exist(bus):
    assert aws_events_check_if_bus_policy_exist(events_client, bus) == True

