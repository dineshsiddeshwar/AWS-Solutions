import boto3
import time
import datetime
import os
import ipaddress
import time
import json

def lambda_handler(event, context):
    # Get region and RDS instance name from input
    region = event['region']
    rds_instances = event['rds_instances']
    


    if 'subnet_id' in event:
        rds_instance_data = rds_instances[0]
        rds_instance_name = rds_instance_data["instance_name"]
        endpoint_id = rds_instance_data["endpoint_id"]
        return changeVPC(region, rds_instance_name, event["subnet_id"],rds_instances,endpoint_id)
        # retrieve the current list of subnets associated with the VPC endpoint
    else:
        rds_instance_name = rds_instances[0]
        return changeVPC(region, rds_instance_name,rds_instances=rds_instances)


def changeVPC(region, rds_instance_name,input_subnet_id = None, rds_instances = None, endpoint_id =None):
    ec2 = boto3.client('ec2', region_name=region)
    rds_client = boto3.client('rds', region_name=region)
    ssm_client = boto3.client('ssm', region_name=region)

    response = rds_client.describe_db_instances(DBInstanceIdentifier=rds_instance_name)
    db_instance = response['DBInstances'][0]

    # Get VPC, security group of the RDS instance
    vpc_id = db_instance['DBSubnetGroup']['VpcId']

    security_group_ids = [sg['VpcSecurityGroupId'] for sg in db_instance['VpcSecurityGroups']]
    subnet_ids = [subnet['SubnetIdentifier'] for subnet in db_instance['DBSubnetGroup']['Subnets']]

    lambda_client = boto3.client('lambda', region_name=region)
    response = lambda_client.get_function(FunctionName=os.environ['FUNCTION_NAME'])
    lambda_vpc_id = response['Configuration']['VpcConfig']['VpcId'] if 'VpcConfig' in response['Configuration'] else ""
    lambda_subnet_ids = response['Configuration']['VpcConfig']['SubnetIds'] if 'VpcConfig' in response['Configuration'] else []
    lambda_sg_ids = response['Configuration']['VpcConfig']['SecurityGroupIds'] if 'VpcConfig' in response['Configuration'] else []

    if input_subnet_id is not None:
        if input_subnet_id not in lambda_subnet_ids:
            f'scorecard_vpcboundlambda Lambda function is not in the same subnet (Input: {input_subnet_id}, Lambda Subnets: {lambda_subnet_ids}), starting SSM Automation execution'
            accountID = getAccountId()
            response = ssm_client.start_automation_execution(
                DocumentName='AWSConfigRemediation-MoveLambdaToVPC',
                Parameters={
                    'AutomationAssumeRole': [f'arn:aws:iam::{accountID}:role/platform_dbcontrols_movevpcrole'],
                    'FunctionName': [os.environ['FUNCTION_NAME']],
                    'SecurityGroupIds': lambda_sg_ids,
                    'SubnetIds': [input_subnet_id]
                }
            )
            execution_id = response['AutomationExecutionId']
            
            response = ec2_client.describe_vpc_endpoints(VpcEndpointIds=[vpc_endpoint_id])
            current_subnet_ids = response['VpcEndpoints'][0]['SubnetIds']
            # remove all current subnets from the VPC endpoint
            ec2_client.modify_vpc_endpoint(
                VpcEndpointId=endpoint_id,
                RemoveSubnetIds=current_subnet_ids
            )
            # add the new subnet to the VPC endpoint
            ec2_client.modify_vpc_endpoint(
                VpcEndpointId=endpoint_id,
                AddSubnetIds=[input_subnet_id]
            )

            return {
                'rds_instance_name': rds_instance_name,
                'region': region,
                'subnet_id': subnet_ids[0],
                'vpc_id': vpc_id,
                'message': f'Changing Subnet from {input_subnet_id} to {lambda_subnet_ids}',
                'automationexecutionid': execution_id,
                'rds_instances':rds_instances
            }
        else:
            return {
                'rds_instance_name': rds_instance_name,
                'region': region,
                'subnet_id': lambda_subnet_ids[0],
                'vpc_id': vpc_id,
                'message': 'Already in same subnet',
                'rds_instances':rds_instances
            }
    else:
        if lambda_vpc_id == vpc_id:
            print(
                f'scorecard_vpcboundlambda Lambda function is already in the RDS VPC (VpcId: {vpc_id}), skipping SSM Automation execution')
            return {
                'rds_instance_name': rds_instance_name,
                'region': region,
                'subnet_id': lambda_subnet_ids[0],
                'vpc_id': vpc_id,
                'message': 'Already in same VPC',
                'rds_instances':rds_instances

            }
        else:
            print(
                f'scorecard_vpcboundlambda Lambda function is not in the RDS VPC (RDS VpcId: {vpc_id}, Lambda VpcId: {lambda_vpc_id}), starting SSM Automation execution')

            # Check if the security group already exists
            try:
                tag_key = 'DCRScoreCard'
                tag_value = 'True'

                response = ec2.describe_security_groups(
                    Filters=[
                        {'Name': 'vpc-id', 'Values': [vpc_id]},
                        {'Name': f'tag:{tag_key}', 'Values': [tag_value]}
                    ]
                )
                security_group_id = response['SecurityGroups'][0]['GroupId']
            except:
                # If the security group does not exist, create a new one
                ec2_create_sg_response = ec2.create_security_group(
                    GroupName="scorecard_lambdaSG",
                    Description="Security Group for Scorecard La",
                    VpcId=vpc_id
                )
                security_group_id = ec2_create_sg_response['GroupId']

                ec2.create_tags(
                    Resources=[security_group_id],
                    Tags=[{'Key': 'DCRScoreCard', 'Value': 'True'}]
                )

            accountID = getAccountId()
            response = ssm_client.start_automation_execution(
                DocumentName='AWSConfigRemediation-MoveLambdaToVPC',
                Parameters={
                    'AutomationAssumeRole': [f'arn:aws:iam::{accountID}:role/platform_dbcontrols_movevpcrole'],
                    'FunctionName': [os.environ['FUNCTION_NAME']],
                    'SecurityGroupIds': [security_group_id],
                    'SubnetIds': [subnet_ids[0]]
                }
            )

            execution_id = response['AutomationExecutionId']
            
            existingSubnet = "None"
            
            if len(lambda_subnet_ids) > 0:
                existingSubnet = lambda_subnet_ids[0]

            return {
                'rds_instance_name': rds_instance_name,
                'region': region,
                'subnet_id': subnet_ids[0],
                'vpc_id': vpc_id,
                'message': f'Changing VPC from {lambda_vpc_id} to {vpc_id} | subnet {existingSubnet} to  subnet {subnet_ids[0]}',
                'automationexecutionid': execution_id,
                'rds_instances':rds_instances

            }
def getAccountId():
    sts_client = boto3.client('sts', region_name=os.environ['AWS_REGION'],endpoint_url=f"https://sts.{os.environ['AWS_REGION']}.amazonaws.com")
    response = sts_client.get_caller_identity()
    account_id = response['Account']
    return account_id