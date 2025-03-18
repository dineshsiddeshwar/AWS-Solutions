import random
import logging
import boto3
from datetime import datetime

LOGGER = logging.getLogger('logging')
LOGGER.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
LOGGER.addHandler(CH)

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# This lambda will be executed during create/update AWS ChildAccount
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


class TagEKSAmiPerAccount(object):
    """
    # Class: TagEKSAmiPerAccount
    # Description: EKS AMI Tagging in the child account
    """

    def __init__(self, event, context):
        self.event = event
        self.context = context
        LOGGER.info("Event: %s" % self.event)
        LOGGER.info("Context: %s" % self.context)
        try:
            # get relevant input params from event
            session_client = boto3.Session()

            self.reason_data = ""
            self.res_dict = {"account_type": event['ResourceProperties']['AccountType']}
            self.account_number = event['accountNumber']

            self.sts_client = session_client.client('sts')
            self.ssm_client = session_client.client('ssm')

            # Fetch the values form SSM Parameters
            self.public_regions_str = event['SSMParametres']['whitelisted_regions_public']
            self.public_regions = self.public_regions_str.split(',')

            self.private_regions_str = event['SSMParametres']['whitelisted_regions_private']
            self.private_regions = self.private_regions_str.split(',')

            self.ami_tags_str = event['SSMParametres']['ami_tags']
            self.tagging = self.ami_tags_str.split(',')

            self.owner = ['amazon']
            self.batch_size = 300
            self.amilist_pub = ["amazon-eks-node-1.18*", "amazon-eks-gpu-node-1.18*", "amazon-eks-arm64-node-1.18*",
                                "amazon-eks-node-1.19*", "amazon-eks-gpu-node-1.19*", "amazon-eks-arm64-node-1.19*",
                                "amazon-eks-node-1.20*", "amazon-eks-gpu-node-1.20*", "amazon-eks-arm64-node-1.20*",
                                "amazon-eks-node-1.21*", "amazon-eks-gpu-node-1.21*", "amazon-eks-arm64-node-1.21*",
                                "amazon-eks-node-1.22*", "amazon-eks-gpu-node-1.22*", "amazon-eks-arm64-node-1.22*",
                                "amazon-eks-node-1.23*", "amazon-eks-gpu-node-1.23*", "amazon-eks-arm64-node-1.23*",
                                "amazon-eks-node-1.24*", "amazon-eks-gpu-node-1.24*", "amazon-eks-arm64-node-1.24*",
                                "amazon-eks-node-1.25*", "amazon-eks-gpu-node-1.25*", "amazon-eks-arm64-node-1.25*",
                                "amazon-eks-node-1.26*", "amazon-eks-gpu-node-1.26*", "amazon-eks-arm64-node-1.26*",
                                "amazon-eks-node-1.27*", "amazon-eks-gpu-node-1.27*", "amazon-eks-arm64-node-1.27*", 
                                "amazon-eks-node-1.28*", "amazon-eks-gpu-node-1.28*", "amazon-eks-arm64-node-1.28*",
                                "amazon-eks-node-1.29*", "amazon-eks-gpu-node-1.29*", "amazon-eks-arm64-node-1.29*", "bottlerocket-aws-k8s*"]
            
            self.amilist_priv = ["amazon-eks-node-1.18*", "amazon-eks-gpu-node-1.18*", "amazon-eks-arm64-node-1.18*",
                                "amazon-eks-node-1.19*", "amazon-eks-gpu-node-1.19*", "amazon-eks-arm64-node-1.19*",
                                "amazon-eks-node-1.20*", "amazon-eks-gpu-node-1.20*", "amazon-eks-arm64-node-1.20*",
                                "amazon-eks-node-1.21*", "amazon-eks-gpu-node-1.21*", "amazon-eks-arm64-node-1.21*",
                                "amazon-eks-node-1.22*", "amazon-eks-gpu-node-1.22*", "amazon-eks-arm64-node-1.22*",
                                "amazon-eks-node-1.23*", "amazon-eks-gpu-node-1.23*", "amazon-eks-arm64-node-1.23*",
                                "amazon-eks-node-1.24*", "amazon-eks-gpu-node-1.24*", "amazon-eks-arm64-node-1.24*",
                                "amazon-eks-node-1.25*", "amazon-eks-gpu-node-1.25*", "amazon-eks-arm64-node-1.25*",
                                "amazon-eks-node-1.26*", "amazon-eks-gpu-node-1.26*", "amazon-eks-arm64-node-1.26*",
                                "amazon-eks-node-1.27*", "amazon-eks-gpu-node-1.27*", "amazon-eks-arm64-node-1.27*", 
                                "amazon-eks-node-1.28*", "amazon-eks-gpu-node-1.28*", "amazon-eks-arm64-node-1.28*",
                                "amazon-eks-node-1.29*", "amazon-eks-gpu-node-1.29*", "amazon-eks-arm64-node-1.29*", "bottlerocket-aws-k8s*"]                                
            # child account session
            self.child_account_role_arn = "arn:aws:iam::{}:role/platform_service_inflation". \
                format(self.account_number)
            self.child_account_session_name = "childAccountSession-" + \
                                              str(random.randint(1, 100000))
            self.child_account_role = self.sts_client.assume_role(
                RoleArn=self.child_account_role_arn,
                RoleSessionName=self.child_account_session_name)
            self.child_credentials = self.child_account_role.get('Credentials')
            self.child_access_key = self.child_credentials.get('AccessKeyId')
            self.child_secret_access_key = self.child_credentials.get('SecretAccessKey')
            self.child_session_token = self.child_credentials.get('SessionToken')
            self.child_assume_role_session = boto3.Session(
                self.child_access_key,
                self.child_secret_access_key,
                self.child_session_token)
        except Exception as exception:
            self.reason_data = "Missing required property %s" % exception
            LOGGER.error(self.reason_data)

    # List EKS Images in child account.
    def list_eks_images(self):
        if 'public' in self.res_dict['account_type']:
            try:
                print('Public Inside List Images')
                for region in self.public_regions:
                    ec2_client = self.child_assume_role_session.client('ec2', region_name=region)
                    print("INSIDE REGION - {}", region)
                    response = ec2_client.describe_images(
                        Owners=self.owner,
                        Filters=[
                            {'Name': 'name', 'Values': self.amilist_pub}
                        ]
                    )
                    images = response['Images']
                    self.tag_resources(images, ec2_client)
                self.res_dict['EKS AMI Tagging'] = 'PASSED'
            except Exception as exception:
                print("ERROR EKS AMI Tagging", exception)
                self.reason_data = "EKS AMI Tagging %s" % exception
                LOGGER.error(self.reason_data)
                self.res_dict['EKS AMI Tagging'] = 'FAILED'
                return self.res_dict
            return self.res_dict
        elif 'private' in self.res_dict['account_type']:
            try:
                print('Private Inside List Images')
                for region in self.private_regions:
                    ec2_client = self.child_assume_role_session.client('ec2', region_name=region)
                    print("INSIDE REGION - {}", region)
                    response = ec2_client.describe_images(
                        Owners=self.owner,
                        Filters=[
                            {'Name': 'name', 'Values': self.amilist_priv}
                        ]
                    )
                    images = response['Images']
                    self.tag_resources(images, ec2_client)
                self.res_dict['EKS AMI Tagging'] = 'PASSED'
            except Exception as exception:
                print("ERROR EKS AMI Tagging", exception)
                self.reason_data = "EKS AMI Tagging %s" % exception
                LOGGER.error(self.reason_data)
                self.res_dict['EKS AMI Tagging'] = 'FAILED'
                return self.res_dict
            return self.res_dict
        elif 'hybrid' in self.res_dict['account_type']:
            try:
                print('Hybrid Inside List Images')
                for region in self.private_regions:
                    ec2_client = self.child_assume_role_session.client('ec2', region_name=region)
                    print("INSIDE REGION - {}", region)
                    response = ec2_client.describe_images(
                        Owners=self.owner,
                        Filters=[
                            {'Name': 'name', 'Values': self.amilist_priv}
                        ]
                    )
                    images = response['Images']
                    self.tag_resources(images, ec2_client)
                self.res_dict['EKS AMI Tagging'] = 'PASSED'
            except Exception as exception:
                print("ERROR EKS AMI Tagging", exception)
                self.reason_data = "EKS AMI Tagging %s" % exception
                LOGGER.error(self.reason_data)
                self.res_dict['EKS AMI Tagging'] = 'FAILED'
                return self.res_dict
            return self.res_dict
        elif 'Managed_Services' in self.res_dict['account_type']:
            try:
                print('Managed Inside List Images')
                for region in self.public_regions:
                    ec2_client = self.child_assume_role_session.client('ec2', region_name=region)
                    print("INSIDE REGION - {}", region)
                    response = ec2_client.describe_images(
                        Owners=self.owner,
                        Filters=[
                            {'Name': 'name', 'Values': self.amilist_pub}
                        ]
                    )
                    images = response['Images']
                    self.tag_resources(images, ec2_client)
                self.res_dict['EKS AMI Tagging'] = 'PASSED'
            except Exception as exception:
                print("ERROR EKS AMI Tagging", exception)
                self.reason_data = "EKS AMI Tagging %s" % exception
                LOGGER.error(self.reason_data)
                self.res_dict['EKS AMI Tagging'] = 'FAILED'
                return self.res_dict
            return self.res_dict
        elif 'Migration' in self.res_dict['account_type']:
            try:
                print('Migration Inside List Images')
                for region in self.public_regions:
                    ec2_client = self.child_assume_role_session.client('ec2', region_name=region)
                    print("INSIDE REGION - {}", region)
                    response = ec2_client.describe_images(
                        Owners=self.owner,
                        Filters=[
                            {'Name': 'name', 'Values': self.amilist_pub}
                        ]
                    )
                    images = response['Images']
                    self.tag_resources(images, ec2_client)
                self.res_dict['EKS AMI Tagging'] = 'PASSED'
            except Exception as exception:
                print("ERROR EKS AMI Tagging", exception)
                self.reason_data = "EKS AMI Tagging %s" % exception
                LOGGER.error(self.reason_data)
                self.res_dict['EKS AMI Tagging'] = 'FAILED'
                return self.res_dict
            return self.res_dict
        elif 'Data-Management' in self.res_dict['account_type']:
            try:
                print('Data-Management Inside List Images')
                for region in self.public_regions:
                    ec2_client = self.child_assume_role_session.client('ec2', region_name=region)
                    print("INSIDE REGION - {}", region)
                    response = ec2_client.describe_images(
                        Owners=self.owner,
                        Filters=[
                            {'Name': 'name', 'Values': self.amilist_pub}
                        ]
                    )
                    images = response['Images']
                    self.tag_resources(images, ec2_client)
                self.res_dict['EKS AMI Tagging'] = 'PASSED'
            except Exception as exception:
                print("ERROR EKS AMI Tagging", exception)
                self.reason_data = "EKS AMI Tagging %s" % exception
                LOGGER.error(self.reason_data)
                self.res_dict['EKS AMI Tagging'] = 'FAILED'
                return self.res_dict
            return self.res_dict

    # Un-Tag EKS AMIs which are above expire.
    def Un_Tag_list_eks_images(self):
        if 'public' in self.res_dict['account_type']:
            try:
                print('Public Inside List Images')
                for region in self.public_regions:
                    ec2_client = self.child_assume_role_session.client('ec2', region_name=region)
                    print("INSIDE REGION - {}", region)
                    response = ec2_client.describe_images(
                        Owners=self.owner,
                        Filters=[
                            {'Name': 'name', 'Values': self.amilist_pub},
                            {'Name': 'tag:platform_image_whitelist', 'Values': ['yes']}
                        ]
                    )
                    images = response['Images']
                    deprecating_Image_list = []
                    for image in images : 
                        I_DateValue = datetime.strptime(image['DeprecationTime'], '%Y-%m-%dT%H:%M:%S.000Z')
                        C_DateValue = datetime.strptime(datetime.today().strftime('%Y-%m-%dT%H:%M:%S.000Z'), '%Y-%m-%dT%H:%M:%S.000Z')
                        Delta = I_DateValue-C_DateValue
                        print(Delta.days)
                        if Delta.days <= 30 :
                            deprecating_Image_list.append(image)
                    if len(deprecating_Image_list) > 0:
                        self.Un_tag_resources(deprecating_Image_list, ec2_client)
            except Exception as exception:
                print("ERROR EKS AMI Tagging", exception)
                return False
            return True
        elif 'private' in self.res_dict['account_type']:
            try:
                print('Public Inside List Images')
                for region in self.private_regions:
                    ec2_client = self.child_assume_role_session.client('ec2', region_name=region)
                    print("INSIDE REGION - {}", region)
                    response = ec2_client.describe_images(
                        Owners=self.owner,
                        Filters=[
                            {'Name': 'name', 'Values': self.amilist_priv},
                            {'Name': 'tag:platform_image_whitelist', 'Values': ['yes']}
                        ]
                    )
                    images = response['Images']
                    deprecating_Image_list = []
                    for image in images : 
                        I_DateValue = datetime.strptime(image['DeprecationTime'], '%Y-%m-%dT%H:%M:%S.000Z')
                        C_DateValue = datetime.strptime(datetime.today().strftime('%Y-%m-%dT%H:%M:%S.000Z'), '%Y-%m-%dT%H:%M:%S.000Z')
                        Delta = I_DateValue-C_DateValue
                        print(Delta.days)
                        if Delta.days <= 30 :
                            deprecating_Image_list.append(image)
                    if len(deprecating_Image_list) > 0:
                        self.Un_tag_resources(deprecating_Image_list, ec2_client)
            except Exception as exception:
                print("ERROR EKS AMI Tagging", exception)
                return False
            return True
        elif 'hybrid' in self.res_dict['account_type']:
            try:
                print('Public Inside List Images')
                for region in self.private_regions:
                    ec2_client = self.child_assume_role_session.client('ec2', region_name=region)
                    print("INSIDE REGION - {}", region)
                    response = ec2_client.describe_images(
                        Owners=self.owner,
                        Filters=[
                            {'Name': 'name', 'Values': self.amilist_priv},
                            {'Name': 'tag:platform_image_whitelist', 'Values': ['yes']}
                        ]
                    )
                    images = response['Images']
                    deprecating_Image_list = []
                    for image in images : 
                        I_DateValue = datetime.strptime(image['DeprecationTime'], '%Y-%m-%dT%H:%M:%S.000Z')
                        C_DateValue = datetime.strptime(datetime.today().strftime('%Y-%m-%dT%H:%M:%S.000Z'), '%Y-%m-%dT%H:%M:%S.000Z')
                        Delta = I_DateValue-C_DateValue
                        print(Delta.days)
                        if Delta.days <= 30 :
                            deprecating_Image_list.append(image)
                    if len(deprecating_Image_list) > 0:
                        self.Un_tag_resources(deprecating_Image_list, ec2_client)
            except Exception as exception:
                print("ERROR EKS AMI Tagging", exception)
                return False
            return True
        elif 'Managed_Services' in self.res_dict['account_type']:
            try:
                print('Public Inside List Images')
                for region in self.public_regions:
                    ec2_client = self.child_assume_role_session.client('ec2', region_name=region)
                    print("INSIDE REGION - {}", region)
                    response = ec2_client.describe_images(
                        Owners=self.owner,
                        Filters=[
                            {'Name': 'name', 'Values': self.amilist_pub},
                            {'Name': 'tag:platform_image_whitelist', 'Values': ['yes']}
                        ]
                    )
                    images = response['Images']
                    deprecating_Image_list = []
                    for image in images : 
                        I_DateValue = datetime.strptime(image['DeprecationTime'], '%Y-%m-%dT%H:%M:%S.000Z')
                        C_DateValue = datetime.strptime(datetime.today().strftime('%Y-%m-%dT%H:%M:%S.000Z'), '%Y-%m-%dT%H:%M:%S.000Z')
                        Delta = I_DateValue-C_DateValue
                        print(Delta.days)
                        if Delta.days <= 30 :
                            deprecating_Image_list.append(image)
                    if len(deprecating_Image_list) > 0:
                        self.Un_tag_resources(deprecating_Image_list, ec2_client)
            except Exception as exception:
                print("ERROR EKS AMI Tagging", exception)
                return False
            return True
        elif 'Migration' in self.res_dict['account_type']:
            try:
                print('Public Inside List Images')
                for region in self.public_regions:
                    ec2_client = self.child_assume_role_session.client('ec2', region_name=region)
                    print("INSIDE REGION - {}", region)
                    response = ec2_client.describe_images(
                        Owners=self.owner,
                        Filters=[
                            {'Name': 'name', 'Values': self.amilist_pub},
                            {'Name': 'tag:platform_image_whitelist', 'Values': ['yes']}
                        ]
                    )
                    images = response['Images']
                    deprecating_Image_list = []
                    for image in images : 
                        I_DateValue = datetime.strptime(image['DeprecationTime'], '%Y-%m-%dT%H:%M:%S.000Z')
                        C_DateValue = datetime.strptime(datetime.today().strftime('%Y-%m-%dT%H:%M:%S.000Z'), '%Y-%m-%dT%H:%M:%S.000Z')
                        Delta = I_DateValue-C_DateValue
                        print(Delta.days)
                        if Delta.days <= 30 :
                            deprecating_Image_list.append(image)
                    if len(deprecating_Image_list) > 0:
                        self.Un_tag_resources(deprecating_Image_list, ec2_client)
            except Exception as exception:
                print("ERROR EKS AMI Tagging", exception)
                return False
            return True
        elif 'Data-Management' in self.res_dict['account_type']:
            try:
                print('Public Inside List Images')
                for region in self.public_regions:
                    ec2_client = self.child_assume_role_session.client('ec2', region_name=region)
                    print("INSIDE REGION - {}", region)
                    response = ec2_client.describe_images(
                        Owners=self.owner,
                        Filters=[
                            {'Name': 'name', 'Values': self.amilist_pub},
                            {'Name': 'tag:platform_image_whitelist', 'Values': ['yes']}
                        ]
                    )
                    images = response['Images']
                    deprecating_Image_list = []
                    for image in images : 
                        I_DateValue = datetime.strptime(image['DeprecationTime'], '%Y-%m-%dT%H:%M:%S.000Z')
                        C_DateValue = datetime.strptime(datetime.today().strftime('%Y-%m-%dT%H:%M:%S.000Z'), '%Y-%m-%dT%H:%M:%S.000Z')
                        Delta = I_DateValue-C_DateValue
                        print(Delta.days)
                        if Delta.days <= 30 :
                            deprecating_Image_list.append(image)
                    if len(deprecating_Image_list) > 0:
                        self.Un_tag_resources(deprecating_Image_list, ec2_client)
            except Exception as exception:
                print("ERROR EKS AMI Tagging", exception)
                return False
            return True

    # Add tags to AMI's in batches
    def create_batch_tag_in_resource(self, ec2_client, item):
        print(item)
        print(type(item))
        try:
            ec2_client.create_tags(Resources=item,
                                   Tags=[{'Key': self.tagging[0],
                                          'Value': self.tagging[1], }, ], )
        except Exception as exception:
            print(str(exception))
            # str_exc = str(exception)
            # if Batch AMI/Snapshot Tag Fails. Tag AMI/Snapshot one at a time for that batch.
            # if  str_exc.find("InvalidSnapshot.NotFound") != -1:
            # self.create_single_tag_in_resource(ec2_client,item)

    # Fetch AMI ID and Snapshot ID's and put it in a list.
    def tag_resources(self, images, ec2_client):
        """Tagging resources"""
        tag_resource_ami = []
        # tag_resource_snap = []
        for image in images:
            try:
                imageid = image['ImageId']
                if 'BETA' not in image['Name']:
                    # print("Name of the Image", image['Name'])
                    tag_resource_ami.append(imageid)
                    # k = image['BlockDeviceMappings'][0].get('Ebs')
                    # snap_id = k['SnapshotId']
                    # tag_resource_snap.append(snap_id)
                    # print(">>>>>", tag_resourcelist)
            except Exception as e:
                print("Name of the Image", image['Name'])
                print(str(e))
                print("Tag Resources")
                print(image)

        # Divide the AMI ID's and Snapshot ID's in batch of 30.
        # tag_resource_ami.extend(tag_resource_snap)
        print(len(tag_resource_ami))
        for i in range(0, len(tag_resource_ami), self.batch_size):
            batch_resource = tag_resource_ami[i:i + self.batch_size]
            self.create_batch_tag_in_resource(ec2_client, batch_resource)

    # AMIs to Un-Tag are as follows.
    def Un_tag_resources(self, images, ec2_client):
        print(len(images))
        un_tag_resource_ami = []
        print("UN-Tag AMI's")
        for image in images:
            imageid = image['ImageId']
            un_tag_resource_ami.append(imageid)
        for i in range(0, len(un_tag_resource_ami), self.batch_size):
            batch_resource = un_tag_resource_ami[i:i + self.batch_size]
            self.create_batch_Un_tag_in_resource(ec2_client, batch_resource)

    # Un-tags to AMI's in batches
    def create_batch_Un_tag_in_resource(self, ec2_client, item):
        print("UN-Tagging List IS : ", item)
        print(type(item))
        try:
            ec2_client.delete_tags(Resources=item,
                                   Tags=[{'Key': self.tagging[0],
                                          'Value': self.tagging[1], }, ], )
        except Exception as exception:
            print(str(exception))

def lambda_handler(event, context):
    """"
    Lambda handler calls the function that Tags the TOE Approved EKS AMI's in the child account
    """
    result_value = {}
    try:
        result_value.update(event)
        tag_eks_ami_account_obj = TagEKSAmiPerAccount(event, context)
        output_value = tag_eks_ami_account_obj.list_eks_images()
        print("Output of the function : " + str(output_value))
        print ("Starting un-tagging of 30 days above expire AMIs")
        if tag_eks_ami_account_obj.Un_Tag_list_eks_images():
            print("Un-tag of 30 days above expire is successful..!!")
        else:
            print("Un-tag of 30 days above expire is successful..!!")
        result_value.update(output_value)
        return result_value

    except Exception as exception:
        print("Error in Lambda Handler", exception)
        result_value['Handler Exception'] = str(exception)
        return result_value
