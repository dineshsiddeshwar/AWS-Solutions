import boto3
import json
import pytest 
from TestCases.aws_api_gateway_tests import *
# Create Athena client
apigateway_client = boto3.client('apigateway')

with open("../parameters.json") as json_data:
    parameters_data = json.load(json_data)
    print(parameters_data)

@pytest.mark.parametrize('api_key_name', parameters_data['APIGateway']['ListOfAPIKeys'])
def test_aws_apigateway_check_if_rest_api_key_exist(api_key_name):
    assert aws_apigateway_check_if_rest_api_key_exist(apigateway_client, api_key_name) == True

@pytest.mark.parametrize('rest_api_name', parameters_data['APIGateway']['ListOfRestAPINames'])
def test_aws_apigateway_check_if_rest_api_exist(rest_api_name):
    assert aws_apigateway_check_if_rest_api_exist(apigateway_client, rest_api_name) == True

@pytest.mark.parametrize('plan_name', parameters_data['APIGateway']['ListOfUsagePlanNames'])
def test_aws_apigateway_check_if_usage_plan_exist(plan_name):
    assert aws_apigateway_check_if_usage_plan_exist(apigateway_client, plan_name) == True

@pytest.mark.parametrize('plan_name', parameters_data['APIGateway']['ListOfUsagePlanNames'])
def test_aws_apigateway_check_if_usage_plan_key_exist(plan_name):
    assert aws_apigateway_check_if_usage_plan_key_exist(apigateway_client, plan_name) == True

@pytest.mark.parametrize('rest_api_name', parameters_data['APIGateway']['ListOfRestAPINames'])
def test_aws_apigateway_check_if_deployment_exist(rest_api_name):
    assert aws_apigateway_check_if_deployment_exist(apigateway_client, rest_api_name) == True

@pytest.mark.parametrize('rest_api_name', parameters_data['APIGateway']['ListOfRestAPINames'])
def test_aws_apigateway_check_if_stage_exist(rest_api_name):
    assert aws_apigateway_check_if_stage_exist(apigateway_client, rest_api_name) == True

@pytest.mark.parametrize('rest_api_name', parameters_data['APIGateway']['ListOfRestAPINames'])
def test_aws_apigateway_check_if_resource_exist(rest_api_name):
    assert aws_apigateway_check_if_resource_exist(apigateway_client, rest_api_name) == True

@pytest.mark.parametrize('rest_api_name', parameters_data['APIGateway']['ListOfAPIsWithAuthorizers'])
def test_aws_apigateway_check_if_authorizer_exist(rest_api_name):
    assert aws_apigateway_check_if_authorizer_exist(apigateway_client, rest_api_name) == True

@pytest.mark.parametrize("rest_api_name", parameters_data['APIGateway']['ListOfRestAPINamesWithMethods'])
@pytest.mark.parametrize("http_name", parameters_data['APIGateway']['ListOfMethodNames'])
def test_aws_apigateway_check_if_method_exist(rest_api_name,http_name):
    assert aws_apigateway_check_if_method_exist(apigateway_client, rest_api_name, http_name) == True

@pytest.mark.parametrize("rest_api_name", parameters_data['APIGateway']['ListOfRestAPINamesWithMethods'])
@pytest.mark.parametrize("http_name", parameters_data['APIGateway']['ListOfMethodNames'])
def test_aws_apigateway_check_if_method_response_exist(rest_api_name,http_name):
    assert aws_apigateway_check_if_method_response_exist(apigateway_client, rest_api_name, http_name) == True

@pytest.mark.parametrize("rest_api_name", parameters_data['APIGateway']['ListOfRestAPINamesWithMethods'])
@pytest.mark.parametrize("http_name", parameters_data['APIGateway']['ListOfMethodNames'])
def test_aws_apigateway_check_if_integration_exist(rest_api_name,http_name):
    assert aws_apigateway_check_if_integration_exist(apigateway_client, rest_api_name, http_name) == True

@pytest.mark.parametrize("rest_api_name", parameters_data['APIGateway']['ListOfRestAPINamesWithMethods'])
@pytest.mark.parametrize("http_name", parameters_data['APIGateway']['ListOfMethodNames'])
def test_aws_apigateway_check_if_integration_response_exist(rest_api_name,http_name):
    assert aws_apigateway_check_if_integration_response_exist(apigateway_client, rest_api_name, http_name) == True
