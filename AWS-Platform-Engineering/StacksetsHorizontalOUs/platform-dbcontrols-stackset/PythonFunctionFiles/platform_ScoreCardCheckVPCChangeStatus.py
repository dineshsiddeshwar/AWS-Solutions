import json
import boto3
import datetime
import time
import os

def lambda_handler(event, context):
    region = event["region"]
    rds_instance_name = event["rds_instance_name"]
    automationExecutionID = event["automationexecutionid"]
    subnet_id = event["subnet_id"]
    vpc_id = event["vpc_id"]
    rds_instances = event["rds_instances"]

    iterationLimit = 10
    
    # print(event)
    # if event.get("iterations") is not None:
    #     iterations = 0
    #     print("not there")
    # else:
    #     print("there")
        
    try:
        iterations = int(event['iterations']) + 1
    except Exception as e:
        iterations = 0
        
        
    result = checkStatus(region,rds_instance_name,automationExecutionID,subnet_id)
    vpcChangeStatus = result['status']
    result['region'] = region
    result['rds_instance_name'] = rds_instance_name
    result['iterations'] = iterations
    result['vpc_id'] = vpc_id
    result['rds_instances'] = rds_instances

    
    if iterations > iterationLimit:
        raise Exception(f"Timed Out (Iterations) changing VPC")
    elif vpcChangeStatus in ["Failed","Timed Out","Cancelled"]:
        raise Exception(f"{vpcChangeStatus} changing VPC")

    return result
  

def checkStatus(region,rds_instance_name,automationExecutionID,subnet_id):
    session = boto3.Session(region_name=region)
    ssm_client = session.client('ssm') 

    response = ssm_client.describe_automation_executions(
        Filters = [
            {
                'Key': 'ExecutionId',
                'Values': [automationExecutionID]
            
            }    
        ]
        
    
    )
    status = response['AutomationExecutionMetadataList'][0]['AutomationExecutionStatus']
    
    return {
        'region':region,
        'rds_instance_name':rds_instance_name,
        'automationexecutionid': automationExecutionID,
        'status': status,
        'subnet_id':subnet_id
    }