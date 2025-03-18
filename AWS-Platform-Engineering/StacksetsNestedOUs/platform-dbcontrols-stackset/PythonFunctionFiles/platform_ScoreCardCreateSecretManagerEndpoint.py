import boto3
import time
import datetime
import random
import os
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    vpc_id = event['vpc_id']
    subnet_id = event['subnet_id']
    region = event['region']
    rds_instances = event['rds_instances']
    inputPayload = {"invocationType": "check_sm_connectivity"}
    
    functionName = os.environ['FUNCTION_NAME']
    lambda_client = boto3.client('lambda',region_name = region)
    
    try:
        response = lambda_client.invoke(
            FunctionName=functionName,
            Payload=json.dumps(inputPayload)
        )
        
        responsePayload = response['Payload'].read()
        response_arr = json.loads(responsePayload)
        print(response_arr)
        secretsmanager_public_api_reachable = response_arr['secretsmanager_public_api_reachable']
        
        if secretsmanager_public_api_reachable == "True":
            print("True")
            return {
                'endpoint_ip': "None",
                'endpoint_id': "None",
                'security_group_id':"None",
                'vpc_id':vpc_id,
                'region':region,
                'subnet_id':subnet_id,
                'rds_instances':rds_instances
            }
    except Exception as e:
        print(e)
        pass

    ec2 = boto3.client('ec2', region_name=region)
    # Check if the security group already exists
    security_group_name = 'SecretsManagerVpcEndpointSecurityGroup'
    security_group_description = 'Security group for Secrets Manager VPC endpoint'
    try:
        response = ec2.describe_security_groups(
            Filters=[
                {'Name': 'vpc-id', 'Values': [vpc_id]},
                {'Name': 'group-name', 'Values': [security_group_name]}
            ]
        )
        security_group_id = response['SecurityGroups'][0]['GroupId']
    except:
        # If the security group does not exist, create a new one
        response = ec2.create_security_group(
            GroupName=security_group_name,
            Description=security_group_description,
            VpcId=vpc_id
        )
        security_group_id = response['GroupId']
        
    print(security_group_id)
        
        
    
    # get the security group of the Lambda function
    lambda_client = boto3.client('lambda',region_name = region)

    response = lambda_client.get_function_configuration(FunctionName=os.environ['FUNCTION_NAME'])
    lambda_security_group_id = response['VpcConfig']['SecurityGroupIds'][0]

    # lambda_security_group_id = ''
    # print(response)
    # for key in response['Configuration'].keys():
    #     if key == 'VpcConfig':    
    #         lambda_security_group_id = response['VpcConfig']['SecurityGroupIds'][0]
    
    print(lambda_security_group_id)

    
    try:
        response = ec2.authorize_security_group_ingress(
            GroupId=security_group_id,
            IpPermissions=[
                {
                    'IpProtocol': '-1',
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
    
    
    response = ec2.create_vpc_endpoint(
        VpcId=vpc_id,
        ServiceName='com.amazonaws.' + region + '.secretsmanager',
        VpcEndpointType='Interface',
        SubnetIds=[subnet_id],
        SecurityGroupIds=[security_group_id], # use the ID of the existing or newly created security group
        PrivateDnsEnabled=False # turn off private DNS
    )
    
    # Get the VPC endpoint ID
    vpc_endpoint_id = response['VpcEndpoint']['VpcEndpointId']
    # Now, wait until the VPC endpoint is available
    while True:
        responseLoop = ec2.describe_vpc_endpoints(VpcEndpointIds=[vpc_endpoint_id])
        endpoint_state = responseLoop['VpcEndpoints'][0]['State']
        if endpoint_state == 'available':
            print(f"VPC endpoint {vpc_endpoint_id} is now available.")
            break
        elif endpoint_state in ['pending', 'pendingAcceptance']:
            print("VPC endpoint is still in the pending state, waiting for 10 seconds...")
            time.sleep(10)
        else:
            raise Exception(f"VPC endpoint {vpc_endpoint_id} entered an unexpected state: {endpoint_state}")
    
    
    secret_manager = boto3.client('secretsmanager', region_name=region)
    print(response)
    # secret_manager.tag_resource(ResourceArn=response['VpcEndpoint']['Arn'], Tags=[{'Key': 'DCRScoreCard', 'Value': 'True'}])
    vpc_endpoint_id = response['VpcEndpoint']['VpcEndpointId']
    endpoint_dns = response['VpcEndpoint']['DnsEntries']
    # Get the IP address of the VPC endpoint
    network_interface_id = response['VpcEndpoint']['NetworkInterfaceIds'][0]
    network_interface = ec2.describe_network_interfaces(
        NetworkInterfaceIds=[network_interface_id]
    )
    vpc_endpoint_ip = network_interface['NetworkInterfaces'][0]['PrivateIpAddress']
    ec2.create_tags(
        Resources=[vpc_endpoint_id],
        Tags=[{'Key': 'DCRScoreCard', 'Value': 'True'}]
    )
    ec2.create_tags(
        Resources=[security_group_id],
        Tags=[{'Key': 'DCRScoreCard', 'Value': 'True'}]
    )

    return {
        'endpoint_ip': endpoint_dns[0]['DnsName'],
        'endpoint_id': vpc_endpoint_id,
        'security_group_id':security_group_id,
        'vpc_id':vpc_id,
        'region':region,
        'subnet_id':subnet_id,
        'rds_instances':rds_instances

    }
