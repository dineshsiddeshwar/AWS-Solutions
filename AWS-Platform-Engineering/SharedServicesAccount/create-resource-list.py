import boto3
import json
import pdb

regions = ['us-east-1', 'eu-west-1', 'ap-southeast-1']  # Replace with your desired list of regions

#file path

file_path = ".\\resources-prod.json"


#master dict containing resource info

dict_resources = dict()

#import dictionary contents from json



# Open the JSON file and load its contents into a dictionary
with open(file_path, 'r') as json_file:
    data = json.load(json_file)

# Access the dictionary and print its contents
print(data)
dict_resources = data


def get_vpc_ids (regions):
    vpc_ids={}
    for region in regions:
        ec2_client=boto3.client('ec2',region_name=region)
        response=ec2_client.describe_vpcs()
        vpcs=response['Vpcs']
        vpc_ids[region]=[vpc['VpcId'] for vpc in vpcs]
    return vpc_ids

vpc_ids = get_vpc_ids(regions)
print(vpc_ids)
dict_resources['aws_vpc']=vpc_ids

#subnet ids
def get_subnet_ids(regions):
    subnet_ids = {}
    for region in regions:
        ec2_client = boto3.client('ec2', region_name=region)
        response = ec2_client.describe_subnets()
        subnets = response['Subnets']
        az=dict()
        for subnet in subnets:
            
            az[subnet['AvailabilityZone']]=subnet['SubnetId']
        subnet_ids[region] = az
    return subnet_ids

subnet_ids = get_subnet_ids(regions)
print(subnet_ids)
dict_resources['aws_subnet']=subnet_ids


def get_secondary_subnet_ids(regions):
    subnet_ids = {}
    for region in regions:
        ec2_client = boto3.client('ec2', region_name=region)
        response = ec2_client.describe_subnets()
        subnets = response['Subnets']
        az=dict()
        for subnet in subnets:
            print(subnet)
            #az[subnet['AvailabilityZone']]=subnet['SubnetId']
        #subnet_ids[region] = az
    return subnet_ids


