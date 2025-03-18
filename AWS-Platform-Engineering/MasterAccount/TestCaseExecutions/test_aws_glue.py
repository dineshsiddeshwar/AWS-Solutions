import boto3
import json
import pytest 
from TestCases.aws_glue_tests import *
# Create Glue client
glue_client = boto3.client('glue')

with open("../parameters.json") as json_data:
    parameters_data = json.load(json_data)
    print(parameters_data)

@pytest.mark.parametrize('db_name', parameters_data['Glue']['ListOfGlueDatabaseNames'])
def test_aws_glue_check_if_database_exist(db_name):
    assert aws_glue_check_if_database_exist(glue_client, db_name) == True

@pytest.mark.parametrize('crawler_name', parameters_data['Glue']['ListOfGlueCrawlerNames'])
def test_aws_glue_check_if_crawler_exist(crawler_name):
    assert aws_glue_check_if_crawler_exist(glue_client, crawler_name) == True

@pytest.mark.parametrize('classifier_name', parameters_data['Glue']['ListOfGlueClassifierNames'])
def test_aws_glue_check_if_classifier_exist(classifier_name):
    assert aws_glue_check_if_classifier_exist(glue_client, classifier_name) == True