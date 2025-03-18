import boto3
import json
import pytest 
from TestCases.aws_service_catalog_tests import *
# Create Service Catalog client
servicecatalog_client = boto3.client('servicecatalog')

with open("../parameters.json") as json_data:
    parameters_data = json.load(json_data)
    print(parameters_data)

@pytest.mark.parametrize('product_name', parameters_data['ServiceCatalog']['ListOfProductNames'])
def test_aws_servicecatalog_check_if_product_exist(product_name):
    assert aws_servicecatalog_check_if_product_exist(servicecatalog_client, product_name) == True

@pytest.mark.parametrize('portfolio_name', parameters_data['ServiceCatalog']['ListOfProductPortfolioNames'])
def test_aws_servicecatalog_check_if_product_portfolio_exist(portfolio_name):
    assert aws_servicecatalog_check_if_product_portfolio_exist(servicecatalog_client, portfolio_name) == True

@pytest.mark.parametrize('product_name', parameters_data['ServiceCatalog']['ListOfProductNames'])
def test_aws_servicecatalog_check_if_product_portfolio_associated(product_name):
    assert aws_servicecatalog_check_if_product_portfolio_associated(servicecatalog_client, product_name) == True

@pytest.mark.parametrize('portfolio_name', parameters_data['ServiceCatalog']['ListOfProductPortfolioNames'])
def test_aws_servicecatalog_check_if_principal_portfolio_associated(portfolio_name):
    assert aws_servicecatalog_check_if_principal_portfolio_associated(servicecatalog_client, portfolio_name) == True
