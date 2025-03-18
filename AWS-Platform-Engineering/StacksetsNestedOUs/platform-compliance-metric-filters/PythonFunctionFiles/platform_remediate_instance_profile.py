
import random
import boto3

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

class CheckProfileEC2(object):

    def __init__(self, event):
        global session
        session = boto3.session.Session()
        # get approved regions
        try:
            self.account_number = str(boto3.client('sts').get_caller_identity().get('Account'))
            print("account number:",self.account_number)
            self.approved_regions = ["us-east-1","eu-west-1","us-east-2","us-west-1","us-west-2","ap-south-1","ap-southeast-2","ap-southeast-1","eu-central-1","eu-west-2","ap-northeast-2","ap-northeast-1","ca-central-1","eu-north-1"]
            
        except Exception as exception:
            logger.error(str(exception))
        

    def describe_ec2(self,region):  #add next token loop
        ec2=boto3.client('ec2',region_name=region)
        vpcs=ec2.describe_vpcs()
        vpcsList = vpcs['Vpcs']
        instance_id = []
        instance_profile_name = []

        if vpcsList:
            # decribe ec2 list
            print("VPCs exist in the region:",region,"no. of VPCs:", len(vpcsList))
            response = ec2.describe_instances(
                            Filters=[{"Name": "instance-state-name", "Values" : ["pending","running","shutting-down","stopping","stopped"]}],
                            DryRun=False,
                            MaxResults=1000
                        )        
            while True:
                instance_list_tmp = [r['Instances'] for r in response['Reservations']]
                instance_list = [val for sublist in instance_list_tmp for val in sublist]            
                for i in instance_list:
                    instance_id.append(i['InstanceId'])
                    try:
                        instance_profile_name.append(i['IamInstanceProfile']['Arn'].split('/')[-1])
                    except:
                        instance_profile_name.append('null')
                if 'NextToken' in response:
                    NextToken = response['NextToken']
                    response = self.ec2_client.describe_instances(
                        DryRun=False,
                        MaxResults=1000,
                        NextToken=NextToken
                    )
                else:
                    break
                    
        return instance_id, instance_profile_name
        
            
    def get_profile_role(self, profile_name):        
        response = self.iam_client.get_instance_profile(
            InstanceProfileName=profile_name
        )        
        role_name = response['InstanceProfile']['Roles'][0]['RoleName']
        return role_name

    def get_role_policies(self, role_name): 
        role_policies = []
        response = self.iam_client.list_attached_role_policies(
            RoleName=role_name
        )
        while True:
            policies_list = response['AttachedPolicies']
            role_policies.extend([p['PolicyName'] for p in policies_list])
            if response['IsTruncated'] == True:
                marker = response['Marker']
                response = self.iam_client.list_attached_role_policies(
                    RoleName=role_name,
                    Marker=marker
                )
            else:
                break
        
        return role_policies

    def get_missing_policies(self, m_policies_list):
        required_policies = ['platform_iam_pass_role_policy','platform_sts_full_access','platform_ec2instance_policy','ReadOnlyAccess','AmazonSSMManagedInstanceCore','CloudWatchAgentServerPolicy','AmazonSSMDirectoryServiceAccess', 'AWSBackupFullAccess', 'AmazonEC2FullAccess']
        missing_policies = [p for p in required_policies if p not in m_policies_list]
        return missing_policies

    def get_instance_tag(self,instance_id):
        try:
            response = self.ec2_client.describe_tags(
                            Filters=[
                                        {
                                            'Name': 'resource-id',
                                            'Values': [
                                            instance_id,
                                            ],
                                        },
                                    ],
                            )
            tag_list = response['Tags']
            logger.info(tag_list)
            for key_tag in tag_list:
                if key_tag['Key'] == 'aws:eks:cluster-name':
                    print(key_tag['Key'])
                    print('==== Inside get_instance_tag loop =======')
                    return True
            else:
                return False
        except Exception as exception:
            logger.error(str(exception))
    
    def associate_profile(self,instance_id,instance_tag):
        if not instance_tag:
            response = self.ec2_client.associate_iam_instance_profile(
                IamInstanceProfile={
                    'Name': 'platform_service_instance'
                },
                InstanceId=instance_id
            )
        else:
            print(" EKS-Node skipping platform_service_instance role")

    def add_policies(self,role,missing_p,account_number,instance_tag):
        for m in missing_p:
            if m in ['platform_iam_pass_role_policy','platform_sts_full_access','platform_ec2instance_policy']:
                policy_arn = 'arn:aws:iam::{}:policy/{}'.format(account_number,m) 
                if not instance_tag:
                    response = self.iam_client.attach_role_policy(
                        RoleName=role,
                        PolicyArn=policy_arn
                    )
                else:
                    print('skipping policies - {}'.format(m))
            else:
                policy_arn = 'arn:aws:iam::aws:policy/{}'.format(m)
                response = self.iam_client.attach_role_policy(
                RoleName=role,
                PolicyArn=policy_arn
                )

    def policies_to_detach(self):
        self.iam_client = boto3.client('iam')
        required_policies_tormeove = ['CloudWatchFullAccessV2','AmazonSSMFullAccess']
        existing_policies = self.get_role_policies("platform_service_instance")
        toremove_policies = [ptr for ptr in existing_policies if ptr in required_policies_tormeove]
        if toremove_policies != None:
            for ptrn in toremove_policies:
                policy_arn = 'arn:aws:iam::aws:policy/{}'.format(ptrn)
                response = self.iam_client.detach_role_policy(
                    RoleName='platform_service_instance',
                    PolicyArn=policy_arn
                )

    def profile_remediate(self):
        for region in self.approved_regions:
            self.iam_client = boto3.client('iam',region_name=region)
            self.ec2_client = boto3.client('ec2',region_name=region)
            print("Set for region:",region)
            [int_id, int_name] = self.describe_ec2(region)
            for id, name in zip(int_id, int_name):
                instance_tag = self.get_instance_tag(id)
                if name == 'null':
                    try:
                        self.associate_profile(id,instance_tag)
                        logger.info('Instance {} profile association SUCCESS'.format(id))
                    except Exception as exception:
                        logger.info('Instance {} profile association FAILED\n ERROR:{}'.format(id,str(exception)))
                    continue
                try:
                    role = self.get_profile_role(name)
                    policies = self.get_role_policies(role)
                    missing_p = self.get_missing_policies(policies)
                    if missing_p != None:
                        self.add_policies(role,missing_p,self.account_number,instance_tag)
                    logger.info('Instance {} with role {} permissions SUCCESS'.format(id,name))
                except Exception as exception:
                    logger.info('Instance {} with role {} permissions FAILED\n ERROR:{}'.format(id,name,str(exception)))

def lambda_handler(event,context):
    """
    """
    try:
        profile_ec2_object = CheckProfileEC2(event)
        profile_ec2_object.policies_to_detach()
        profile_ec2_object.profile_remediate()
    except Exception as exception:
        logger.error(str(exception))

