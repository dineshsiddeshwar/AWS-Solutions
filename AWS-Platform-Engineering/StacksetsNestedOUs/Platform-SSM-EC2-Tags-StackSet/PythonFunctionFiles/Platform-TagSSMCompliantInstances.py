import boto3

"""
This Lambda Function is used to add agent installation Tags to the EC2 instancess that are created in child account
"""
class SSMTaggingManagment(object):

    def __init__(self, event, context):
        self.event = event
        self.context = context
        session_client = boto3.Session()
        self.ssm_client = session_client.client('ssm' ,region_name="us-east-1")
        self.ec2_client = boto3.client('ec2')

        ## Check if it is RESPC Account
        platform_IsRESPCAccount = self.ssm_client.get_parameter(Name='/Platform-Tag/platform_IsRESPCAccount')
        self.platform_IsRESPCAccount = platform_IsRESPCAccount['Parameter']['Value']
        print("platform Is RESPC Account", self.platform_IsRESPCAccount)

        ## Get type of account
        platform_AccountType = self.ssm_client.get_parameter(Name='/Platform-Tag/platform_AccountType')
        self.platform_AccountType = platform_AccountType['Parameter']['Value']
        print("platform Account type", self.platform_AccountType)

        # Windows Tags
        self.window_tags = [{'Key': 'platform_ssminstall', 'Value': 'yes'},
                            {'Key': 'platform_install_patch', 'Value': 'yes'},
                            {'Key': 'platform_windows_association', 'Value': 'yes'}
                            ]
        
        self.linux_tags = [ {'Key': 'platform_install_patch', 'Value': 'yes'},
                            {'Key': 'platform_ssminstall', 'Value': 'yes'},
                            {'Key': 'platform_linux_association', 'Value': 'yes'}
                             ]
        
        self.eks_tags = [{'Key': 'platform_ssminstall', 'Value': 'no'},
                         {'Key': 'platform_install_patch', 'Value': 'no'},
                         {'Key': 'platform_domainjoin_linux', 'Value': 'no'},
                         {'Key': 'platform_linux_association', 'Value': 'no'}
                         ]
        
        self.exception_windows_tags = [{'Key': 'platform_flexera_windows', 'Value': 'yes'},
                                                {'Key': 'platform_rapid7_windows', 'Value': 'yes'},
                                                {'Key': 'platform_cloudwatch', 'Value': 'yes'},
                                                {'Key': 'platform_falcon_windows', 'Value': 'yes'},
                                                {'Key': 'platform_cloudhealth_windows', 'Value': 'yes'},
                                                {'Key': 'platform_ssminstall', 'Value': 'yes'},
                                                {'Key': 'platform_install_patch', 'Value': 'yes'},
                                                {'Key': 'platform_cloudwatch_windows', 'Value': 'yes'},
                                                {'Key': 'platform_domainjoin_windows', 'Value': 'yes'},
                                                {'Key': 'platform_windows_association', 'Value': 'no'},
                                                ]
        
        
        
        self.exception_linux_tags = [{'Key': 'platform_flexera_linux', 'Value': 'yes'},
                                                {'Key': 'platform_rapid7_linux', 'Value': 'yes'},
                                                {'Key': 'platform_cloudwatch', 'Value': 'yes'},
                                                {'Key': 'platform_falcon_linux', 'Value': 'yes'},
                                                {'Key': 'platform_cloudhealth_linux', 'Value': 'yes'},
                                                {'Key': 'platform_ssminstall', 'Value': 'yes'},
                                                {'Key': 'platform_install_patch', 'Value': 'yes'},
                                                {'Key': 'platform_cloudwatch_linux', 'Value': 'yes'},
                                                {'Key': 'platform_domainjoin_linux', 'Value': 'yes'},
                                                {'Key': 'platform_linux_association', 'Value': 'no'}
                                                ]
        
        
        
        if "Yes" in self.platform_IsRESPCAccount and "hybrid" in  self.platform_AccountType :
            print("adding RESPC specific tags..")
            for i in range(len(self.exception_windows_tags)):
                if self.exception_windows_tags[i]['Key'] == "platform_domainjoin_windows":
                    del self.exception_windows_tags[i]
                    break
            self.exception_windows_tags.append({'Key': 'platform_aws_managed_ad_domainjoin', 'Value': 'yes'})
            print("Added for Windows EC2 instances..")

            for i in range(len(self.exception_linux_tags)):
                if self.exception_linux_tags[i]['Key'] == "platform_domainjoin_linux":
                    del self.exception_linux_tags[i]
                    break
            self.exception_linux_tags.append({'Key': 'platform_aws_managed_ad_domainjoin', 'Value': 'yes'})
            print("Added for linux EC2 instances..")
            
            for i in range(len(self.eks_tags)):
                if self.eks_tags[i]['Key'] == "platform_domainjoin_linux":
                    del self.eks_tags[i]
                    break
            self.eks_tags.append({'Key': 'platform_aws_managed_ad_domainjoin', 'Value': 'no'})
            print("Added for Eks EC2 instances..")


    """
    Attach tags to the EC2 instances based on if they are windows or linux instances.
    """
    def describe_nonroutablesubnet_function(self, subnet_id):
        try:
            print("Inside Non routable function")
            count = 0
            describe_subnet = self.ec2_client.describe_subnets(SubnetIds=[subnet_id])
            nonroutable_Tag = describe_subnet['Subnets'][0]['Tags']
            if nonroutable_Tag == []:
                return False
            for tag in nonroutable_Tag:
                if tag['Key'] == "platform-vpc-subnet-non-routable" and tag['Value'] == "Yes":
                    count += 1
                else:
                    print("No Tag found")
            if count == 1:
                print("Ending Non routable function")
                return True
            else:
                return False
        except Exception as e:
            raise Exception(str(e))   
            return False
        

    def tagging_exception_handler(self, platform_type, tags_response):
        '''
        This method is used to handle exceptions while attaching tags
        '''
        try:
            print("Inside agent agent exception handler")
            agent_exception_status = False
            if platform_type == "Windows":
                exception_tags = self.exception_windows_tags
            else:
                exception_tags = self.exception_linux_tags

            for tag in tags_response['Tags']:
                if tag['Key'] == 'platform_agent_exception_flexera':
                    agent_exception_status = True
                    for tag in exception_tags:
                        if 'platform_flexera' in tag['Key']:
                            tag['Value'] = 'no'
                            break
                if tag['Key'] == 'platform_agent_exception_rapid7':
                    agent_exception_status = True
                    for tag in exception_tags:
                        if 'platform_rapid7' in tag['Key']:
                            tag['Value'] = 'no'
                            break
                if tag['Key'] == 'platform_agent_exception_cloudwatch':
                    agent_exception_status = True
                    for tag in exception_tags:
                        if 'platform_cloudwatch' in tag['Key']:
                            tag['Value'] = 'no'
                            break
                if tag['Key'] == 'platform_agent_exception_falcon':
                    agent_exception_status = True
                    for tag in exception_tags:
                        if 'platform_falcon' in tag['Key']:
                            tag['Value'] = 'no'
                            break
                if tag['Key'] == 'platform_agent_exception_cloudhealth':
                    agent_exception_status = True
                    for tag in exception_tags:
                        if 'platform_cloudhealth' in tag['Key']:
                            tag['Value'] = 'no'
                            break
            if agent_exception_status:
                return exception_tags, True
            
            return tags_response, False
        except Exception as e:
            raise Exception(str(e))

    def delete_old_tags(self, instance_id, platform_type, check_tags):
        '''
        This function is used to remove old tags from the ec2 instances for agent installation
        '''
        try:
            print("Inside delete Old tags")
            if platform_type == "Windows":
                tags_to_delete = [{'Key': 'platform_flexera_windows', 'Value': 'yes'},
                                  {'Key': 'platform_rapid7_windows', 'Value': 'yes'},
                                  {'Key': 'platform_cloudwatch', 'Value': 'yes'},
                                  {'Key': 'platform_falcon_windows', 'Value': 'yes'},
                                  {'Key': 'platform_cloudhealth_windows', 'Value': 'yes'},
                                  {'Key': 'platform_domainjoin_windows', 'Value': 'yes'},
                                  {'Key': 'platform_cloudwatch_windows', 'Value': 'yes'}
                                  ]
            else:
                tags_to_delete = [{'Key': 'platform_flexera_linux', 'Value': 'yes'},
                                  {'Key': 'platform_rapid7_linux', 'Value': 'yes'},
                                  {'Key': 'platform_cloudwatch', 'Value': 'yes'},
                                  {'Key': 'platform_falcon_linux', 'Value': 'yes'},
                                  {'Key': 'platform_cloudhealth_linux', 'Value': 'yes'},
                                  {'Key': 'platform_domainjoin_linux', 'Value': 'yes'},
                                  {'Key': 'platform_cloudwatch_linux', 'Value': 'yes'}
                                  ]
                
            # Iterate over tags to delete
            for tag in tags_to_delete:
                if tag['Key'] in check_tags:
                    self.ec2_client.delete_tags(Resources=[instance_id], Tags=[tag])
                else:
                    print("No agent specific tag on ec2, hence skipping")
            print("Deleted Old tags")
        except Exception as e:
            raise Exception(str(e))
        

    def attach_tags(self,ssm_response, tags_response, instance_id, image_name, check_nonroutable_subnet_tag):
        try:
            print("Inside attach tag function")
            platform_type = ssm_response['InstanceInformationList'][0]['PlatformType']
            
            if check_nonroutable_subnet_tag == True:
                print("Instance associated with non-routable subnet")
                if 'amazon-eks' in image_name or 'bottlerocket-aws-k8s' in image_name :
                    initial_tags = self.eks_tags
                elif platform_type == "Windows":
                    initial_tags = self.exception_windows_tags
                    for tag in initial_tags:
                        if tag['Key'] == 'platform_domainjoin_windows':
                            tag['Value'] = 'no'
                            break
                else:
                    initial_tags = self.exception_linux_tags
                    for tag in initial_tags:
                        if tag['Key'] == 'platform_domainjoin_linux':
                            tag['Value'] = 'no'
                            break
            elif "Yes" in self.platform_IsRESPCAccount and "hybrid" in  self.platform_AccountType :
                print("tagging ec2 in RESPC account")
                if 'amazon-eks' in image_name or 'bottlerocket-aws-k8s' in image_name :
                    initial_tags = self.eks_tags
                elif platform_type == "Windows":
                    initial_tags = self.exception_windows_tags
                else:
                    initial_tags = self.exception_linux_tags
            else:
                print("tagging regular instances")
                if 'amazon-eks' in image_name or 'bottlerocket-aws-k8s' in image_name :
                    initial_tags = self.eks_tags
                elif platform_type == "Windows":
                    initial_tags = self.window_tags
                else:
                    initial_tags = self.linux_tags

            if len(tags_response['Tags']) == 0:
                print("Inside length")
                add_tag_response = self.ec2_client.create_tags(Resources=[instance_id], Tags=initial_tags)
            else:
                print("Adding missing  tags")
                attached_tags = []
                check_tags = []
                for tag in tags_response['Tags']:
                    check_tags.append(tag['Key'])

                #cheking if any old exception tags are present on an EC2 instance
                print("checking for agent exception tags")
                exception_tags, exception_status = self.tagging_exception_handler(platform_type, tags_response)

                #One time activity to remove old tags
                if exception_status == True:
                    initial_tags = exception_tags
                else:
                    self.delete_old_tags(instance_id, platform_type, check_tags)
                    
                for tag in initial_tags:
                    if tag['Key'] not in check_tags:
                        attached_tags.append(tag)
                if len(attached_tags) != 0:
                    add_tag_response = self.ec2_client.create_tags(Resources=[instance_id], Tags=attached_tags)
        except Exception as e:
            raise Exception(str(e))

    """
    Find the isntancess that are reporting to SSM and Tag those instances in the business account
    """
    def ssmTags(self):
        try:
            print("Start check_ssm_agent")
            token = ""
            child_assume_role_session = boto3.Session()
            self.ec2_client = child_assume_role_session.client('ec2')
            ec2_desc_response = self.ec2_client.describe_instances(NextToken=token)
            for result in ec2_desc_response['Reservations']:
                for instances_list in result['Instances']:
                    instance_id = instances_list['InstanceId']
                    image_id = instances_list['ImageId']
                    image_name = '' 
                    subnet_id = instances_list['NetworkInterfaces'][0]['SubnetId']
                    check_nonroutable_subnet_tag = self.describe_nonroutablesubnet_function(subnet_id)
                    print("######### Checking instance ",instance_id)
                    describe_image_response = self.ec2_client.describe_images(ImageIds=[image_id])
                    if describe_image_response and describe_image_response['Images'] == []:
                        print("No image found with Image Id ",image_id)
                    else:
                        image_name = describe_image_response['Images'][0]['Name']
                        print("Image name for Instance id",instance_id, "is",image_name )
                    ssm_response = child_assume_role_session.client('ssm').describe_instance_information(
                        InstanceInformationFilterList=[
                            {
                                'key': 'InstanceIds',
                                'valueSet': [
                                    instance_id,
                                ]
                            },
                        ]
                    )
                    print("SSM Response",ssm_response)

                    if ('amazon-eks' in image_name) or ('bottlerocket-aws-k8s' in image_name) or (len(ssm_response['InstanceInformationList']) > 0):
                        tags_response = self.ec2_client.describe_tags(
                            Filters=[{'Name': 'resource-id', 'Values': [instance_id, ], }, ], )                    
                        self.attach_tags(ssm_response, tags_response, instance_id, image_name, check_nonroutable_subnet_tag)
                    else:
                        print("No EKS instance or instance reporting to SSM found to tag")
            return True

        except Exception as exception:
            print(exception)
            return False

def lambda_handler(event, context):
    ssmTaggingManagment = SSMTaggingManagment(event, context)
    return ssmTaggingManagment.ssmTags()