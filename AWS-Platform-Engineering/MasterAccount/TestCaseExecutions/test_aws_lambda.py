import boto3
import json
import pytest 
from TestCases.aws_lambda_tests import *
# Create Lambda client
lambda_client = boto3.client('lambda')

with open("../parameters.json") as json_data:
    parameters_data = json.load(json_data)
    print(parameters_data)

@pytest.mark.parametrize('function_name', parameters_data['Lambda']['ListOfLambdaFunctions'])
def test_aws_lambda_check_if_function_exist(function_name):
    assert aws_lambda_check_if_function_exist(lambda_client, function_name) == True

@pytest.mark.parametrize('function_name', parameters_data['Lambda']['ListOfLambdaFunctionPermissions'])   
def test_aws_lambda_check_if_lambda_permission_added(function_name):
    assert aws_lambda_check_if_lambda_permission_added(lambda_client, function_name) == True
    
@pytest.mark.parametrize('layer_name', parameters_data['Lambda']['ListOfLambdaLayerNames'])   
def test_aws_lambda_check_if_lambda_layer_is_created(layer_name):
    assert aws_lambda_check_if_lambda_layer_is_created(lambda_client, layer_name) == True

@pytest.mark.parametrize('function_name', parameters_data['Lambda']['ListOfLambdaWithEventSourceMapping'])   
def test_aws_lambda_check_if_event_source_mapping_is_created(function_name):
    assert aws_lambda_check_if_event_source_mapping_is_created(lambda_client, function_name) == True