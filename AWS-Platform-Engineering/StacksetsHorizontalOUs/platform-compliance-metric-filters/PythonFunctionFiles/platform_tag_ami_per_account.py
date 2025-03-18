import boto3
from datetime import datetime

RESULT_DICT = {}
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# This lambda will be executed in every AWS ChildAccount which runs once in 12 hours and tags the AMIs

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class TagamiPerAccount(object):
    """
    # Class: TagamiPerAccount
    # Description: AMI Tagging in the child account
    """
    def __init__(self, event, context):

        try:
            self.session_client = boto3.Session()
            self.ssm_client = self.session_client.client('ssm', region_name='us-east-1')
            region_names = self.ssm_client.get_parameter(Name='platform_whitelisted_regions')
            self.region_list = (region_names['Parameter']['Value']).split(',')
            self.eks_list = ["amazon-eks-node-*", "amazon-eks-gpu-node-*", "amazon-eks-arm64-node-*"]
            amilist = self.ssm_client.get_parameter(Name='platform_TOE_Complaint_OS_list')
            self.amilist_with_eks = (amilist['Parameter']['Value']).split(',')
            self.amilist = [ami for ami in self.amilist_with_eks if ami not in self.eks_list]
            print("AMI List for account are:", self.amilist)
            owner = self.ssm_client.get_parameter(Name='platform_ami_owner_account')
            self.owner = (owner['Parameter']['Value']).split(',')
            self.eksowner = ['amazon']
            self.batch_size = 200
            tagging = self.ssm_client.get_parameter(Name='platform_ami_tags')
            self.tagging = (tagging['Parameter']['Value']).split(',')
            print("AMI tags", self.tagging)
        except Exception as exception:
            print(str(exception))


    # tag platform AMIs in child account.
    def tag_platform_AMIs_in_account(self):
        try:
            for responseRegion in self.region_list:
                ec2_client = self.session_client.client('ec2', region_name=responseRegion)
                child_ssm_client = self.session_client.client('ssm', region_name=responseRegion)
                print("ENTERING INTO REGION", responseRegion)
                response = ec2_client.describe_images(
                    Owners=self.owner,
                    Filters=[
                        {'Name': 'name', 'Values': self.amilist},
                        {'Name': 'architecture', 'Values': ['x86_64']}
                    ]
                )
                images = response['Images']
                #adhoc amis whitelisting feature
                #get adhoc ami list of location if any
                try:
                    adhoc_amilist = []
                    toe_adhoc_response = child_ssm_client.get_parameter(Name="Adhoc_TOE_Complaint_OS_Flavours")
                    adhoc_amilist_values = toe_adhoc_response['Parameter']['Value']
                    adhoc_amilist = adhoc_amilist_values.split(',')
                except Exception as exception:
                    adhoc_amilist = []
 
                #get adhoc ami owner accounts list of location if any
                try:
                    adhoc_ami_owner_list = []
                    toe_adhoc_ami_owner_response = child_ssm_client.get_parameter(Name="Adhoc_AMI_Owner_Account")
                    adhoc_ami_owner_values = toe_adhoc_ami_owner_response['Parameter']['Value']
                    adhoc_ami_owner_list = adhoc_ami_owner_values.split(',')
                except Exception as exception:
                    adhoc_ami_owner_list = []
                
                #retrieve all adhoc images if any
                Adhocimages = []
                if adhoc_amilist and adhoc_ami_owner_list:
                    try:
                        response = ec2_client.describe_images(Owners=adhoc_ami_owner_list, Filters=[{'Name': 'name', 'Values': adhoc_amilist},{'Name': 'architecture', 'Values': ['x86_64']}])
                        Adhocimages = response['Images']
                    except Exception as exception:
                        Adhocimages = []
                    
                #Invoke rest part accordingly
                if Adhocimages :
                   images.extend(Adhocimages)

                self.tag_resources(images, ec2_client)
            RESULT_DICT['tag_ami_per_account'] = "PASSED"
        except Exception as exception:
            print(str(exception))

    # Un_tag platform AMIs in child account.
    def Un_tag_platform_AMIs_in_account(self):
        try:
            for responseRegion in self.region_list:
                ec2_client = self.session_client.client('ec2', region_name=responseRegion)
                print("ENTERING INTO REGION", responseRegion)
                response = ec2_client.describe_images(
                    Owners=self.owner,
                    Filters=[
                        {'Name': 'name', 'Values': self.amilist},
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
        except Exception as exception:
            print(str(exception))
            return False
        return True
    # Add tags to AMI's in batches
    def create_batch_tag_in_resource(self, ec2_client, item):
        print(item)
        print(type(item))
        print("Tag Batch AMI's")
        try:
            ec2_client.create_tags(Resources=item,
                                   Tags=[{'Key': self.tagging[0],
                                          'Value': self.tagging[1], }, ], )
        except Exception as exception:
            print(str(exception))
            str_exc = str(exception)
            print("Exception", str_exc)
           
    # Fetch AMI ID and Snapshot ID's and put it in a list.
    def tag_resources(self, images, ec2_client):
        """Tagging resources"""
        tag_resource_ami = []
        # tag_resource_snap = []
        print("Tag AMI's")
        for image in images:
            try:
                imageid = image['ImageId']
                if 'BETA' not in image['Name']:
                    # print("Name of the Image", image['Name'])
                    tag_resource_ami.append(imageid)
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
    """
    Lambda handler calls the function that Tags the TOE Approved AMI's in the child account
    """
    try:
        tag_ami_account_object = TagamiPerAccount(event, context)
        tag_ami_account_object.tag_platform_AMIs_in_account()
        print("platform AMIs whitelisting performed successfully..!!")
        if tag_ami_account_object.Un_tag_platform_AMIs_in_account():
            print("platform AMIs which above to deprecate in 30 days are Un-Tagged successfully..!!")
        else:
            print("platform AMIs which above to deprecate in 30 days are Un-Tagged Failed..!!")

        RESULT_DICT['tag_ami_per_account'] = "PASSED"
        return RESULT_DICT
    except Exception as exception:
        print(str(exception))