def get_endpoint_ids(regions):
    endpoint_ids = {}
    for region in regions:
        ec2_client = boto3.client('ec2', region_name=region)
        response = ec2_client.describe_vpc_endpoints()
        endpoints = response['VpcEndpoints']
        vpce=dict()
        for endpoint in endpoints:
            if endpoint['VpcEndpointType']=='Interface':
                service_name_suffix = endpoint['ServiceName'].split('.')[3:]
                service_name_suffix = ".".join(service_name_suffix)
                if service_name_suffix == 'logs':
                    service_keyname = 'CloudWatchLogs-Endpoint'
                elif service_name_suffix == 'events':
                    service_keyname = 'CloudWatchEvents-Endpoint'
                elif service_name_suffix=='monitoring':
                    service_keyname='CloudWatchMonitoring-Endpoint'
                elif service_name_suffix == 's3':
                    service_keyname ='S3PrivateLink-Endpoint'
                elif service_name_suffix == 'lambda':
                    service_keyname ='LambdaPrivateLink-Endpoint'
                elif service_name_suffix == 'ecr.api':
                    service_keyname ='ECRAPI-Endpoint'
                elif service_name_suffix == 'ecr.dkr':
                    service_keyname ='ECRDocker-Endpoint'
                elif service_name_suffix == 'appstream.api':
                    service_keyname ='AppStreamAPI-Endpoint'
                elif service_name_suffix == 'appstream.streaming':
                    service_keyname ='AppStreamStreaming-Endpoint'
                elif service_name_suffix == 'sagemaker.api':
                    service_keyname ='SageMakerAPI-Endpoint'
                elif service_name_suffix == 'sagemaker.runtime':
                    service_keyname ='SageMakerRuntime-Endpoint'
                elif service_name_suffix == 'states':
                    service_keyname ='StepFunction-Endpoint'
                elif service_name_suffix == 'execute-api':
                    service_keyname = 'api-gateway-Endpoint'
                elif service_name_suffix == 'airflow.api':
                    service_keyname = 'ApacheAirflowAPI-Endpoint'
                elif service_name_suffix == 'airflow.ops':
                    service_keyname = 'ApacheAirflowOPS-Endpoint'
                elif service_name_suffix == 'airflow.env':
                    service_keyname = 'ApacheAirflowENV-Endpoint'
                elif service_name_suffix == 'aps':
                    service_keyname = 'Aps-Endpoint'
                elif service_name_suffix == 'aps-workspaces':
                    service_keyname = 'Aps-workspaces-Endpoint'
                elif service_name_suffix == 'rds':
                    service_keyname = 'RDS-Endpoint'
                elif service_name_suffix == 'dms':
                    service_keyname = 'DMS-Endpoint'
                elif service_name_suffix == 'redshift':
                    service_keyname = 'Redshift-Endpoint'
                elif service_name_suffix == 'elasticache':
                    service_keyname = 'Elasticache-Endpoint'
                elif service_name_suffix == 'elasticloadbalancing':
                    service_keyname = 'ELB-Endpoint'
                elif service_name_suffix == 'eks':
                    service_keyname = 'EKS-Endpoint'
                elif service_name_suffix == 'dynamodb':
                    service_keyname = 'DynamoDB-Endpoint'
                elif service_name_suffix == 'fsx':
                    service_keyname = 'FSx-Endpoint'
                elif service_name_suffix == 'grafana':
                    service_keyname = 'Grafana-Endpoint'
                elif service_name_suffix == 'securityhub':
                    service_keyname = 'SecurityHub-Endpoint'
                elif service_name_suffix == 'backup':
                    service_keyname = 'Backup-Endpoint'
                elif service_name_suffix == 'Codebuild':
                    service_keyname = 'Codebuild-Endpoint'
                elif service_name_suffix == 'appsync-api':
                    service_keyname = 'AppSyncAPI-Endpoint'
                elif service_name_suffix == 'quicksight-website':
                    service_keyname = 'QuickSightWebsite-Endpoint'
                elif service_name_suffix == 'config':
                    service_keyname = 'Config-Endpoint'
                else:
                    service_keyname=str(service_name_suffix)+'-Endpoint'
                vpce[service_keyname]=endpoint['VpcEndpointId']
        endpoint_ids[region] = vpce
    return endpoint_ids

endpoint_ids = get_endpoint_ids(regions)
print(endpoint_ids)
dict_resources['aws_vpc_endpoint']=endpoint_ids

# ctr=0
# for x in hostedzones:
#     if "dkr.ecr.us" in x['Name']:
#         break
#     ctr+=1


