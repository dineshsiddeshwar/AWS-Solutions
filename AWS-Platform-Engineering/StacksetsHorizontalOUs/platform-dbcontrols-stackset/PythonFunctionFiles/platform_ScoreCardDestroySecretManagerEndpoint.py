import boto3
import os
import random
import time
from botocore.exceptions import ClientError
def lambda_handler(event, context):
    
    delay = random.uniform(1,200)
    time.sleep(delay)
    vpc_id = event["vpc_id"]
    tag_name = 'DCRScoreCard'
    tag_value = 'True'
    region = event["region"]

    ec2 = boto3.client('ec2', region_name = region)
    # Get all endpoints in the given VPC
    endpoints = ec2.describe_vpc_endpoints(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])['VpcEndpoints']
    # Filter endpoints with the specified tag
    print(endpoints)
    endpoints_to_delete = []
    for endpoint in endpoints:
        if 'Tags' in endpoint:
            for tag in endpoint['Tags']:
                if tag['Key'] == tag_name and tag['Value'] == tag_value:
                    endpoints_to_delete.append(endpoint['VpcEndpointId'])
                    break
    # Delete the endpoints
    for endpoint_id in endpoints_to_delete:
        ec2.delete_vpc_endpoints(VpcEndpointIds=[endpoint_id])
    # Create a Boto3 client for AWS Lambda
    lambda_client = boto3.client('lambda', region_name = region)
    # Update the Lambda function's VPC configuration
    response = lambda_client.update_function_configuration(
        FunctionName=os.environ['FUNCTION_NAME'],
        VpcConfig={
            'SubnetIds': [],
            'SecurityGroupIds': []
        }
    )
    time.sleep(60)  
    return {
        "message" : f"deleted {len(endpoints_to_delete)} endpoints"
    }