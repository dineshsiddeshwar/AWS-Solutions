import boto3
from datetime import datetime

RESULT_DICT = {}
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# This lambda will be executed in every AWS ChildAccount which runs once in 12 hours and tags the AMIs

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class TagEksamiPerAccount(object):
    """
    # Class: TagEksamiPerAccount
    # Description: AMI Tagging in the child account
    """
    def __init__(self, event, context):

        try:
            self.session_client = boto3.Session()
            self.ssm_client = self.session_client.client('ssm', region_name='us-east-1')
            region_names = self.ssm_client.get_parameter(Name='platform_whitelisted_regions')
            self.region_list = (region_names['Parameter']['Value']).split(',')
            self.eksowner = ['amazon']
            self.eks_amilist = ["amazon-eks-node-*", "amazon-eks-gpu-node-*", "amazon-eks-arm64-node-*", "bottlerocket-aws-k8s*"] 
            self.batch_size = 250
            tagging = self.ssm_client.get_parameter(Name='platform_ami_tags')
            self.tagging = (tagging['Parameter']['Value']).split(',')
            print("AMI tags", self.tagging)
        except Exception as exception:
            print(str(exception))

    # tag platform EKS AMIs in child account.
    def tag_platform_EKS_AMIs_in_account(self):
        try:
            for responseRegion in self.region_list:
                ec2_client = self.session_client.client('ec2', region_name=responseRegion)
                print("ENTERING INTO REGION", responseRegion)
                response = ec2_client.describe_images(
                    Owners=self.eksowner,
                    Filters=[
                        {'Name': 'name', 'Values': self.eks_amilist}
                    ]
                )
                images = response['Images']
                all_images = []
                for image in images:
                    all_images.append(image)
                    
                # Retrieving EKS images with tags already present.
                response_images_with_tags = ec2_client.describe_images(
                    Owners=self.eksowner,
                    Filters=[
                        {'Name': 'name', 'Values': self.eks_amilist},
                        {'Name': 'tag:platform_image_whitelist', 'Values': ['yes']}
                    ]
                )
                images_with_tags = response_images_with_tags['Images']
                images_with_tags_already = []
                for image in images_with_tags:
                    images_with_tags_already.append(image)
                images_to_be_tagged = []
                for element in all_images:
                    if element not in images_with_tags_already:
                        images_to_be_tagged.append(element)
                
            
                deprecating_Image_list = []
                for image in images_to_be_tagged : 
                    I_DateValue = datetime.strptime(image['DeprecationTime'], '%Y-%m-%dT%H:%M:%S.000Z')
                    C_DateValue = datetime.strptime(datetime.today().strftime('%Y-%m-%dT%H:%M:%S.000Z'), '%Y-%m-%dT%H:%M:%S.000Z')
                    Delta = I_DateValue-C_DateValue
                    if Delta.days <= 30 :
                        deprecating_Image_list.append(image)
                final_list = []
                for element in images_to_be_tagged:
                    if element not in deprecating_Image_list:
                        final_list.append(element)
                    
                
                
                self.tag_resources(final_list, ec2_client)
        except Exception as exception:
            print(str(exception))

    # Un_tag platform EKS AMIs in child account.
    def Un_tag_platform_EKS_AMIs_in_account(self):
        try:
            for responseRegion in self.region_list:
                ec2_client = self.session_client.client('ec2', region_name=responseRegion)
                print("ENTERING INTO REGION", responseRegion)
                response = ec2_client.describe_images(
                    Owners=self.eksowner,
                    Filters=[
                        {'Name': 'name', 'Values': self.eks_amilist},
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
                if len(deprecating_Image_list) > 0:
                    self.Un_tag_resources(deprecating_Image_list, ec2_client)
        except Exception as exception:
            print(str(exception))
            return False
        return True
        
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
        print("Tag AMI's")
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
        tag_ami_account_object = TagEksamiPerAccount(event, context)
        tag_ami_account_object.tag_platform_EKS_AMIs_in_account()
        print("platform EKS AMIs whitelisting performed successfully..!!")
        if tag_ami_account_object.Un_tag_platform_EKS_AMIs_in_account() :
            print("platform EKS AMIs which above to deprecate in 30 days are Un-Tagged successfully..!!")
        else:
            print("platform EKS AMIs which above to deprecate in 30 days are Un-Tagged Failed..!!")

        RESULT_DICT['tag_ami_per_account'] = "PASSED"
        return RESULT_DICT
    except Exception as exception:
        print(str(exception))