def get_hostedzones():
    hostedzone_ids = {"us-east-1": {}, "eu-west-1": {}, "ap-southeast-1" : {} }
    Route53_client = boto3.client('route53')
    response = Route53_client.list_hosted_zones_by_name()
    hostedzones = response['HostedZones']
    hostedzones_all=[]
    hostedzones_all.extend(hostedzones)
    while response['IsTruncated']:
        response = Route53_client.list_hosted_zones_by_name(DNSName=response['NextDNSName'], HostedZoneId=response['NextHostedZoneId'])
        hostedzones = response['HostedZones']
        hostedzones_all.extend(hostedzones)
    for h in hostedzones_all:
        if "us-east-1" in h['Name']:
            region="us-east-1"
        elif "eu-west-1" in h['Name']:
            region="eu-west-1"
        elif "ap-southeast-1" in h['Name']:
            region="ap-southeast-1"
        if h['Name'].endswith('.'):
            h['Name'] = h['Name'].rstrip('.')
        service_name_suffix = h['Name'].split('.')[:-3]
        service_name_suffix = ".".join(service_name_suffix)
        if service_name_suffix == 'logs':
            service_keyname = 'CloudWatchLogs-Endpoint'
        elif service_name_suffix == 'events':
            service_keyname = 'CloudWatchEvents-Endpoint'
        elif service_name_suffix=='monitoring':
            service_keyname='CloudWatchMonitoring-Endpoint'
        elif service_name_suffix == 's3':
            service_keyname ='S3PrivateLink-Endpoint'
        elif service_name_suffix == 'lambda':
            service_keyname ='LambdaPrivateLink-Endpoint'
        elif service_name_suffix == 'api.ecr':
            service_keyname ='ECRAPI-Endpoint'
        elif service_name_suffix == 'dkr.ecr':
            service_keyname ='ECRDocker-Endpoint'
        elif 'kinesis' in service_name_suffix:
            service_keyname ='kinesis-streams-Endpoint'
        elif 'firehose' in service_name_suffix:
            service_keyname ='kinesis-firehose-Endpoint'
        elif service_name_suffix == 'appstream2':
            service_keyname ='AppStreamAPI-Endpoint'
        elif service_name_suffix == 'streaming.appstream':
            service_keyname ='AppStreamStreaming-Endpoint'
        elif 'ecs-a' in service_name_suffix:
            service_keyname = 'ecs-agent'
        elif 'ecs-t' in service_name_suffix:
            service_keyname = 'ecs-telemetry'
        elif service_name_suffix == 'api.sagemaker':
            service_keyname ='SageMakerAPI-Endpoint'
        elif service_name_suffix == 'runtime.sagemaker':
            service_keyname ='SageMakerRuntime-Endpoint'
        elif service_name_suffix == 'states':
            service_keyname ='StepFunction-Endpoint'
        elif service_name_suffix == 'execute-api':
            service_keyname = 'api-gateway-Endpoint'
        elif service_name_suffix == 'airflow.api':
            service_keyname = 'ApacheAirflowAPI-Endpoint'
        elif service_name_suffix == 'airflow.ops':
            service_keyname = 'ApacheAirflowOPS-Endpoint'
        elif service_name_suffix == 'airflow.env':
            service_keyname = 'ApacheAirflowENV-Endpoint'
        elif service_name_suffix == 'aps':
            service_keyname = 'Aps-Endpoint'
        elif service_name_suffix == 'aps-workspaces':
            service_keyname = 'Aps-workspaces-Endpoint'
        elif service_name_suffix == 'rds':
            service_keyname = 'RDS-Endpoint'
        elif service_name_suffix == 'dms':
            service_keyname = 'DMS-Endpoint'
        elif service_name_suffix == 'redshift':
            service_keyname = 'Redshift-Endpoint'
        elif service_name_suffix == 'elasticache':
            service_keyname = 'Elasticache-Endpoint'
        elif service_name_suffix == 'elasticloadbalancing':
            service_keyname = 'ELB-Endpoint'
        elif service_name_suffix == 'eks':
            service_keyname = 'EKS-Endpoint'
        elif service_name_suffix == 'dynamodb':
            service_keyname = 'DynamoDB-Endpoint'
        elif service_name_suffix == 'fsx':
            service_keyname = 'FSx-Endpoint'
        elif service_name_suffix == 'grafana':
            service_keyname = 'Grafana-Endpoint'
        elif service_name_suffix == 'securityhub':
            service_keyname = 'SecurityHub-Endpoint'
        elif service_name_suffix == 'backup':
            service_keyname = 'Backup-Endpoint'
        elif service_name_suffix == 'ds':
            service_keyname = 'DS-Endpoint'
        elif service_name_suffix == 'appsync-api':
            service_keyname = 'AppSyncAPI-Endpoint'
        elif service_name_suffix == 'quicksight-website':
            service_keyname = 'QuickSightWebsite-Endpoint'
        elif service_name_suffix == 'config':
            service_keyname = 'Config-Endpoint'
        else:
            service_keyname=str(service_name_suffix)+'-Endpoint'
        hostedzoneid=h['Id'].split('/')[-1]
        #vpc_asoociated_with_hostedzone=Route53_client.get_hosted_zone(Id=hostedzoneid)['VPCs']
        hostedzone_ids[region][service_keyname]=[]
        hostedzone_ids[region][service_keyname].append(hostedzoneid)
        #hostedzone_ids[region][service_keyname].append(vpc_asoociated_with_hostedzone)
        recordsets=Route53_client.list_resource_record_sets(HostedZoneId=h['Id'])['ResourceRecordSets']
        for r in recordsets:
            if r['Type']=='A':
                r_name = r['Name']
                if r_name.endswith('.'):
                    r_name=r_name.rstrip('.')
                recordset_resource=str(hostedzoneid)+"_"+str(r_name)+"_A"
                hostedzone_ids[region][service_keyname].append(recordset_resource)
    return hostedzone_ids


