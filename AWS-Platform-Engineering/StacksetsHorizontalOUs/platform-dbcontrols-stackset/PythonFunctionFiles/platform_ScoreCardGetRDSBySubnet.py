import boto3
import time
import datetime
import random
import os
import json
from botocore.exceptions import ClientError


def lambda_handler(event, context):
    # Get the AWS region from the environment variable
    region = event["region"]
    # Get the VPC ID from the event
    vpc_id = event["vpc_id"]
    
    rds_instances_input = event["rds_instances"]


    event_subnet_id = event["subnet_id"]

    endpoint_ip = event["endpoint_ip"]
    endpoint_id = event["endpoint_id"]

    # Initialize the AWS RDS client
    rds = boto3.client('rds', region_name=region)
    ec2 = boto3.client('ec2', region_name=region)

    lambda_client = boto3.client('lambda', region_name=region)

    # Create a paginator for the describe_db_instances function
    paginator = rds.get_paginator('describe_db_instances')

    # Create an empty list to store the RDS instances
    vpc_rds_instances = []

    # get the security group of the Lambda function
    lambda_client = boto3.client('lambda', region_name=region)

    response = lambda_client.get_function_configuration(FunctionName=os.environ['FUNCTION_NAME'])
    lambda_security_group_id = response['VpcConfig']['SecurityGroupIds'][0]

    # lambda_security_group_id = ''
    # for key in response['Configuration'].keys():
    #     if key == 'VpcConfig':    
    #         lambda_security_group_id = response['VpcConfig']['SecurityGroupIds'][0]

    paginator = rds.get_paginator('describe_db_instances')
    response_iterator = paginator.paginate()
    for response in response_iterator:
        rds_instances = response['DBInstances']
        for instance in rds_instances:
            rds_vpc_id = instance['DBSubnetGroup']['VpcId']
            instance_name = instance['DBInstanceIdentifier']

            if vpc_id == rds_vpc_id and instance_name in rds_instances_input:
                # Extract the endpoint URL and port from the instance
                endpoint = instance['Endpoint']
                url = endpoint['Address']
                port = endpoint['Port']
                # Add the endpoint URL and port to the list of RDS instances
                vpc_rds_instances.append((instance_name, url, port))

                rds_security_groups = instance['VpcSecurityGroups']
                rds_security_group = instance['VpcSecurityGroups'][0]['VpcSecurityGroupId']
                print(rds_security_groups)

                try:
                    response = ec2.authorize_security_group_ingress(
                        GroupId=rds_security_group,
                        IpPermissions=[
                            {
                                'FromPort': port,
                                'ToPort': port,
                                'IpProtocol': 'TCP',
                                'UserIdGroupPairs': [{'GroupId': lambda_security_group_id}]
                            }
                        ]
                    )
                    print('Inbound rule added successfully')
                except ClientError as e:
                    if 'Duplicate' in str(e):
                        print('Inbound rule already exists')
                    else:
                        raise e

    for instance in vpc_rds_instances:
        print(instance)

    inputPayload = {
        "invocationType": "precheck_sockets",
        "rds_list": vpc_rds_instances
    }
    functionName = os.environ['FUNCTION_NAME']
    response = lambda_client.invoke(
        FunctionName=functionName,
        Payload=json.dumps(inputPayload)
    )

    responsePayload = response['Payload'].read()
    response_arr = json.loads(responsePayload)

    if 'errorMessage' in response_arr:
        raise Exception(response_arr['errorMessage'])

    reachable = response_arr["reachable"]
    unreachable = response_arr["unreachable"]

    rds = boto3.client('rds', region_name=region)
    connectable_instances = []
    non_connectable_instances = {}
    for instance in reachable:
        try:
            rds.describe_db_instances(DBInstanceIdentifier=instance)
            connectable_instances.append(
                {"instance_name": instance, "endpoint_ip": endpoint_ip, "endpoint_id": endpoint_id,"region":region})
        except:
            response = rds.describe_db_instances(DBInstanceIdentifier=instance)
            instance_subnet = response['DBInstances'][0]['DBSubnetGroup']['VpcId']
            if instance_subnet not in non_connectable_instances:
                non_connectable_instances[instance_subnet] = []
            non_connectable_instances[instance_subnet].append(
                {"instance_name": instance, "endpoint_ip": endpoint_ip, "endpoint_id": endpoint_id})
    result = []
    for subnet_id in set(list(non_connectable_instances.keys()) + [event_subnet_id]):
        subnet_instances = {}
        subnet_instances['subnet_id'] = subnet_id
        subnet_instances['region'] = region

        subnet_instances['rds_instances'] = []
        if subnet_id == event_subnet_id:
            subnet_instances['rds_instances'] = connectable_instances
        elif subnet_id in non_connectable_instances:
            subnet_instances['rds_instances'] = non_connectable_instances[subnet_id]
        result.append(subnet_instances)

    return result
