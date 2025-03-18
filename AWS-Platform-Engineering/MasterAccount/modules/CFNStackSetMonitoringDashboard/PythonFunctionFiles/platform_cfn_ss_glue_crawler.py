import os, boto3

#Create Glue client
glue_client = boto3.client('glue')

#The Glue crawler name is passed as a variable to the Lambda function
GLUE_CRAWLER_NAME = os.environ['GLUE_CRAWLER_NAME']

def lambda_handler(event, context):
    #Trigger the Glue crawler
    response = glue_client.start_crawler(Name=GLUE_CRAWLER_NAME)
    return response