def get_hostedzones_DEBUG():
    hostedzone_ids = {"us-east-1": {}, "eu-west-1": {}, "ap-southeast-1" : {} }
    Route53_client = boto3.client('route53')
    response = Route53_client.list_hosted_zones_by_name()
    hostedzones = response['HostedZones']
    for h in hostedzones:
        print(h['Name'])


hostedzone_ids = get_hostedzones()
x=get_hostedzones_DEBUG()

print(hostedzone_ids)
dict_resources['aws_route53_zone']=hostedzone_ids





import boto3
#flow logs
def get_flow_logs():
    flow_logs = {}

    ec2_client = boto3.client('ec2')
    

    for region in regions:
        
        ec2_client = boto3.client('ec2', region_name=region)
        response = ec2_client.describe_flow_logs()

        flow_logs[region] = response['FlowLogs'][0]["FlowLogId"]

    return flow_logs

flow_logs_dict = get_flow_logs()

dict_resources['aws_flow_log']=flow_logs_dict







#policy arns 

import boto3

def list_policy_arns(suffixes):
    policy_arns = dict()

    regions = ['us-east-1', 'eu-west-1', 'ap-southeast-1']

    for region in regions:
        iam_client = boto3.client('iam', region_name=region)
        response = iam_client.list_policies(Scope='Local')

        for policy in response['Policies']:
            policy_name = policy['PolicyName']
            policy_arn = policy['Arn']

            for suffix in suffixes:
                if suffix in policy_name:
                    if region not in policy_arns.keys():
                        policy_arns[region]=[]
                        policy_arns[region].append(policy_arn)
                    else:
                        policy_arns[region].append(policy_arn)

    return policy_arns

suffixes = ["cloud_health", "ITOM"]
policy_arns_dict = list_policy_arns(suffixes)
dict_resources["aws_iam_policy"]= policy_arns_dict


# role arns

import boto3

def list_role_arns(suffixes):
    role_arns = dict()

    regions = ['us-east-1', 'eu-west-1', 'ap-southeast-1']

    for region in regions:
        iam_client = boto3.client('iam', region_name=region)
        response = iam_client.list_roles()

        for role in response['Roles']:
            role_name = role['RoleName']
            role_arn = role['Arn']

            for suffix in suffixes:
                if suffix in role_name:
                    if region not in role_arns.keys():
                        role_arns[region]=[]
                        role_arns[region].append(role_arn)
                    else:
                        role_arns[region].append(role_arn)

    return role_arns

suffixes = ["cloudhealth", "ITOM"]
role_arns_dict = list_role_arns(suffixes)
dict_resources["aws_iam_role"]= role_arns_dict

#instance profiles

import boto3

def get_instance_profiles(suffix):
    instance_profiles = dict()

    regions = ['us-east-1', 'eu-west-1', 'ap-southeast-1']

    for region in regions:
        iam_client = boto3.client('iam', region_name=region)
        response = iam_client.list_instance_profiles()

        for profile in response['InstanceProfiles']:
            profile_name = profile['InstanceProfileName']
            if suffix in profile_name:
                instance_profiles[region] = profile_name

    return instance_profiles

suffix="ITOMDiscovery"
instance_profiles_dict = get_instance_profiles(suffix)


