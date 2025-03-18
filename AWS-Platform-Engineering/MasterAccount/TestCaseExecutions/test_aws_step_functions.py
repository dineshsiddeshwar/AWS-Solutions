import boto3
import json
import pytest 
from TestCases.aws_step_functions_tests import *
# Create Athena client
stepfunctions_client = boto3.client('stepfunctions')

with open("../parameters.json") as json_data:
    parameters_data = json.load(json_data)
    print(parameters_data)

@pytest.mark.parametrize('sm_name', parameters_data['StepFunctions']['ListOfStateMachineNames'])
def test_aws_stepfunctions_check_if_state_machine_exist(sm_name):
    assert aws_stepfunctions_check_if_state_machine_exist(stepfunctions_client, sm_name) == True