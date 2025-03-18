import random
import boto3
import json
import sys
from datetime import datetime

class TagAMIDuringOnboarding(object):
    """
    # Class: TagAmiPerAccount
    # Description: AMI Tagging in the child account
    """

    def __init__(self, event):
        try:
            self.account_number = str(event['ProvisionedProduct']['AccountNumber'])
            secondaryRoleArn = "arn:aws:iam::{}:role/AWSControlTowerExecution".format(self.account_number)
            secondarySessionName = "SecondarySession-" + str(random.randint(1, 100000))
            session = boto3.session.Session()
            sts_client = session.client('sts')
            self.ssm_client = session.client('ssm')
            self.batch_size = 600

            self.toe_amis_allowed = event['SSMParameters']['TOE_Complaint_OS_Flavours_Private'] if "Private" in event['ProvisionedProduct']['OU'] or "Hybrid" in event['ProvisionedProduct']['OU'] else event['SSMParameters']['TOE_Complaint_OS_Flavours_Public']
            self.amilist = self.toe_amis_allowed.split(',')
            self.eks_list = ["amazon-eks-node-*", "amazon-eks-gpu-node-*", "amazon-eks-arm64-node-*"]
            self.toeamisallowed = [ami for ami in self.amilist if ami not in self.eks_list]
            print("AMIs allowed", self.toeamisallowed)

            self.regions_str = event['SSMParameters']['whitelisted_regions_private'] if "Private" in event['ProvisionedProduct']['OU'] or "Hybrid" in event['ProvisionedProduct']['OU'] else event['SSMParameters']['whitelisted_regions_public']
            self.regions = self.regions_str.split(',')
            print("Regions allowed", self.regions)

            self.owner = (event['SSMParameters']['ami_owner_account']).split(',')
            print("AMIs owner list", self.owner)
          
            self.tagging = (event['SSMParameters']['ami_tags']).split(',')
            print("AMI tag key value", self.tagging)

            secondaryRoleCreds = sts_client.assume_role(RoleArn=secondaryRoleArn, RoleSessionName=secondarySessionName)
            credentials = secondaryRoleCreds.get('Credentials')
            accessKeyID = credentials.get('AccessKeyId')
            secretAccessKey = credentials.get('SecretAccessKey')
            sessionToken = credentials.get('SessionToken')
            self.assumeRoleSession = boto3.session.Session(accessKeyID, secretAccessKey, sessionToken)
        except Exception as exception:
            print(str(exception))

    def tag_ami_account(self):
        try:
            for responseRegion in self.regions:
                ec2_client = self.assumeRoleSession.client('ec2', region_name=responseRegion)
                child_ssm_client = self.assumeRoleSession.client('ssm', region_name=responseRegion)
                print("ENTERING INTO REGION", responseRegion)
                response = ec2_client.describe_images(
                    Owners=self.owner,
                    Filters=[
                        {'Name': 'name', 'Values': self.toeamisallowed},
                        {'Name': 'architecture', 'Values': ['x86_64']}
                    ]
                )
                images = response['Images']

                try:
                    adhoc_amilist = []
                    toe_adhoc_response = child_ssm_client.get_parameter(Name="Adhoc_TOE_Complaint_OS_Flavours")
                    adhoc_amilist_values = toe_adhoc_response['Parameter']['Value']
                    adhoc_amilist = adhoc_amilist_values.split(',')
                except Exception as exception:
                    adhoc_amilist = []
 
                try:
                    adhoc_ami_owner_list = []
                    toe_adhoc_ami_owner_response = child_ssm_client.get_parameter(Name="Adhoc_AMI_Owner_Account")
                    adhoc_ami_owner_values = toe_adhoc_ami_owner_response['Parameter']['Value']
                    adhoc_ami_owner_list = adhoc_ami_owner_values.split(',')
                except Exception as exception:
                    adhoc_ami_owner_list = []
                
                Adhocimages = []
                if adhoc_amilist and adhoc_ami_owner_list:
                    try:
                        response = ec2_client.describe_images(Owners=adhoc_ami_owner_list, Filters=[{'Name': 'name', 'Values': adhoc_amilist}])
                        Adhocimages = response['Images']
                    except Exception as exception:
                        Adhocimages = []

                if Adhocimages :
                   images.extend(Adhocimages)

                self.tag_resources(images, ec2_client)

            return True
        except Exception as exception:
            print(str(exception))
            return False

    def create_batch_tag_in_resource(self, ec2_client, item):
        print(item)
        print(type(item))
        try:
            ec2_client.create_tags(Resources=item,
                                   Tags=[{'Key': self.tagging[0],
                                          'Value': self.tagging[1], }, ], )
        except Exception as exception:
            print(str(exception))

    def tag_resources(self, images, ec2_client):
        tag_resource_ami = []
        for image in images:
            try:
                imageid = image['ImageId']
                if 'BETA' not in image['Name']:
                    tag_resource_ami.append(imageid)
            except Exception as e:
                print("Name of the Image", image['Name'])
                print(str(e))
                print("Tag Resources")
                print(image)
        print(len(tag_resource_ami))
        for i in range(0, len(tag_resource_ami), self.batch_size):
            batch_resource = tag_resource_ami[i:i + self.batch_size]
            self.create_batch_tag_in_resource(ec2_client, batch_resource)

    # Get Un-Tag AMI's for private child account.
    def Un_tag_ami_account(self):
        try:
            for responseRegion in self.regions:
                ec2_client = self.assumeRoleSession.client('ec2', region_name=responseRegion)
                print("ENTERING INTO REGION ", responseRegion)
                response = ec2_client.describe_images(
                    Owners=self.owner,
                    Filters=[
                        {'Name': 'name', 'Values': self.toeamisallowed},
                        {'Name': 'architecture', 'Values': ['x86_64']},
                        {'Name': 'tag:platform_image_whitelist', 'Values': ['yes']}
                    ]
                )
                images = response['Images']
                deprecating_Image_list = []
                for image in images : 
                    I_DateValue = datetime.strptime(image['DeprecationTime'], '%Y-%m-%dT%H:%M:%S.000Z')
                    C_DateValue = datetime.strptime(datetime.today().strftime('%Y-%m-%dT%H:%M:%S.000Z'), '%Y-%m-%dT%H:%M:%S.000Z')
                    Delta = I_DateValue-C_DateValue
                    if Delta.days <= 30 :
                        deprecating_Image_list.append(image)
                
                if len(deprecating_Image_list) > 0 :
                    print("IMAGES GETTING DEPRECATED IN 30 DAYS ARE  : ", deprecating_Image_list)
                    self.Un_tag_resources(deprecating_Image_list, ec2_client)
            return True
        except Exception as exception:
            print("Exception Happened and Error message is :", str(exception))
            return False

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

try:
    local_file_path = str(sys.argv[1])+"parameters.json"
    print("Parameters local file path: ", local_file_path)
    with open(local_file_path) as json_data:
        parameters_data = json.load(json_data)
    print(parameters_data)
    if parameters_data : 
        print("parameters are loaded in json format, invokes tag_ami_account function..")
        TagAMI = TagAMIDuringOnboarding(parameters_data)
        if TagAMI.tag_ami_account():
            print("Invoke Tag AMIs per account is success..!!")
        else:
            print("Invoke Tag AMIs per account is fialed..!!")
        if TagAMI.Un_tag_ami_account() :
            print("Un-tagging of above to expire within 30 days is successful..!!")
        else:
            print("Un-tagging of above to expire within 30 days is Failed..!!")
except Exception as ex:
    print("There is an error %s", str(ex))