dict_resources["aws_iam_instance_profile"]= instance_profiles_dict


#securitygroup

import boto3

def filter_security_groups_by_name(group_name):
    security_groups = dict()

    regions = ['us-east-1', 'eu-west-1', 'ap-southeast-1']

    for region in regions:
        ec2_client = boto3.client('ec2', region_name=region)
        response = ec2_client.describe_security_groups()

        for group in response['SecurityGroups']:
            if group_name in group['GroupName']:
                group_id = group['GroupId']
                security_groups.setdefault(region, []).append(group_id)

    return security_groups

group_name = "sharedvpcsec"
security_groups_dict = filter_security_groups_by_name(group_name)
dict_resources["aws_security_group"]= security_groups_dict


# Route 53 resources

#aws_route53_resolver_endpoint


def get_resolver_endpoints():
    resolver_endpoints = {}

    

    for region in regions:
        resolver_client = boto3.client('route53resolver', region_name=region)
        response = resolver_client.list_resolver_endpoints()

        endpoint_list = response['ResolverEndpoints']
        endpoint_ids = [endpoint['Id'] for endpoint in endpoint_list]

        resolver_endpoints[region] = endpoint_ids

    return resolver_endpoints

resolver_endpoints_dict = get_resolver_endpoints()
dict_resources["aws_route53_resolver_endpoint"]= resolver_endpoints_dict

#aws_route53_resolver_rule

import boto3

def get_resolver_rules():
    resolver_rules = {}

    

    for region in regions:
        resolver_client = boto3.client('route53resolver', region_name=region)
        response = resolver_client.list_resolver_rules()

        for rule in response['ResolverRules']:
            if 'Domain_Forwarder' in rule['Name']:
                rule_id = rule['Id']
                resolver_rules.setdefault(region, []).append(rule_id)

            

    return resolver_rules

resolver_rules_dict = get_resolver_rules()
dict_resources["aws_route53_resolver_rule"]= resolver_rules_dict

#aws_route53_resolver_rule_association

import boto3

def get_resolver_rule_associations():
    resolver_rule_associations = {}


    for region in regions:
        resolver_client = boto3.client('route53resolver', region_name=region)
        response = resolver_client.list_resolver_rule_associations()

        associations = response['ResolverRuleAssociations']
        for a in associations:
            if "Domain_Forwarder" in a['Name']:
                resolver_rule_associations[region] = a['Id']

    return resolver_rule_associations

resolver_rule_associations_dict = get_resolver_rule_associations()
dict_resources["aws_route53_resolver_rule_association"]= resolver_rule_associations_dict

#aws_ram_resource_share

import boto3

def get_ram_resource_shares():
    ram_resource_shares = {}

    

    for region in regions:
        ram_client = boto3.client('ram', region_name=region)
        response = ram_client.get_resource_shares(resourceOwner='SELF')

        resource_shares = response['resourceShares']
        share_arns = [share['resourceShareArn'] for share in resource_shares]

        ram_resource_shares[region] = share_arns

    return ram_resource_shares

ram_resource_shares_dict = get_ram_resource_shares()
dict_resources["aws_ram_resource_share"]= ram_resource_shares_dict

#aws_ram_principal_association
import boto3

def get_ram_principal_associations():
    ram_associations = {}

    

    for region in regions:
        ram_client = boto3.client('ram', region_name=region)
        response = ram_client.list_principals(resourceOwner='SELF')

        associations = response['principals']
        for a in associations:
            l=[a['id'],a['resourceShareArn']]
            ram_associations.setdefault(region,[]).append(l)

    return ram_associations

ram_associations_dict = get_ram_principal_associations()
dict_resources['aws_ram_principal_association']=ram_associations_dict


file_path = ".\\resources-prod.json"

# Open the file in write mode
with open(file_path, 'w') as json_file:
    # Write the dictionary contents to the file
    json.dump(dict_resources, json_file)

print(f"Dictionary contents written to {file_path} in JSON format.")

