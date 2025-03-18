import boto3
import time
import datetime
import os
import random
def lambda_handler(event, context):
    # Get the VPC ID from the input event
    vpc_id = event['vpc_id']
    region = event['region']
    # Create a boto3 client for RDS
    rds_client = boto3.client('rds', region_name=region) 
    # Create a paginator for the describe_db_instances method
    paginator = rds_client.get_paginator('describe_db_instances')
    # Define the filters to get RDS instances in the specified VPC
    filters = [
        {'Name': 'vpc-id', 'Values': [vpc_id]}
    ]
    # Use the paginator to get all RDS instances matching the filters
    rds_instances = []
    for page in paginator.paginate(Filters=filters):
        rds_instances.extend(page['DBInstances'])
    # Return the list of RDS instances
    return rds_instances
