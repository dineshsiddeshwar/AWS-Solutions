'''
Create SSM Association for Agent installation and domain join process
'''
import logging
import random
import json
import boto3
import time

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
LOGGER.addHandler(CH)


class CreatePlatformAssociation(object):
    """
    Class: InstallCloudhealthagent
    Description: Prerequisite for InstallCloudhealthagent proccess
    """

    def __init__(self, event, context):
        self.event = event
        self.context = context
        LOGGER.info("Event: %s" % self.event)
        LOGGER.info("Context: %s" % self.context)
        try:
            """get relevant input params from event"""
            self.reason_data = ""
            session_client = boto3.Session()
            self.sts_client = session_client.client('sts')
            self.s3_client = session_client.client('s3')
            self.ssm_client = session_client.client('ssm')
            self.child_account_number = event['accountNumber']
            print(self.child_account_number)
            self.account_type = event['ResourceProperties']['AccountType']
            self.private_region = event['SSMParametres']['whitelisted_regions_private'].split(',')
            self.public_region = event['SSMParametres']['whitelisted_regions_public'].split(',')
            self.agent_bucket = event['SSMParametres']['platform_agent_bucket']
            if event['ResourceProperties']['AccountType'] == "private" or event['ResourceProperties']['AccountType'] == "hybrid":
                self.whitelisted_region = self.private_region
            else:
                self.whitelisted_region = self.public_region 
            for region in self.whitelisted_region:
                  self.result_document = {"Platform_Linux_document_creation": {region: ""}}
            for region in self.whitelisted_region:
                  self.result_dict = {"Platform_Linux_Association_creation": {region: ""}}
            self.child_account_arn = "arn:aws:iam::{}:role/AWSControlTowerExecution". \
                format(self.child_account_number)
            self.child_account_sessionname = "linkedAccountSession-" + \
                                             str(random.randint(1, 100000))
            child_account_role_creds = self.sts_client.assume_role \
                (RoleArn=self.child_account_arn, RoleSessionName=self.child_account_sessionname)
            child_credentials = child_account_role_creds.get('Credentials')
            child_access_keyid = child_credentials.get('AccessKeyId')
            child_secret_access_key = child_credentials.get('SecretAccessKey')
            child_session_token = child_credentials.get('SessionToken')
            self.child_assume_role_session = boto3.Session(child_access_keyid, child_secret_access_key,
                                                           child_session_token)
            self.association_id = ""
            self.linux_target_tag = "tag:platform_linux_association"
            self.rate_expression = "rate(240 minutes)"
        except Exception as exception:
            self.reason_data = "Missing required property %s" % exception
            LOGGER.error(self.reason_data)
            raise Exception(str(exception))
            
    def verify_document(self, ssm_childaccount_client, document_name):
        '''
            Verify if the Document is already present or not
        '''
        try:
            response = ssm_childaccount_client.list_documents(
                DocumentFilterList=[
                    {
                        'key': 'Name',
                        'value': document_name
                    },
                ]
            )
            if (response['DocumentIdentifiers'].__len__() > 0):
                return True
            else:
                return False
        except Exception as exception:
            print("Exception occurred while verifying SSM Document {}".format(str(exception)))
            return False
          
    def create_ssm_linux_document(self):
        '''
        This module will creta linux document. If already exists, it will update
        '''
        try:
          LOGGER.info("Creating/Updating Linux Platform Document in the account {0}".format(self.child_account_number))
          if self.account_type == 'private' or self.account_type == 'hybrid':
                self.whitelisted_region = self.private_region
                self.document_path = 'nested-ssm-documnets/platform_linux_private.yaml'
          else:
                self.whitelisted_region = self.public_region
                self.document_path = 'nested-ssm-documnets/platform_linux_public.yaml'
          for region in self.whitelisted_region:
              self.result_document = {"Platform_Linux_Document_creation": {region: ""}}
              
          # Download YAML object from S3
          response = self.s3_client.get_object(Bucket=self.agent_bucket, Key=self.document_path)
          yaml_content = response['Body'].read().decode('utf-8')
            
          for region in self.whitelisted_region:
              count = 0
              self.ssm_childaccount_client = self.child_assume_role_session.client('ssm',
                                                                                     region_name=region)
              try:
                if (not self.verify_document(self.ssm_childaccount_client, "platform_Linux_document")):
                  LOGGER.info("Creating Linux Platform Document in the region {0}".format(region))
                  document_response = self.ssm_childaccount_client.create_document(
                                Content = yaml_content,
                                Name = 'platform_Linux_document',
                                DocumentType='Command',
                                DocumentFormat='YAML',
                                TargetType='/AWS::EC2::Instance',
                                Tags=[
                                    {
                                        'Key': 'platform_donot_delete',
                                        'Value': 'yes'
                                    }
                                ])
                  document_response_status =  document_response['DocumentDescription']['Status']
                  LOGGER.info("waiting for document to be active")
                  while document_response_status != 'Active':
                        if count < 3:
                          time.sleep(5)
                          count +=1
                          describe_document_response = self.ssm_childaccount_client.describe_document(
                                            Name='platform_Linux_document',
                                            DocumentVersion= "$LATEST")
                          document_response_status = describe_document_response['Document']['Status']
                        else:
                          document_response_status = "PENDING"
                          break
                  if document_response_status == 'Active':
                    self.result_document['Platform_Linux_Document_creation'][region] = "PASSED"
                  else:
                    self.result_document['Platform_Linux_Document_creation'][region] = "FAILED"
                else:
                    LOGGER.info("Updating Linux Platform Document in the region {0}".format(region))
                    document_response = self.ssm_childaccount_client.update_document(
                                Content = yaml_content,
                                Name = 'platform_Linux_document',
                                DocumentVersion="$LATEST",
                                DocumentFormat='YAML',
                                TargetType='/AWS::EC2::Instance')
                    document_response_status =  document_response['DocumentDescription']['Status']
                    print("Updated before describe the linux in region",region,document_response_status)
                    while document_response_status != 'Active':
                        if count < 3:
                          print("Sleeping for 5 sec in the region",region)  
                          time.sleep(5)
                          count +=1
                          print("Resuming for 5 sec in the region",region)
                          describe_document_response = self.ssm_childaccount_client.describe_document(
                                            Name='platform_Linux_document',
                                            DocumentVersion= "$LATEST")
                          document_response_status = describe_document_response['Document']['Status']
                        else:
                          document_response_status = "PENDING"
                          break
                    print("Updated the linux in region",region,document_response_status)
                    if document_response_status == 'Active':
                      self.result_document['Platform_Linux_Document_creation'][region] = "PASSED"
                    else:
                      self.result_document['Platform_Linux_Document_creation'][region] = "FAILED"
              except Exception as Ex:
                  LOGGER.error("Exception occured {0}".format(str(Ex)))
                  if 'DuplicateDocumentContent' in str(Ex):
                    LOGGER.info("Document content already exist in the region {0}".format(region))
                    self.result_document['Platform_Linux_Document_creation'][region] = "PASSED"
                  elif 'DocumentAlreadyExists' in str(Ex):
                    LOGGER.info("Document already exist in the region {0}".format(region))
                    self.result_document['Platform_Linux_Document_creation'][region] = "PASSED"
                  else:
                    self.result_document['Platform_Linux_Document_creation'][region] = "FAILED"
          return self.result_document
        except Exception as Ex:
          LOGGER.error("Exception occurred while Creating/Updating Document {}".format(
                str(Ex)))
          return {"Platform_Linux_Document_creation": "FAILED" }


    def file_path(self, region):
        if region == "us-east-1":
            flexera_linux_path = "platform_pvt_flexera_linuxpath_us"
            return flexera_linux_path
        elif region == "eu-west-1":
            flexera_linux_path = "platform_pvt_flexera_linuxpath_eu"
            return flexera_linux_path
        else:
            LOGGER.info("COnsidering EU region by default for all other private region")
            flexera_linux_path = "platform_pvt_flexera_linuxpath_eu"
            return flexera_linux_path
          
    def verify_association(self, ssm_childaccount_client, association_name):
        '''
            Verify if the associatation is already present or not
        '''
        try:
            response = ssm_childaccount_client.list_associations(
                AssociationFilterList=[
                    {
                        'key': 'AssociationName',
                        'value': association_name
                    },
                ]
            )
            if (response['Associations'].__len__() > 0):
                self.association_id = response['Associations'][0]['AssociationId']
                LOGGER.info("Association already exists, updating the association")
                return True
            else:
                LOGGER.info("Association does not exists, creating the association")
                return False
        except Exception as exception:
            print("Exception occurred while verifying SSM Association {}".format(str(exception)))
            return False
    

    def create_ssm_association_private(self):
        '''
        Create the SSM Association in the child account to Run custom document present in the account
        '''
        try:
            ssm_response = self.ssm_client.get_parameters(
                Names=["domainjoin_linuxmainURL", "domainjoin_linuxpreURL","domainjoin_linux_prefilename",
                       "domainjoin_linux_mainfilename"],
                WithDecryption=True)
            for values in ssm_response['Parameters']:
                if values['Name'] == 'domainjoin_linuxmainURL':
                    domainmain_url = values['Value']
                elif values['Name'] == 'domainjoin_linuxpreURL':
                    domainPre_url = values['Value']
                elif values['Name'] == 'domainjoin_linux_prefilename':
                    domainjoinPRe_file = values['Value']
                elif values['Name'] == 'domainjoin_linux_mainfilename':
                    domainjoin_file = values['Value']
            path = self.event['SSMParametres']['platform_linux_dirpath']
            domain_path = self.event['SSMParametres']['domainjoin_linuxpath']
            execution_time = self.event['SSMParametres']['platform_execution_timeout']
            script_path_Ch = self.event['SSMParametres']['platform_pvt_ch_linuxpath']
            script_path_falc = self.event['SSMParametres']['platform_pvt_falcon_linuxpath']
            script_path_rapid = self.event['SSMParametres']['platform_pvt_rapid7_linuxpath']
            file_name_ch = self.event['SSMParametres']['platform_ch_linux_filename']
            file_name_falc = self.event['SSMParametres']['platform_falcon_linux_filename']
            file_name_flex = self.event['SSMParametres']['platform_flexera_linux_filename']
            file_name_rapid = self.event['SSMParametres']['platform_rapid7_linux_filename']
            source_info_falc = '{"path": ' + script_path_falc + '}'
            source_info_ch = '{"path": ' + script_path_Ch + '}'
            source_info_rapid = '{"path": ' + script_path_rapid + '}'
            source_info_preDomain = '{"path": ' + domainmain_url + '}'
            source_info_domain = '{"path": ' + domainPre_url + '}'
            command_line_ch = file_name_ch
            command_line_falc = file_name_falc
            command_line_flex = file_name_flex
            command_line_rapid = file_name_rapid
            command_line_pre = "./" + domainjoinPRe_file
            command_line_domain = "./" + domainjoin_file
            working_directory = path
            execution_timeout = execution_time
            for region in self.private_region:
                count = 0
                flexera_linux_path = self.file_path(region)
                script_path_flex = self.event['SSMParametres'][flexera_linux_path]
                source_info_flex = '{"path": ' + script_path_flex + '}'
                self.ssm_childaccount_client = self.child_assume_role_session.client('ssm',
                                                                                    region_name=region)
                if (not self.verify_association(self.ssm_childaccount_client, "platform_Linux_association")):
                    response = self.ssm_childaccount_client.create_association(
                        Name="platform_Linux_document",
                        DocumentVersion="$LATEST",
                        Parameters={
                            'cloudWatchAction':["configure"],
                            'mode': ["ec2"],
                            'optionalConfigurationSource': ["ssm"],
                            'optionalConfigurationLocationLinux': ["platform_AmazonCloudWatch-Linux"],
                            'optionalRestart': ["yes"],
                            'action': ["Install"],
                            'installationType': ["Uninstall and reinstall"],
                            'name': ["AmazonCloudWatchAgent"],
                            'version': ["latest"],
                            'commandLineForRapidLinux': [command_line_rapid],
                            'commandLineForCloudHealthLinux': [command_line_ch],
                            'commandLineForFalconLinux': [command_line_falc],
                            'commandLineForFlexeraLinux': [command_line_flex],
                            'executionTimeout': [execution_timeout],
                            'sourceInfoForRapidLinux': [source_info_rapid],
                            'sourceInfoForFlexeraLinux': [source_info_flex],
                            'sourceInfoForFalconLinux': [source_info_falc],
                            'sourceInfoForCloudhealthLinux': [source_info_ch],
                            'sourceType': ["S3"],
                            'workingDirectoryLinux': [working_directory],
                            'sourceInfoForLinux': [source_info_preDomain],
                            'sourceInfoForPreLinux': [source_info_domain],
                            'commandLineForLinux': [command_line_domain],
                            'commandLineForPrelinux': [command_line_pre],
                            'workingDirectoryForLinuxDomainJoin': [domain_path]
                        },
                        Targets=[
                            {
                                'Key': self.linux_target_tag,
                                'Values': ['yes']
                            },
                        ],
                        ScheduleExpression=self.rate_expression,
                        AssociationName='platform_Linux_association'
                    )
                    association_status = response['AssociationDescription']['Overview']['Status']
                    while association_status != 'Success':
                        if count < 3:
                            time.sleep(5)
                            count +=1
                            temp_assoc_res = self.ssm_childaccount_client.describe_association(
                                AssociationId=response['AssociationDescription']['AssociationId'],
                                AssociationVersion="$LATEST")
                            association_status = temp_assoc_res['AssociationDescription']['Overview']['Status']
                            if association_status == 'Success':
                                self.result_dict["Platform_Linux_Association_creation"][region] = "SUCCESS"
                                print("SSM Association for Linux agent installation for Linux has been created successfully !!!" + region)
                        else:
                            self.result_dict["Platform_Linux_Association_creation"][region] = "FAILED" 
                            break  
                    
                else:
                    association_response = self.ssm_childaccount_client.list_associations(
                                      AssociationFilterList=[
                                          {
                                              'key': 'AssociationName',
                                              'value': "platform_Linux_association"
                                          },
                                      ]
                                  )
                    self.linux_association_id = association_response['Associations'][0]['AssociationId']
                    response = self.ssm_childaccount_client.update_association(
                        AssociationId=self.linux_association_id,
                        Name="platform_Linux_document",
                        DocumentVersion="$LATEST",
                        Parameters={
                            'cloudWatchAction':["configure"],
                            'mode': ["ec2"],
                            'optionalConfigurationSource': ["ssm"],
                            'optionalConfigurationLocationLinux': ["platform_AmazonCloudWatch-Linux"],
                            'optionalRestart': ["yes"],
                            'action': ["Install"],
                            'installationType': ["Uninstall and reinstall"],
                            'name': ["AmazonCloudWatchAgent"],
                            'version': ["latest"],
                            'commandLineForRapidLinux': [command_line_rapid],
                            'commandLineForCloudHealthLinux': [command_line_ch],
                            'commandLineForFalconLinux': [command_line_falc],
                            'commandLineForFlexeraLinux': [command_line_flex],
                            'executionTimeout': [execution_timeout],
                            'sourceInfoForRapidLinux': [source_info_rapid],
                            'sourceInfoForFlexeraLinux': [source_info_flex],
                            'sourceInfoForFalconLinux': [source_info_falc],
                            'sourceInfoForCloudhealthLinux': [source_info_ch],
                            'sourceType': ["S3"],
                            'workingDirectoryLinux': [working_directory],
                            'sourceInfoForLinux': [source_info_preDomain],
                            'sourceInfoForPreLinux': [source_info_domain],
                            'commandLineForLinux': [command_line_domain],
                            'commandLineForPrelinux': [command_line_pre],
                            'workingDirectoryForLinuxDomainJoin': [domain_path]
                        },
                        Targets=[
                            {
                                'Key': self.linux_target_tag,
                                'Values': ['yes']
                            },
                        ],
                        ScheduleExpression=self.rate_expression,
                        AssociationName='platform_Linux_association'
                    )
                    association_status = response['AssociationDescription']['Overview']['Status']
                    while association_status != 'Success':
                        if count < 3:
                            time.sleep(5)
                            count +=1
                            temp_assoc_res = self.ssm_childaccount_client.describe_association(
                                AssociationId=response['AssociationDescription']['AssociationId'],
                                AssociationVersion="$LATEST")
                            association_status = temp_assoc_res['AssociationDescription']['Overview']['Status']
                            if association_status == 'Success':
                                self.result_dict["Platform_Linux_Association_creation"][region] = "SUCCESS"
                                print("SSM Association for Linux agent installation for Linux has been updated successfully!!!" + region)
                        else:
                            print("SSM Association for Linux agent installation update as failed or the association status is still pending!!!" + region)
                            self.result_dict["Platform_Linux_Association_creation"][region] = "FAILED"
                            break
            return self.result_dict
        except Exception as exception:
            print("Exception occurred while creating SSM Association for linux {}".format(str(exception)))
            return self.result_dict
          
          
    def create_ssm_association_public(self):
        '''
        Create the SSM Association in the child account to Run custom document present in the account
        '''
        try:
            path = self.event['SSMParametres']['platform_linux_dirpath']
            execution_time = self.event['SSMParametres']['platform_execution_timeout']
            script_path_Ch = self.event['SSMParametres']['platform_pub_ch_linuxpath']
            script_path_falc = self.event['SSMParametres']['platform_pub_falcon_linuxpath']
            script_path_rapid = self.event['SSMParametres']['platform_pub_rapid7_linuxpath']
            script_path_flex = self.event['SSMParametres']['platform_pub_flexera_linuxpath']
            file_name_ch = self.event['SSMParametres']['platform_ch_linux_filename']
            file_name_falc = self.event['SSMParametres']['platform_falcon_linux_filename']
            file_name_flex = self.event['SSMParametres']['platform_flexera_linux_filename']
            file_name_rapid = self.event['SSMParametres']['platform_rapid7_linux_filename']
            source_info_falc = '{"path": ' + script_path_falc + '}'
            source_info_ch = '{"path": ' + script_path_Ch + '}'
            source_info_flex = '{"path": ' + script_path_flex + '}'
            source_info_rapid = '{"path": ' + script_path_rapid + '}'
            command_line_ch = file_name_ch
            command_line_falc = file_name_falc
            command_line_flex = file_name_flex
            command_line_rapid = file_name_rapid
            working_directory = path
            execution_timeout = execution_time
            for region in self.public_region:
                count = 0
                self.ssm_childaccount_client = self.child_assume_role_session.client('ssm',
                                                                                    region_name=region)
                if (not self.verify_association(self.ssm_childaccount_client, "platform_Linux_association")):
                    response = self.ssm_childaccount_client.create_association(
                        Name="platform_Linux_document",
                        DocumentVersion="$LATEST",
                        Parameters={
                            'cloudWatchAction':["configure"],
                            'mode': ["ec2"],
                            'optionalConfigurationSource': ["ssm"],
                            'optionalConfigurationLocationLinux': ["platform_AmazonCloudWatch-Linux"],
                            'optionalRestart': ["yes"],
                            'action': ["Install"],
                            'installationType': ["Uninstall and reinstall"],
                            'name': ["AmazonCloudWatchAgent"],
                            'version': ["latest"],
                            'commandLineForRapidLinux': [command_line_rapid],
                            'commandLineForCloudHealthLinux': [command_line_ch],
                            'commandLineForFalconLinux': [command_line_falc],
                            'commandLineForFlexeraLinux': [command_line_flex],
                            'executionTimeout': [execution_timeout],
                            'sourceInfoForRapidLinux': [source_info_rapid],
                            'sourceInfoForFlexeraLinux': [source_info_flex],
                            'sourceInfoForFalconLinux': [source_info_falc],
                            'sourceInfoForCloudhealthLinux': [source_info_ch],
                            'sourceType': ["S3"],
                            'workingDirectoryLinux': [working_directory]
                        },
                        Targets=[
                            {
                                'Key': self.linux_target_tag,
                                'Values': ['yes']
                            },
                        ],
                        ScheduleExpression=self.rate_expression,
                        AssociationName='platform_Linux_association'
                    )
                    association_status = response['AssociationDescription']['Overview']['Status']
                    while association_status != 'Success':
                        if count < 3:
                            time.sleep(5)
                            count +=1
                            temp_assoc_res = self.ssm_childaccount_client.describe_association(
                                AssociationId=response['AssociationDescription']['AssociationId'],
                                AssociationVersion="$LATEST")
                            association_status = temp_assoc_res['AssociationDescription']['Overview']['Status']
                            if association_status == 'Success':
                                self.result_dict["Platform_Linux_Association_creation"][region] = "SUCCESS"
                                print("SSM Association for Linux agent installation for Linux has been created successfully!!!")
                        else:
                            self.result_dict["Platform_Linux_Association_creation"][region] = "FAILED" 
                            break
                                 
                    
                else:
                    association_response = self.ssm_childaccount_client.list_associations(
                                      AssociationFilterList=[
                                          {
                                              'key': 'AssociationName',
                                              'value': "platform_Linux_association"
                                          },
                                      ]
                                  )
                    self.linux_association_id = association_response['Associations'][0]['AssociationId']
                    response = self.ssm_childaccount_client.update_association(
                        AssociationId=self.linux_association_id,
                        Name="platform_Linux_document",
                        DocumentVersion="$LATEST",
                        Parameters={
                            'cloudWatchAction':["configure"],
                            'mode': ["ec2"],
                            'optionalConfigurationSource': ["ssm"],
                            'optionalConfigurationLocationLinux': ["platform_AmazonCloudWatch-Linux"],
                            'optionalRestart': ["yes"],
                            'action': ["Install"],
                            'installationType': ["Uninstall and reinstall"],
                            'name': ["AmazonCloudWatchAgent"],
                            'version': ["latest"],
                            'commandLineForRapidLinux': [command_line_rapid],
                            'commandLineForCloudHealthLinux': [command_line_ch],
                            'commandLineForFalconLinux': [command_line_falc],
                            'commandLineForFlexeraLinux': [command_line_flex],
                            'executionTimeout': [execution_timeout],
                            'sourceInfoForRapidLinux': [source_info_rapid],
                            'sourceInfoForFlexeraLinux': [source_info_flex],
                            'sourceInfoForFalconLinux': [source_info_falc],
                            'sourceInfoForCloudhealthLinux': [source_info_ch],
                            'sourceType': ["S3"],
                            'workingDirectoryLinux': [working_directory]
                        },
                        Targets=[
                            {
                                'Key': self.linux_target_tag,
                                'Values': ['yes']
                            },
                        ],
                        ScheduleExpression=self.rate_expression,
                        AssociationName='platform_Linux_association'
                    )
                    association_status = response['AssociationDescription']['Overview']['Status']
                    while association_status != 'Success':
                        if count < 3:
                            time.sleep(5)
                            count +=1
                            temp_assoc_res = self.ssm_childaccount_client.describe_association(
                                AssociationId=response['AssociationDescription']['AssociationId'],
                                AssociationVersion="$LATEST")
                            association_status = temp_assoc_res['AssociationDescription']['Overview']['Status']
                            if association_status == 'Success':
                                self.result_dict["Platform_Linux_Association_creation"][region] = "SUCCESS"
                                print("SSM Association for Linux agent installation for Linux has been updated successfully!!!")
                        else:
                            print("SSM Association for Linux agent installation update as failed or the association status is still pending!!!" + region)
                            self.result_dict["Platform_Linux_Association_creation"][region] = "FAILED" 
                            break 
            return self.result_dict
        except Exception as exception:
            print("Exception occurred while creating SSM Association for linux {}".format(str(exception)))
            return self.result_dict


