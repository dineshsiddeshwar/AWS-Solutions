# This lambda was updated as part of RARS Migration from 1.0 to 2.0
from ast import Return
import boto3
import json
import os
import datetime
import base64
import requests
from botocore.exceptions import ClientError

class SendQueueMessageRecieverBox(object):
    def __init__(self, event, context):
        self.exception = []
        self.event = event
        self.context = context
        session_client = boto3.session.Session()
        self.sqs_client = session_client.client('sqs', region_name="us-east-1")
        self.secretManager_client = session_client.client('secretsmanager', region_name="us-east-1")
        self.s3_client = boto3.resource('s3')
        SSM_client = session_client.client('ssm', region_name="us-east-1")
        snow_integration_log_bucket  = SSM_client.get_parameter(Name='SnowIntegrationLogBucket')
        self.snow_integration_log_bucket = snow_integration_log_bucket['Parameter']['Value']

    def get_secret(self):
        secret_name = "IntegrationCreds-RARS"
        try:
            get_secret_value_response = self.secretManager_client.get_secret_value( SecretId=secret_name)
        except ClientError as e:
            if e.response['Error']['Code'] == 'DecryptionFailureException':
                raise e
            elif e.response['Error']['Code'] == 'InternalServiceErrorException':
                raise e
            elif e.response['Error']['Code'] == 'InvalidParameterException':
                raise e
            elif e.response['Error']['Code'] == 'InvalidRequestException':
                raise e
            elif e.response['Error']['Code'] == 'ResourceNotFoundException':
                raise e
        else:
            if 'SecretString' in get_secret_value_response:
                secret = get_secret_value_response['SecretString']
                return secret
            else:
                decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
                return decoded_binary_secret

    def get_SIMAAS_BearerToken(self, url, client_id, client_secret,username,password):
        try:
            payload='client_id='+client_id+'&client_secret='+client_secret+'&grant_type=password'+'&username='+username+'&password='+password
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            response = requests.request("POST", url, headers=headers, data=payload)
            bearer_token = json.loads(response.text)
        except Exception as exception:
            print("Exception while getting SIMAAS Bearer token and error is {}".format(exception))
        else:
            if bearer_token :
                print("bearer token has been returned...")
                return bearer_token
            else :
                print("No bearer token has been returned...")

    def send_Snow_Response (self, event):
        try:
            api_data = json.loads(self.get_secret())
            if api_data :
                print("retrieved AWS secret manager data..")
                Bearer_token_data = self.get_SIMAAS_BearerToken(api_data['SIMAAS_URL'], api_data['SIMAAS_client_id'], api_data['SIMAAS_client_secret'],api_data['SIMAAS_username'],api_data['SIMAAS_password'])
                if Bearer_token_data :
                    print("SIMAAS bearer toaken is retrieved ...")
                    dynamicnowdata = datetime.datetime.now().strftime("%Y-%m-%d %I:%M:%S")
                    print("dynamic now date is framed..")
                    payload = json.dumps({
                            "u_supplier_reference": event['task_number'],
                            "ice4u_target_id": event['task_number'],
                            "u_work_notes": "Work Note - Payload recieved and currently work in progress",
                            "u_close_notes": "",
                            "u_state": "2",
                            "u_short_description": "",
                            "u_description": "",
                            "u_due_date": dynamicnowdata,
                            "u_comments": ""
                        })
                    headers = { 'Authorization': 'Bearer '+Bearer_token_data['access_token'] , 'Content-Type': 'application/json'}
                    response = requests.request("POST", api_data['RARS_URL'], headers=headers, data=payload)
                else:
                    print("Failed to get SIMAAS bearer toaken...")
            else:
                print("failed at getting required secrets from AWS secret manager..")
        except Exception as exception:
            print("Exception while sending response to Snow and error is {}".format(exception))
        else:
            if response.status_code :
                print("bearer API resposne status has been returned and value is:{}".format(response.status_code))
                return response.status_code
            else :
                print("No status code has been returned...")  

    def getQueueURL(self):
        try:
            queue_url = self.sqs_client.get_queue_url(QueueName="platform_snow_request_box.fifo").get('QueueUrl')
            print("Queue URL is {}".format(queue_url))
        except Exception as exception:
            print("Exception in Lambda Handler and error is {}".format(exception))
        return queue_url

    def CreateRecordInS3bucket(self, event):
        print("Recording with event {}".format(event))
        try:
            print("Inside function to create the dynamic .json file...")
            dynamicfilename = datetime.datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
            print("filename format created is {}".format(dynamicfilename))
            file_name =  dynamicfilename + "_payload.json"
            print("file name is {}".format(file_name))
            s3_file_name =  event['RequestNo'] + "/" + file_name
            print("s3 bucket path in bucket snow-integration-logs would be  {}".format(s3_file_name))
            local_file_path = "/tmp/payload.json"
            print("file path:{}".format(local_file_path))
            with open(local_file_path, 'w') as fp:
                json.dump(event, fp)
            print("event is stored in local json file")
            self.s3_client.meta.client.upload_file(local_file_path,self.snow_integration_log_bucket, s3_file_name)
            print("file uploaded successfully..")
            os.remove(local_file_path)
            print("File deleted after upload to s3 bucket")
        except Exception as exception:
            print("Exception in Lambda Handler and error is {}".format(exception))

    def ValidateCreatequeueMessage(self, event):
        print("Message recieved from Snow and body is {}".format(event))
        try:
            print("Framing the reciever queue message..")
            if event['snow_variables']['sh_connectivity_type'] == "Connected to Shell Services (Private)":
                print("Account is indetified as the private account hence processing for private account onboarding")
                if event['snow_variables']['sh_virginia'] == 'false' :
                    NVirginiaValue = "No-VPC"
                else :
                    NVirginiaValue = "32" if event['snow_variables']['sh_vpc_size_virginia'] == "Small (32)s" else ("64" if event['snow_variables']['sh_vpc_size_virginia'] == "Medium (64)"  else ("128" if event['snow_variables']['sh_vpc_size_virginia'] == "Large (128)"  else "256"))
                               
                if event['snow_variables']['sh_ireland'] == 'false' :
                    IrelandValue = "No-VPC"
                else :
                    IrelandValue = "32" if event['snow_variables']['sh_vpc_size_ireland'] == "Small (32)s" else ("64" if event['snow_variables']['sh_vpc_size_ireland'] == "Medium (64)"  else ("128" if event['snow_variables']['sh_vpc_size_ireland'] == "Large (128)"  else "256"))

                if event['snow_variables']['sh_singapore_ap_southeast_1'] == 'false' :
                    SingaporeValue = "No-VPC"
                else :
                    SingaporeValue = "32" if event['snow_variables']['sh_vpc_size_singapore'] == "Small (32)s" else ("64" if event['snow_variables']['sh_vpc_size_singapore'] == "Medium (64)"  else ("128" if event['snow_variables']['sh_vpc_size_singapore'] == "Large (128)"  else "256"))

                if 'sh_email_address_of_contributor_s' in event['snow_variables'].keys():
                    BusinessContributor =  event['snow_variables']['sh_email_address_of_contributor_s']
                else:
                    BusinessContributor = ""

                if 'sh_email_address_of_operator' in event['snow_variables'].keys():
                    BusinessOperator =  event['snow_variables']['sh_email_address_of_operator']
                else:
                    BusinessOperator = ""

                if 'sh_email_address_buss_lmd_operator' in event['snow_variables'].keys():
                    BusinessLimitedOperator =  event['snow_variables']['sh_email_address_buss_lmd_operator']
                else:
                    BusinessLimitedOperator = ""

                if 'sh_email_address_of_read_only' in event['snow_variables'].keys():
                    BusinessReadonly =  event['snow_variables']['sh_email_address_of_read_only']
                else:
                    BusinessReadonly = ""

                if event['snow_variables']['sh_need_business_custom'] == 'Yes' :
                    if 'sh_email_address_of_business_custom' in event['snow_variables'].keys():
                        BusinessCustom = event['snow_variables']['sh_email_address_of_business_custom']
                else:
                    BusinessCustom = "NotOpted"

                if  'sh_is_iot_account' in event['snow_variables'].keys():
                    IsIOTAccount = event['snow_variables']['sh_is_iot_account']
                else: 
                    IsIOTAccount = "No"

                if  'sh_is_respc_account' in event['snow_variables'].keys():
                    IsRESPCAccount = event['snow_variables']['sh_is_respc_account']
                else: 
                    IsRESPCAccount = "No"

                if  'sh_non_rou_subnets' in event['snow_variables'].keys():
                    IsNonroutableSubnets = event['snow_variables']['sh_non_rou_subnets']  
                else: 
                    IsNonroutableSubnets = "No"

                if  'sh_is_hybrid_respc_account_domain_join_ou_name' in event['snow_variables'].keys():
                    HybridRESPCAccountDomainJoinOUName = event['snow_variables']['sh_is_hybrid_respc_account_domain_join_ou_name']
                else: 
                    HybridRESPCAccountDomainJoinOUName = "NA"

                if 'sh_sox_relevant' in event['snow_variables'].keys():
                    if event['snow_variables']['sh_sox_relevant'] != "":
                        SOXrelevant = event['snow_variables']['sh_sox_relevant']
                else:
                    SOXrelevant = "NA"

                if 'sh_active_bia_id' in event['snow_variables'].keys():
                    if event['snow_variables']['sh_active_bia_id'] != "":
                        ActiveBIAid = event['snow_variables']['sh_active_bia_id']
                else:
                    ActiveBIAid = "NA"
                
                if 'sh_info_classify' in event['snow_variables'].keys():
                    if event['snow_variables']['sh_info_classify'] != "":
                        DataClassification = event['snow_variables']['sh_info_classify']
                else:
                    DataClassification = "Unrestricted"

                if 'sh_sel_tenancy' in event['snow_variables'].keys():
                    if event['snow_variables']['sh_sel_tenancy'] == "Single Tenancy":
                        AccountTenancy = "Single-Tenancy"
                    else:
                        AccountTenancy = event['snow_variables']['sh_sel_tenancy']
                else:
                    AccountTenancy = "Single-Tenancy"

                if 'sh_business_type' in event['snow_variables'].keys():
                    BussinessType = event['snow_variables']['sh_business_type']
                else:
                    BussinessType = " "

                if 'sh_databricks_account' in event['snow_variables'].keys():
                    IsDatabricksAccount = event['snow_variables']['sh_databricks_account']
                else:
                    IsDatabricksAccount = "No"

                if 'sh_databricks_environment' in event['snow_variables'].keys():
                    DatabricksEnvironment = event['snow_variables']['sh_databricks_environment']
                else:
                    DatabricksEnvironment = "NA"

                if 'sh_add_ext' in event['snow_variables'].keys():
                    DatabricksVolumeRequired = event['snow_variables']['sh_add_ext']
                else:
                    DatabricksVolumeRequired = "No"

                if 'sh_databricts_region' in event['snow_variables'].keys():
                    DatabricksS3Region = event['snow_variables']['sh_databricts_region']
                else:
                    DatabricksS3Region = "NA"

                if 'sh_prj_number_aws' in event['snow_variables'].keys():
                    DatabricksProjectID = event['snow_variables']['sh_prj_number_aws']
                else:
                    DatabricksProjectID = "NA"

                RecieverBoxQueuemessage = {
                    "SoldToCode": event['snow_variables']['sh_stc_number'],
                    "NVirginia": NVirginiaValue,
                    "Ireland":IrelandValue,
                    "Singapore": SingaporeValue,
                    "CustodianUser":event['snow_variables']['sh_custodian_email_id'],
                    "CustodianUserFirstName":event['snow_variables']['sh_custodian_first_name'],
                    "CustodianUserLastName":event['snow_variables']['sh_custodian_last_name'],
                    "RequestorEmail":event['snow_variables']['sh_request_for_email'],
                    "SupportDL":event['snow_variables']['sh_app_dl_email'],
                    "ApexID": event['snow_variables']['sh_apex_id'],
                    "Environment":"Private-Production",
                    "Budget": event['snow_variables']['sh_monthly_budget'],
                    "LOB": event['snow_variables']['sh_lob'],
                    "Migration":"No",
                    "RequestNo": event['requested_item_number'],
                    "Apex_Environment": event['snow_variables']['sh_operating_env'],
                    "Apex_ID_Name": event['snow_variables']['sh_buss_app_name'],
                    "RequestType" :"Create",
                    "AccountNumber":"",
                    "AccountName":event['snow_variables']['sh_application_name'],
                    "BusinessContributors":BusinessContributor,
                    "BusinessOperators":BusinessOperator,
                    "BusinessLimitedOperators":BusinessLimitedOperator,
                    "BusinessReadOnly":BusinessReadonly,
                    "BusinessCustom":BusinessCustom,
                    "RequestTaskNo": event['task_number'],
                    "WorkLoadType": event['snow_variables']['sh_workload_type'],
                    "IsIOTAccount": IsIOTAccount,
                    "IsRESPCAccount": IsRESPCAccount,
                    "IsNonroutableSubnets": IsNonroutableSubnets,
                    "HybridRESPCAccountDomainJoinOUName" : HybridRESPCAccountDomainJoinOUName,
                    "SOXrelevant": SOXrelevant,
                    "ActiveBIAid": ActiveBIAid,
                    "DataClassification": DataClassification,
                    "AccountTenancy": AccountTenancy,
                    "BussinessType": BussinessType,
                    "IsDatabricksAccount": IsDatabricksAccount,
                    "DatabricksEnvironment": DatabricksEnvironment,
                    "DatabricksVolumeRequired": DatabricksVolumeRequired,
                    "DatabricksS3Region": DatabricksS3Region,
                    "DatabricksProjectID": DatabricksProjectID
                }
                print("private onboard request message is framed now ...")
            
            elif event['snow_variables']['sh_connectivity_type'] == "Hybrid Connectivity (Protected Public and Private connectivity)":
                print("Account is indetified as the hybrid account hence processing for hybrid account onboarding")
                if event['snow_variables']['sh_virginia'] == 'false' :
                    NVirginiaValue = "No-VPC"
                else :
                    NVirginiaValue = "64" if event['snow_variables']['sh_vpc_size_virginia_us_east'] == "Medium (64)"  else ("128" if event['snow_variables']['sh_vpc_size_virginia_us_east'] == "Large (128)"  else "256")
                                     

                if event['snow_variables']['sh_ireland'] == 'false' :
                    IrelandValue = "No-VPC"
                else :
                    IrelandValue = "64" if event['snow_variables']['sh_vpc_size_ireland_eu_west'] == "Medium (64)"  else ("128" if event['snow_variables']['sh_vpc_size_ireland_eu_west'] == "Large (128)"  else "256")
                
                if event['snow_variables']['sh_singapore_ap_southeast_1'] == 'false' :
                    SingaporeValue = "No-VPC"
                else :
                    SingaporeValue = "64" if event['snow_variables']['sh_vpc_size_singapore'] == "Medium (64)"  else ("128" if event['snow_variables']['sh_vpc_size_singapore'] == "Large (128)"  else "256")


                if 'sh_email_address_of_contributor_s' in event['snow_variables'].keys():
                    BusinessContributor =  event['snow_variables']['sh_email_address_of_contributor_s']
                else:
                    BusinessContributor = ""

                if 'sh_email_address_of_operator' in event['snow_variables'].keys():
                    BusinessOperator =  event['snow_variables']['sh_email_address_of_operator']
                else:
                    BusinessOperator = ""

                if 'sh_email_address_buss_lmd_operator' in event['snow_variables'].keys():
                    BusinessLimitedOperator =  event['snow_variables']['sh_email_address_buss_lmd_operator']
                else:
                    BusinessLimitedOperator = ""

                if 'sh_email_address_of_read_only' in event['snow_variables'].keys():
                    BusinessReadonly =  event['snow_variables']['sh_email_address_of_read_only']
                else:
                    BusinessReadonly = ""

                if event['snow_variables']['sh_need_business_custom'] == 'Yes' :
                    if 'sh_email_address_of_business_custom' in event['snow_variables'].keys():
                        BusinessCustom = event['snow_variables']['sh_email_address_of_business_custom']
                else:
                    BusinessCustom = "NotOpted"

                if  'sh_is_iot_account' in event['snow_variables'].keys():
                    IsIOTAccount = event['snow_variables']['sh_is_iot_account']
                else: 
                    IsIOTAccount = "No"

                if  'sh_is_respc_account' in event['snow_variables'].keys():
                    IsRESPCAccount = event['snow_variables']['sh_is_respc_account']
                else: 
                    IsRESPCAccount = "No"
                
                if  'sh_non_rou_subnets' in event['snow_variables'].keys():
                    IsNonroutableSubnets = event['snow_variables']['sh_non_rou_subnets']
                else: 
                    IsNonroutableSubnets = "No"

                if  'sh_is_hybrid_respc_account_domain_join_ou_name' in event['snow_variables'].keys():
                    HybridRESPCAccountDomainJoinOUName = event['snow_variables']['sh_is_hybrid_respc_account_domain_join_ou_name']
                else: 
                    HybridRESPCAccountDomainJoinOUName = "NA"

                if 'sh_sox_relevant' in event['snow_variables'].keys():
                    if event['snow_variables']['sh_sox_relevant'] != "":
                        SOXrelevant = event['snow_variables']['sh_sox_relevant']
                else:
                    SOXrelevant = "NA"

                if 'sh_active_bia_id' in event['snow_variables'].keys():
                    if event['snow_variables']['sh_active_bia_id'] != "":
                        ActiveBIAid = event['snow_variables']['sh_active_bia_id']
                else:
                    ActiveBIAid = "NA"
                
                if 'sh_info_classify' in event['snow_variables'].keys():
                    if event['snow_variables']['sh_info_classify'] != "":
                        DataClassification = event['snow_variables']['sh_info_classify']
                else:
                    DataClassification = "Unrestricted"

                if 'sh_sel_tenancy' in event['snow_variables'].keys():
                    if event['snow_variables']['sh_sel_tenancy'] == "Single Tenancy":
                        AccountTenancy = "Single-Tenancy"
                    else:
                        AccountTenancy = event['snow_variables']['sh_sel_tenancy']
                else:
                    AccountTenancy = "Single-Tenancy"

                if 'sh_business_type' in event['snow_variables'].keys():
                    BussinessType = event['snow_variables']['sh_business_type']
                else:
                    BussinessType = " "

                if 'sh_databricks_account' in event['snow_variables'].keys():
                    IsDatabricksAccount = event['snow_variables']['sh_databricks_account']
                else:
                    IsDatabricksAccount = "No"

                if 'sh_databricks_environment' in event['snow_variables'].keys():
                    DatabricksEnvironment = event['snow_variables']['sh_databricks_environment']
                else:
                    DatabricksEnvironment = "NA"

                if 'sh_add_ext' in event['snow_variables'].keys():
                    DatabricksVolumeRequired = event['snow_variables']['sh_add_ext']
                else:
                    DatabricksVolumeRequired = "No"

                if 'sh_databricts_region' in event['snow_variables'].keys():
                    DatabricksS3Region = event['snow_variables']['sh_databricts_region']
                else:
                    DatabricksS3Region = "NA"

                if 'sh_prj_number_aws' in event['snow_variables'].keys():
                    DatabricksProjectID = event['snow_variables']['sh_prj_number_aws']
                else:
                    DatabricksProjectID = "NA"

                RecieverBoxQueuemessage = {
                    "SoldToCode": event['snow_variables']['sh_stc_number'],
                    "NVirginia": NVirginiaValue,
                    "Ireland":IrelandValue,
                    "Singapore": SingaporeValue,
                    "CustodianUser":event['snow_variables']['sh_custodian_email_id'],
                    "CustodianUserFirstName":event['snow_variables']['sh_custodian_first_name'],
                    "CustodianUserLastName":event['snow_variables']['sh_custodian_last_name'],
                    "RequestorEmail":event['snow_variables']['sh_request_for_email'],
                    "SupportDL":event['snow_variables']['sh_app_dl_email'],
                    "ApexID": event['snow_variables']['sh_apex_id'],
                    "Environment":"Hybrid-Account",
                    "Budget": event['snow_variables']['sh_monthly_budget'],
                    "LOB": event['snow_variables']['sh_lob'],
                    "Migration":"No",
                    "RequestNo": event['requested_item_number'],
                    "Apex_Environment": event['snow_variables']['sh_operating_env'],
                    "Apex_ID_Name": event['snow_variables']['sh_buss_app_name'],
                    "RequestType" :"Create",
                    "AccountNumber":"",
                    "AccountName":event['snow_variables']['sh_application_name'],
                    "BusinessContributors":BusinessContributor,
                    "BusinessOperators":BusinessOperator,
                    "BusinessLimitedOperators":BusinessLimitedOperator,
                    "BusinessReadOnly":BusinessReadonly,
                    "BusinessCustom":BusinessCustom,
                    "RequestTaskNo": event['task_number'],
                    "WorkLoadType": event['snow_variables']['sh_workload_type'],
                    "IsIOTAccount": IsIOTAccount,
                    "IsRESPCAccount": IsRESPCAccount,
                    "IsNonroutableSubnets": IsNonroutableSubnets,
                    "HybridRESPCAccountDomainJoinOUName" : HybridRESPCAccountDomainJoinOUName,
                    "SOXrelevant": SOXrelevant,
                    "ActiveBIAid": ActiveBIAid,
                    "DataClassification": DataClassification,
                    "AccountTenancy": AccountTenancy,
                    "BussinessType": BussinessType,
                    "IsDatabricksAccount": IsDatabricksAccount,
                    "DatabricksEnvironment": DatabricksEnvironment,
                    "DatabricksVolumeRequired": DatabricksVolumeRequired,
                    "DatabricksS3Region": DatabricksS3Region,
                    "DatabricksProjectID": DatabricksProjectID
                }
                print("Hybrid onboard request message is framed now ...")


            elif event['snow_variables']['sh_connectivity_type'] == "Internet facing (Public)":
                print("Account is indetified as the public account hence processing for public account onboarding")
                if 'sh_email_address_of_contributor_s' in event['snow_variables'].keys():
                    BusinessContributor =  event['snow_variables']['sh_email_address_of_contributor_s']
                else:
                    BusinessContributor = ""

                if 'sh_email_address_of_operator' in event['snow_variables'].keys():
                    BusinessOperator =  event['snow_variables']['sh_email_address_of_operator']
                else:
                    BusinessOperator = ""

                if 'sh_email_address_buss_lmd_operator' in event['snow_variables'].keys():
                    BusinessLimitedOperator =  event['snow_variables']['sh_email_address_buss_lmd_operator']
                else:
                    BusinessLimitedOperator = ""

                if 'sh_email_address_of_read_only' in event['snow_variables'].keys():
                    BusinessReadonly =  event['snow_variables']['sh_email_address_of_read_only']
                else:
                    BusinessReadonly = ""

                if event['snow_variables']['sh_need_business_custom'] == 'Yes' :
                    if 'sh_email_address_of_business_custom' in event['snow_variables'].keys():
                        BusinessCustom = event['snow_variables']['sh_email_address_of_business_custom']
                else:
                    BusinessCustom = "NotOpted"

                if  'sh_is_respc_account' in event['snow_variables'].keys():
                    IsRESPCAccount = event['snow_variables']['sh_is_respc_account']
                else: 
                    IsRESPCAccount = "No"
                    
                if  'sh_is_iot_account' in event['snow_variables'].keys():
                    IsIOTAccount = event['snow_variables']['sh_is_iot_account']
                else: 
                    IsIOTAccount = "No"

                if  'sh_non_rou_subnets' in event['snow_variables'].keys():
                    IsNonroutableSubnets = event['snow_variables']['sh_non_rou_subnets']  
                else: 
                    IsNonroutableSubnets = "No"

                if  'sh_is_hybrid_respc_account_domain_join_ou_name' in event['snow_variables'].keys():
                    HybridRESPCAccountDomainJoinOUName = event['snow_variables']['sh_is_hybrid_respc_account_domain_join_ou_name']
                else: 
                    HybridRESPCAccountDomainJoinOUName = "NA"

                if 'sh_sox_relevant' in event['snow_variables'].keys():
                    if event['snow_variables']['sh_sox_relevant'] != "":
                        SOXrelevant = event['snow_variables']['sh_sox_relevant']
                else:
                    SOXrelevant = "NA"

                if 'sh_active_bia_id' in event['snow_variables'].keys():
                    if event['snow_variables']['sh_active_bia_id'] != "":
                        ActiveBIAid = event['snow_variables']['sh_active_bia_id']
                else:
                    ActiveBIAid = "NA"
                
                if 'sh_info_classify' in event['snow_variables'].keys():
                    if event['snow_variables']['sh_info_classify'] != "":
                        DataClassification = event['snow_variables']['sh_info_classify']
                else:
                    DataClassification = "Unrestricted"

                if 'sh_sel_tenancy' in event['snow_variables'].keys():
                    if event['snow_variables']['sh_sel_tenancy'] == "Single Tenancy":
                        AccountTenancy = "Single-Tenancy"
                    else:
                        AccountTenancy = event['snow_variables']['sh_sel_tenancy']
                else:
                    AccountTenancy = "Single-Tenancy"

                if 'sh_business_type' in event['snow_variables'].keys():
                    BussinessType = event['snow_variables']['sh_business_type']
                else:
                    BussinessType = " "

                if 'sh_databricks_account' in event['snow_variables'].keys():
                    IsDatabricksAccount = event['snow_variables']['sh_databricks_account']
                else:
                    IsDatabricksAccount = "No"

                if 'sh_databricks_environment' in event['snow_variables'].keys():
                    DatabricksEnvironment = event['snow_variables']['sh_databricks_environment']
                else:
                    DatabricksEnvironment = "NA"

                if 'sh_add_ext' in event['snow_variables'].keys():
                    DatabricksVolumeRequired = event['snow_variables']['sh_add_ext']
                else:
                    DatabricksVolumeRequired = "No"

                if 'sh_databricts_region' in event['snow_variables'].keys():
                    DatabricksS3Region = event['snow_variables']['sh_databricts_region']
                else:
                    DatabricksS3Region = "NA"

                if 'sh_prj_number_aws' in event['snow_variables'].keys():
                    DatabricksProjectID = event['snow_variables']['sh_prj_number_aws']
                else:
                    DatabricksProjectID = "NA"

                RecieverBoxQueuemessage = {
                    "SoldToCode": event['snow_variables']['sh_stc_number'],
                    "NVirginia": "No-VPC",
                    "Ireland":"No-VPC",
                    "Singapore":"No-VPC",
                    "CustodianUser":event['snow_variables']['sh_custodian_email_id'],
                    "CustodianUserFirstName":event['snow_variables']['sh_custodian_first_name'],
                    "CustodianUserLastName":event['snow_variables']['sh_custodian_last_name'],
                    "RequestorEmail":event['snow_variables']['sh_request_for_email'],
                    "SupportDL":event['snow_variables']['sh_app_dl_email'],
                    "ApexID": event['snow_variables']['sh_apex_id'],
                    "Environment":"Public-Production",
                    "Budget": event['snow_variables']['sh_monthly_budget'],
                    "LOB": event['snow_variables']['sh_lob'],
                    "Migration":"No",
                    "RequestNo": event['requested_item_number'],
                    "Apex_Environment": event['snow_variables']['sh_operating_env'],
                    "Apex_ID_Name": event['snow_variables']['sh_buss_app_name'],
                    "RequestType" :"Create",
                    "AccountNumber":"",
                    "AccountName":event['snow_variables']['sh_application_name'],
                    "BusinessContributors":BusinessContributor,
                    "BusinessOperators":BusinessOperator,
                    "BusinessLimitedOperators":BusinessLimitedOperator,
                    "BusinessReadOnly":BusinessReadonly,
                    "BusinessCustom":BusinessCustom,
                    "RequestTaskNo": event['task_number'],
                    "WorkLoadType": event['snow_variables']['sh_workload_type'],
                    "IsIOTAccount": IsIOTAccount,
                    "IsRESPCAccount": IsRESPCAccount,
                    "IsNonroutableSubnets": IsNonroutableSubnets,
                    "HybridRESPCAccountDomainJoinOUName" : HybridRESPCAccountDomainJoinOUName,
                    "SOXrelevant": SOXrelevant,
                    "ActiveBIAid": ActiveBIAid,
                    "DataClassification": DataClassification,
                    "AccountTenancy": AccountTenancy,
                    "BussinessType": BussinessType,
                    "IsDatabricksAccount": IsDatabricksAccount,
                    "DatabricksEnvironment": DatabricksEnvironment,
                    "DatabricksVolumeRequired": DatabricksVolumeRequired,
                    "DatabricksS3Region": DatabricksS3Region,
                    "DatabricksProjectID": DatabricksProjectID
                }
                print("public onboard request message is framed now ...")
            else :
                print ("Unknow request from Snow form hence exiting....")
                exit()
            return RecieverBoxQueuemessage
        except Exception as exception:
            print("Exception in Lambda Handler and error is {}".format(exception))

    def recordAqueueMessage(self, event):
        print("Recording with event {}".format(event))
        try:
            queueurl = self.getQueueURL()
            print("Got queue URL {}".format(queueurl))
            response = self.sqs_client.send_message(QueueUrl=queueurl, MessageBody=json.dumps(event), MessageGroupId="SnowRequest")
            print("Send result: {}".format(response))
        except Exception as exception:
            print("Exception in Lambda Handler and error is {}".format(exception))

