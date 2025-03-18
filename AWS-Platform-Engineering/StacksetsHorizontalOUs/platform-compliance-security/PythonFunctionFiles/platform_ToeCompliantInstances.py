import json
import boto3
import re
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
logger.addHandler(CH)

class ToeCompliance(object):
    def __init__(self, event, context):
        self.session = boto3.session.Session()
        self.ssm_client = self.session.client('ssm')

    def get_instances(self,ec2_client):
        try:
            instances=ec2_client.describe_instances(MaxResults=999)
            all_instances=[]
            images_lists=[]
            number_of_instances_tagged=0
            instance_image_mapping={}
            for reservation in instances['Reservations']:
                for instance in reservation['Instances']:
                    #print(instance)
                    instance_id=instance['InstanceId']
                    image_id=instance['ImageId']
                    if instance['Tags']:
                        for tag in (instance['Tags']):
                            if tag['Key']=='platform_toe_compliant':
                                number_of_instances_tagged=number_of_instances_tagged+1
                                print('instances with tag',instance_id)
                                print('tag value',tag['Value'])
                    instance_image_mapping[instance_id]=image_id
            print('number of instances scanned',len(instance_image_mapping))
            print('number_of_instances_having tags',number_of_instances_tagged)
            return instance_image_mapping
        except Exception as exception:
            print(str(exception))
            
    def get_images(self, instance_image_mapping, ec2_client):
        images_lists=[]
        try:
            for instance_id, image_id in instance_image_mapping.items():
                try: 
                    response = ec2_client.describe_images(
                    ImageIds=[image_id]
                    )
                    images_lists.append(response['Images'][0]['Name'])
                    instance_image_mapping[instance_id]=response['Images'][0]['Name']
                    print(response['Images'][0]['Name'])
                except Exception as exception:
                    images_lists.append('AMI not found')
                    instance_image_mapping[instance_id]='AMI not found'
                    print('AMI not found')
            return instance_image_mapping
        except Exception as exception:
            print(str(exception))
            
    def toe_check(self,instance_image_mapping, ec2_client):
        master_list=[]
        pattern_list=[r'RHEL-7*',r'RHEL-8*',r'RHEL-9*',r'amzn2-ami-hvm*',r'amzn2-ami-.*-hvm-.*',r'aws-storage-gateway-*',r'aws-datasync-*',
        r'bottlerocket-aws-k8s-*',r'aws-parallelcluster-.*-amzn2*',r'Windows_Server-2019-English-Full-Base*',r'Windows_Server-2016-English-Full-Base*',r'Windows_Server-2016-English-Full-ECS_Optimized-*',
        r'Windows_Server-2019-English-Full-ECS_Optimized-*',r'Windows_Server-2022-English-Full-Base*',r'Windows_Server-2022-English-Full-ECS_Optimized-*',r'ubuntu/images/hvm-ssd/ubuntu-focal-20.04*',
        r'ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-*',r'amzn2-ami-ecs-hvm-*',r'amazon-eks-node-*',r'amazon-eks-arm64-node-*',r'ShellCorp-GI-RHEL-7.9*',r'ShellCorp-GI-RHEL-8*']

        matched_amis=[]
        match_found_flag=0
        instance_tag_yes=[]
        instance_tag_no=[]
        instance_tag_other=[]
        for instance_id,ami_name in instance_image_mapping.items():
            for pattern in pattern_list:
                if re.match(pattern,ami_name):
                    matched_amis.append(instance_id)
                    match_found_flag=1
                    break

            if match_found_flag==1:
                instance_tag_yes.append(instance_id)
            elif match_found_flag==0 and ami_name!='AMI not found':
                instance_tag_no.append(instance_id)
            else:
                instance_tag_other.append(instance_id)
            match_found_flag=0
        master_list.append(instance_tag_yes)
        master_list.append(instance_tag_no)
        master_list.append(instance_tag_other)
        print('master list',master_list)
        print('yes',master_list[0])
        print('no',master_list[1])
        print('other',master_list[2])
        return master_list
        
    def batch_and_tag(self, master_list, ec2_client):
        number_of_instances_tag_created_or_updated=0
        instance_tag_yes=master_list[0]
        instance_tag_no=master_list[1]
        instance_tag_other=master_list[2]
        try: 
            batches_for_yes=[instance_tag_yes[i:i+100] for i in range(0, len(instance_tag_yes), 100)]
            batches_for_no=[instance_tag_no[i:i+100] for i in range(0, len(instance_tag_no), 100)]
            batches_for_other=[instance_tag_other[i:i+100] for i in range(0, len(instance_tag_other), 100)]
            if len(batches_for_yes)>0:    
                for batch in batches_for_yes:
                        ec2_client.create_tags(Resources=batch,
                                            Tags=[{'Key': 'platform_toe_compliant',
                                                    'Value': 'yes', }, ], )
                        number_of_instances_tag_created_or_updated=number_of_instances_tag_created_or_updated+len(batch)
            if len(batches_for_no)>0:
                for batch in batches_for_no:
                        ec2_client.create_tags(Resources=batch,
                                            Tags=[{'Key': 'platform_toe_compliant',
                                                    'Value': 'no', }, ], )
                        number_of_instances_tag_created_or_updated=number_of_instances_tag_created_or_updated+len(batch)
            if len(batches_for_other)>0:
                for batch in batches_for_other:
                        ec2_client.create_tags(Resources=batch,
                                            Tags=[{'Key': 'platform_toe_compliant',
                                                    'Value': 'NoAMIFound', }, ], )
                        number_of_instances_tag_created_or_updated=number_of_instances_tag_created_or_updated+len(batch)
            print('number_of_instances_tag_created_or_updated',number_of_instances_tag_created_or_updated)
        except Exception as exception:
            print(str(exception))
        
    def for_regions(self):
        ssm_client=boto3.client('ssm')
        regions_response =ssm_client.get_parameter(Name='platform_whitelisted_regions')
        regions_results = regions_response['Parameter']['Value']
        regions = regions_results.split(',')
        for region in regions:
            self.orchestration_func(region) 
            
    def orchestration_func(self, region):
        print('region',region)
        ec2_client = boto3.client('ec2',region_name=region)
        instance_image_mapping=self.get_instances(ec2_client)
        if len(instance_image_mapping)>0:
            instance_image_mapping=self.get_images(instance_image_mapping,ec2_client)
        else:
            instance_image_mapping={}
            print('no instances found')
        if len(instance_image_mapping)>0:
            master_list=self.toe_check(instance_image_mapping, ec2_client)
        else:
            master_list=[]
            print('no mapping found')    
        if len(master_list)>0:
            self.batch_and_tag(master_list, ec2_client)
        else:
            print('no instances found and no tagging done')
        
def lambda_handler(event, context):
    toe_compliance= ToeCompliance(event, context)
    toe_compliance.for_regions()