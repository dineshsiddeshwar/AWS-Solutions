import random
import boto3
from datetime import datetime

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# This lambda will be executed during create/update  AWS ChildAccount
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
VALUE_DICT = {}


class TagAmiPerAccount(object):
    """
    # Class: TagAmiPerAccount
    # Description: AMI Tagging in the child account
    """

    def __init__(self, event, context):
        self.exception = []
        try:
            self.account_number = str(event['accountNumber'])
            secondaryRoleArn = "arn:aws:iam::{}:role/AWSControlTowerExecution".format(self.account_number)
            secondarySessionName = "SecondarySession-" + str(random.randint(1, 100000))
            session = boto3.session.Session()
            sts_client = session.client('sts')
            self.ssm_client = session.client('ssm')
            self.batch_size = 200

            # Fetch the values form SSM Parameters
            toe_public_response = self.ssm_client.get_parameter(Name="TOE_Complaint_OS_Flavours_Public")
            self.toe_complinet_os_public = toe_public_response['Parameter']['Value']
            toe_private_response = self.ssm_client.get_parameter(Name="TOE_Complaint_OS_Flavours_Private")
            self.toe_complinet_os_private = toe_private_response['Parameter']['Value']
            ami_owner_response = self.ssm_client.get_parameter(Name="ami_owner_account")
            self.ami_owner_account = ami_owner_response['Parameter']['Value']
            private_regions_response = self.ssm_client.get_parameter(Name="whitelisted_regions_private")
            self.private_regions_str = private_regions_response['Parameter']['Value']
            public_regions_response = self.ssm_client.get_parameter(Name="whitelisted_regions_public")
            self.public_regions_str = public_regions_response['Parameter']['Value']
            ami_tags_response = self.ssm_client.get_parameter(Name="ami_tags")
            self.ami_tags_str = ami_tags_response['Parameter']['Value']

            self.amilist_pub_with_eks = self.toe_complinet_os_public.split(',')
            self.eks_list = ["amazon-eks-node-*", "amazon-eks-gpu-node-*", "amazon-eks-arm64-node-*"]
            self.amilist_pub = [ami for ami in self.amilist_pub_with_eks if ami not in self.eks_list]
            self.amilist_priv = self.toe_complinet_os_private.split(',')
            self.owner = self.ami_owner_account.split(',')
            self.private_regions = self.private_regions_str.split(',')
            self.public_regions = self.public_regions_str.split(',')
            self.tagging = self.ami_tags_str.split(',')

            # Logging to child account.
            secondaryRoleCreds = sts_client.assume_role(RoleArn=secondaryRoleArn, RoleSessionName=secondarySessionName)
            credentials = secondaryRoleCreds.get('Credentials')
            accessKeyID = credentials.get('AccessKeyId')
            secretAccessKey = credentials.get('SecretAccessKey')
            sessionToken = credentials.get('SessionToken')
            self.assumeRoleSession = boto3.session.Session(accessKeyID, secretAccessKey, sessionToken)
        except Exception as exception:
            print(str(exception))
            self.exception.append(str(exception))
            raise Exception(str(exception))

    # Get AMI's for private child account.
    def tag_ami_private_account(self):
        try:
            for responseRegion in self.private_regions:
                ec2_client = self.assumeRoleSession.client('ec2', region_name=responseRegion)
                child_ssm_client = self.assumeRoleSession.client('ssm', region_name=responseRegion)
                print("ENTERING INTO REGION", responseRegion)
                response = ec2_client.describe_images(
                    Owners=self.owner,
                    Filters=[
                        {'Name': 'name', 'Values': self.amilist_priv},
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
                        response = ec2_client.describe_images(Owners=adhoc_ami_owner_list, Filters=[{'Name': 'name', 'Values': adhoc_amilist}])
                        Adhocimages = response['Images']
                    except Exception as exception:
                        Adhocimages = []
                    
                #Invoke rest part accordingly
                if Adhocimages :
                   images.extend(Adhocimages)

                self.tag_resources(images, ec2_client)
            VALUE_DICT['tag_private_account'] = "PASSED"
            return True, self.exception
        except Exception as exception:
            print(str(exception))
            self.exception.append(str(exception))
            return False, self.exception

    # Get Un-Tag AMI's for private child account.
    def Un_tag_ami_private_account(self):
        try:
            for responseRegion in self.private_regions:
                ec2_client = self.assumeRoleSession.client('ec2', region_name=responseRegion)
                print("ENTERING INTO REGION ", responseRegion)
                response = ec2_client.describe_images(
                    Owners=self.owner,
                    Filters=[
                        {'Name': 'name', 'Values': self.amilist_priv},
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
                    print(Delta.days)
                    if Delta.days <= 30 :
                        deprecating_Image_list.append(image)
                
                if len(deprecating_Image_list) > 0 :
                    print("IMAGES GETTING DEPRECATED IN 30 DAYS ARE  : ", deprecating_Image_list)
                    self.Un_tag_resources(deprecating_Image_list, ec2_client)
            return True
        except Exception as exception:
            print("Exception Happened and Error message is :", str(exception))
            return False

    # Add tags to Single AMI at a time.
    '''
    def create_single_tag_in_resource (self,ec2_client,item):
        for i in item:
            res = str(i)
            try:
                response = ec2_client.create_tags(Resources=[res],
                                                  Tags=[{'Key': self.tagging[0],
                                                         'Value': self.tagging[1], }, ], )
            except Exception as exception:
                print(str(exception))
                str_exc = str(exception)
    '''

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

    # Get AMI's from public child account.
    def tag_ami_public_account(self):
        try:
            for responseRegion in self.public_regions:
                ec2_client = self.assumeRoleSession.client('ec2', region_name=responseRegion)
                child_ssm_client = self.assumeRoleSession.client('ssm', region_name=responseRegion)
                print("ENTERING INTO REGION", responseRegion)
                response = ec2_client.describe_images(
                    Owners=self.owner,
                    Filters=[
                        {'Name': 'name', 'Values': self.amilist_pub},
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
                        response = ec2_client.describe_images(Owners=adhoc_ami_owner_list, Filters=[{'Name': 'name', 'Values': adhoc_amilist}])
                        Adhocimages = response['Images']
                    except Exception as exception:
                        Adhocimages = []
                    
                #Invoke rest part accordingly
                if Adhocimages :
                   images.extend(Adhocimages)

                self.tag_resources(images, ec2_client)
            VALUE_DICT['tag_public_account'] = "PASSED"
            return True, self.exception
        except Exception as exception:
            print(str(exception))
            self.exception.append(str(exception))
            return False, self.exception

    # Get Un-Tag AMI's for public child account.
    def Un_tag_ami_public_account(self):
        try:
            for responseRegion in self.public_regions:
                ec2_client = self.assumeRoleSession.client('ec2', region_name=responseRegion)
                print("ENTERING INTO REGION ", responseRegion)
                response = ec2_client.describe_images(
                    Owners=self.owner,
                    Filters=[
                        {'Name': 'name', 'Values': self.amilist_pub},
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
                    print(Delta.days)
                    if Delta.days <= 30 :
                        deprecating_Image_list.append(image)
                
                if len(deprecating_Image_list) > 0 :
                    print("IMAGES GETTING DEPRECATED IN 30 DAYS ARE  : ", deprecating_Image_list)
                    self.Un_tag_resources(deprecating_Image_list, ec2_client)
            return True
        except Exception as exception:
            print("Exception Happened and Error message is :", str(exception))
            return False

def lambda_handler(event, context):
    """
    Lambda handler calls the function that Tags the TOE Approved AMI's in the child account
    """
    try:
        result_value = {}
        result_value.update(event)
        tag_ami_account_object = TagAmiPerAccount(event, context)
        print("Account number is", event['accountNumber'])
        account_type = event['ResourceProperties']['AccountType']
        print(account_type)

        # if account type is public or private.
        if 'private' in account_type:
            print("account is private")
            output_value, exception = tag_ami_account_object.tag_ami_private_account()
            if tag_ami_account_object.Un_tag_ami_private_account() :
                print("Un-tagging of above to expire within 30 days is successful..!!")
            else:
                print("Un-tagging of above to expire within 30 days is Failed..!!")
        elif 'hybrid' in account_type:
            print("account is hybrid")
            output_value, exception = tag_ami_account_object.tag_ami_private_account()
            if tag_ami_account_object.Un_tag_ami_private_account() :
                print("Un-tagging of above to expire within 30 days is successful..!!")
            else:
                print("Un-tagging of above to expire within 30 days is Failed..!!")
        elif 'public' in account_type:
            print("Account is public")
            output_value, exception = tag_ami_account_object.tag_ami_public_account()
            if tag_ami_account_object.Un_tag_ami_public_account() :
                print("Un-tagging of above to expire within 30 days is successful..!!")
            else:
                print("Un-tagging of above to expire within 30 days is Failed..!!")
        elif 'Managed_Services' in account_type:
            print("Account is Be.Agile")
            output_value, exception = tag_ami_account_object.tag_ami_public_account()
            if tag_ami_account_object.Un_tag_ami_public_account() :
                print("Un-tagging of above to expire within 30 days is successful..!!")
            else:
                print("Un-tagging of above to expire within 30 days is Failed..!!")
        elif 'Migration' in account_type:
            print("Account is Migration")
            output_value, exception = tag_ami_account_object.tag_ami_public_account()
            if tag_ami_account_object.Un_tag_ami_public_account() :
                print("Un-tagging of above to expire within 30 days is successful..!!")
            else:
                print("Un-tagging of above to expire within 30 days is Failed..!!")
        elif 'Data-Management' in account_type:
            print("Account is Data Management")
            output_value, exception = tag_ami_account_object.tag_ami_public_account()
            if tag_ami_account_object.Un_tag_ami_public_account() :
                print("Un-tagging of above to expire within 30 days is successful..!!")
            else:
                print("Un-tagging of above to expire within 30 days is Failed..!!")
        result = {}

        # Return Status response back to the Step Function
        if output_value == True:
            result['AMITaggingStatus'] = True
            print("No output to pass to the next state")
        else:
            result['AMITaggingStatus'] = False

        print("printing VALUE_DICT", VALUE_DICT)
        result.update(VALUE_DICT)
        return result

    except Exception as exception:
        print(str(exception))
        result = {}
        result['AMITaggingStatus'] = False
        error_exception = []
        error_exception.append(exception)
        return result