def lambda_handler(event, context):
    """"
    Lamda handler that calls the function to Creat SSM Association to Install cloudhealth Agent
    """
    try:
        result_values = {}
        result_values.update(event)
        print("Event {}".format(event))
        create_ssm_obj = CreatePlatformAssociation(event, context)
        create_ssm_obj.create_ssm_linux_document()
        result_values.update(create_ssm_obj.result_document)
        account_type = event['ResourceProperties']['AccountType']
        if 'private' in account_type or 'hybrid' in account_type:
            print('account is private/hybrid')
            create_ssm_obj.create_ssm_association_private()
            result_values.update(create_ssm_obj.result_dict)
            return result_values
        elif 'public' in account_type:
            print('its public account')
            create_ssm_obj.create_ssm_association_public()
            result_values.update(create_ssm_obj.result_dict)
            return result_values
        elif 'Data-Management' in account_type:
            print('its Data Management account')
            create_ssm_obj.create_ssm_association_public()
            result_values.update(create_ssm_obj.result_dict)
            return result_values
        elif 'Migration' in account_type:
            print('its Migration account')
            create_ssm_obj.create_ssm_association_public()
            result_values.update(create_ssm_obj.result_dict)
            return result_values
        else:
            print("SSM association creation failed for linux or account might be a platform account")
            return result_values
    except Exception as exception:
        print("Exception in Lambda Handler", exception)
        return event
