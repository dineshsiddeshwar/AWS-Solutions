import boto3
import json

class RDSNotAvailableError(Exception):
    pass

def lambda_handler(event, context):
    region = event["region"]
    rds_client = boto3.client('rds',region_name=region)
    if "rds_instance_name" in event:
        rds_instance_name = event["rds_instance_name"]
        db_instance = rds_client.describe_db_instances(DBInstanceIdentifier=rds_instance_name)['DBInstances'][0]
        vpc_id = db_instance['DBSubnetGroup']['VpcId']
        db_instance_status = db_instance['DBInstanceStatus']
        if db_instance_status == 'available':
            return [{
                'vpc_id': vpc_id,
                'region': region,
                'rds_instances': [rds_instance_name]
            }]
        else:
            db_name = db_instance['DBInstanceIdentifier']
            raise RDSNotAvailableError(f"{rds_instance_name} current status is {db_instance_status}. {rds_instance_name} must be available to continue. Try again once available.")
    # create dictionary to hold VPC ID and RDS instance names
    vpc_dict = {}
    # get all RDS instances
    paginator = rds_client.get_paginator('describe_db_instances')
    response_iterator = paginator.paginate()
    lambda_client = boto3.client('lambda',region_name = region)
    for response in response_iterator:
        rds_instances = response['DBInstances']
        for instance in rds_instances:
            db_instance_status = instance['DBInstanceStatus']
            db_name = instance['DBInstanceIdentifier']
            if db_instance_status == 'available':
                vpc_id = instance['DBSubnetGroup']['VpcId']
                instance_name = instance['DBInstanceIdentifier']
                # add VPC ID and RDS instance name to dictionary
                if vpc_id in vpc_dict:
                    vpc_dict[vpc_id]['rds_instances'].append(instance_name)
                else:
                    vpc_dict[vpc_id] = {
                        'vpc_id': vpc_id,
                        'region': region,
                        'rds_instances': [instance_name]
                    }
            else:
                payload  = {
                  "rds_instance_name" : db_name,
                  "region": region,
                  "error": {
                    "Error": "RDSNotAvailableError",
                    "Cause": '{"errorMessage": "' + f"{db_name} current status is {db_instance_status}. {db_name} must be available to continue. Try again once available.\"}}"

                  }
                }             
                response = lambda_client.invoke(
                    FunctionName='platform_ScoreCardErrorHandler',
                    Payload=json.dumps(payload)
                )  
                
                responsePayload = response['Payload'].read()
                
                print(responsePayload)
    # convert dictionary to JSON and return as output
    return list(vpc_dict.values())