def lambda_handler(event, context):
    try:
        print("inside the handler checking the event type and data within it....")
        print(type(event))
        print(event)
        if event and event['body-json']['catalog_item_name'] == "AWS Account - Creation":
            print("Event is for AWS@Shell account creation request.. now it will be processed..")
            sendqueueObject = SendQueueMessageRecieverBox(event['body-json'], context)
            print("object is created..")
            print("sending response back to snow to make ticket open..")
            snowResponsecode = sendqueueObject.send_Snow_Response(event['body-json'])
            if snowResponsecode == 201 or snowResponsecode == 200:
                print("task is updated with open status now..")
                ValidateAndFramedResponse = sendqueueObject.ValidateCreatequeueMessage(event['body-json'])
                if ValidateAndFramedResponse :
                    sendqueueObject.CreateRecordInS3bucket(ValidateAndFramedResponse)
                    print("Request data stored in s3 bucket..")
                    sendqueueObject.recordAqueueMessage(ValidateAndFramedResponse)
                    print("invoked the queue message..")
                return {
                        'statusCode': 200,
                        'body': json.dumps('Request considered for Onbaording to AWS@Shell..!')
                }
            else:
                print("task update did not go well hence not processing request now as it could be malicious request..")
                return {
                    'statusCode': 400,
                    'body': json.dumps('Request cant be processed for other than Onbaord to AWS@Shell..!')
                }
        else:
            return {
                    'statusCode': 400,
                    'body': json.dumps('Request cant be processed for other than Onbaord to AWS@Shell..!')
            }
    except Exception as exception:
        print(exception)