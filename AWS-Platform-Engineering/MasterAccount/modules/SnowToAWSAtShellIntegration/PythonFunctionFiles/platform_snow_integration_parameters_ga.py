# This lambda was updated as part of RARS Migration from 1.0 to 2.0
import json
import os
import boto3
import requests
import datetime
import time
from botocore.exceptions import ClientError
import base64
import ipaddress

class GetParameters(object):
    def __init__(self, event, context):
        try: 
            self.exception = []
            self.event = event
            self.context = context
            self.session_client = boto3.session.Session()
            self.secretManager_client = self.session_client.client('secretsmanager', region_name="us-east-1")
            self.request_type = event['RequestType']
            self.resource_properties = self.event["RequestEventData"]
            self.Environment = self.event["ProvisionedProduct"]['OU']
            self.Business_account = self.event["ProvisionedProduct"]['AccountNumber']
            session_client = boto3.session.Session()
            self.ssm_client = session_client.client('ssm', region_name='us-east-1')
            self.s3_client = boto3.resource('s3')
            tfcparameterstorebucket = self.ssm_client.get_parameter(Name='githubaction_parameter_bucketName')
            self.githubaction_parameter_bucket = tfcparameterstorebucket['Parameter']['Value']
            print("Bucket for storing parameters.json", self.githubaction_parameter_bucket )
            self.dynamodb_client = session_client.client('dynamodb')
            self.cidr_table_name = self.ssm_client.get_parameter(Name='cidr_table_name')['Parameter']['Value']
            print("CIDR Table Name", self.cidr_table_name )
            self.cidr_table_index = self.ssm_client.get_parameter(Name='cidr_table_index')['Parameter']['Value']
            print("CIDR Table Index", self.cidr_table_index )
            self.sender_id = self.ssm_client.get_parameter(Name='sender_id')['Parameter']['Value']
            print("Sender ID", self.sender_id )
            self.operations_dl = self.ssm_client.get_parameter(Name='failure_operation_dl')['Parameter']['Value']
            print("Operational DL", self.operations_dl)
            self.network_table_name = self.ssm_client.get_parameter(Name='platform_network_table_name')['Parameter']['Value']
            print("Network Details Table", self.network_table_name )
            self.env_type = self.ssm_client.get_parameter(Name='platform_Env_type')['Parameter']['Value']
            print("Env type ", self.env_type )
            private_regions_response = self.ssm_client.get_parameter(Name="whitelisted_regions_private")
            self.private_regions_str = private_regions_response['Parameter']['Value']
            self.private_regions = self.private_regions_str.split(",")
            print("Private regions", self.private_regions  )
        except Exception as exception:
            print(str(exception))

    ## Fetch and Create SSM parameters
    def prepare_ssm_parameters_dict(self,event):
        print("Start SSM parameters preparation")
        ssm_parameters_dict = {}
        response = self.ssm_client.describe_parameters()
        param_result = response['Parameters']
        while 'NextToken' in response:
            response = self.ssm_client.describe_parameters(NextToken=response['NextToken']) 
            param_result.extend(response['Parameters']) 

        ssm_parameters = []
        for item in param_result:
            ssm_parameters.append(item['Name'])

        for i in range(0, len(ssm_parameters), 10):
            retries = 0
            get_param_status = 'False'
            try:
                while retries < 4 and get_param_status == 'False':
                    response = self.ssm_client.get_parameters(
                        Names=ssm_parameters[i:i + 10],
                        WithDecryption=True)
                    temp_res_code = response['ResponseMetadata']['HTTPStatusCode']
                    if temp_res_code == 200:
                        get_param_status = 'True'
                        response_parameters = response['Parameters']
                        for param in response_parameters:
                            ssm_parameters_dict[param['Name']] = param['Value']
                    else: 
                        time_to_sleep = 2 ** retries
                        retries += 1
                        time.sleep(time_to_sleep)
            except Exception as exception:
                print("An exception occured while retrieing all values of SSM parameters: ",(exception))
                self.send_failed_Snow_Resonse (event['RequestEventData']['RequestTaskNo'], event['ProvisionedProduct']['Name'])
        event['SSMParameters'] = ssm_parameters_dict
    
    ## Get IP dictionary
    def get_region_ip(self, event):
        try:
            region_ip_dict = {}
            print("Inside get region ip")
            if "Private" in self.Environment:
                print("its private account...")
                for region_name in self.resource_properties.keys():
                    if region_name == 'NVirginia' and self.resource_properties[region_name] != "No-VPC":
                        region_ip_dict.update({"us-east-1": self.resource_properties[region_name]})
                    elif region_name == 'NVirginia' and self.resource_properties[region_name] == "No-VPC":
                        region_ip_dict.update({"us-east-1": "No-VPC"})
                    if region_name == 'Ireland' and self.resource_properties[region_name] != "No-VPC":
                        region_ip_dict.update({"eu-west-1": self.resource_properties[region_name]})
                    elif region_name == 'Ireland' and self.resource_properties[region_name] == "No-VPC":
                        region_ip_dict.update({"eu-west-1": "No-VPC"})
                    if region_name == 'Singapore' and self.resource_properties[region_name] != "No-VPC":
                        region_ip_dict.update({"ap-southeast-1": self.resource_properties[region_name]})  
                    elif region_name == 'Singapore' and self.resource_properties[region_name] == "No-VPC":
                        region_ip_dict.update({"ap-southeast-1": "No-VPC"})                     
                print(region_ip_dict)
            elif "Hybrid" in self.Environment:
                print("its hybrid-account account...")
                for region_name in self.resource_properties.keys():
                    if region_name == 'NVirginia' and self.resource_properties[region_name] != "No-VPC":
                        region_ip_dict.update({"us-east-1": self.resource_properties[region_name]})
                    elif region_name == 'NVirginia' and self.resource_properties[region_name] == "No-VPC":
                        region_ip_dict.update({"us-east-1": "No-VPC"})
                    if region_name == 'Ireland' and self.resource_properties[region_name] != "No-VPC":
                        region_ip_dict.update({"eu-west-1": self.resource_properties[region_name]})
                    elif region_name == 'Ireland' and self.resource_properties[region_name] == "No-VPC":
                        region_ip_dict.update({"eu-west-1": "No-VPC"})
                    if region_name == 'Singapore' and self.resource_properties[region_name] != "No-VPC":
                        region_ip_dict.update({"ap-southeast-1": self.resource_properties[region_name]}) 
                    elif region_name == 'Singapore' and self.resource_properties[region_name] == "No-VPC":
                        region_ip_dict.update({"ap-southeast-1": "No-VPC"})
                print(region_ip_dict)
            else:
                print ("Its not private connectivity..")
                public_region = self.event['SSMParameters']['whitelisted_regions_public'].split(",")
                for pub_region in public_region:
                    region_ip_dict.update({pub_region: "No-VPC"})
                print(region_ip_dict)              
        except Exception as e:
            print("Error occurred in fetching region: ", str(e))
            self.send_failed_Snow_Resonse (event['RequestEventData']['RequestTaskNo'], event['ProvisionedProduct']['Name'])
            return False
        event['RegionIpDictionary'] = region_ip_dict
        return True
    
    ## Append Security Hub Data
    def add_security_hub_control_IDs(self, event):
        try:
            event['cis_aws_securityhub_controls'] = {} 
            event['cis_aws_securityhub_controls']['cis_securityhub_controls'] = ["1.14"]
            event['cis_aws_securityhub_controls']['aws_securityhub_controls'] = ["IAM.6", "ELB.3", "SSM.1"]
        except Exception as e:
            print("Error occurred in add security hub controls at events: ", str(e))
            self.send_failed_Snow_Resonse (event['RequestEventData']['RequestTaskNo'], event['ProvisionedProduct']['Name'])
            return False
        return True
    
    ## Append VPC Extension Index
    def add_vpc_extension_index(self, event, index):
        try:
            event['VPC_cidr_extend_number_US'] = str(index)
            event['VPC_cidr_extend_number_EU'] = str(index)
            event['VPC_cidr_extend_number_SG'] = str(index)
        except Exception as e:
            print("Error occurred in add vpc extension index: ", str(e))
            self.send_failed_Snow_Resonse (event['RequestEventData']['RequestTaskNo'], event['ProvisionedProduct']['Name'])
            return False
        return True
    
    ## Append Env Type
    def add_env_type(self, event):
        try:
            event['Env_type'] = self.env_type
        except Exception as e:
            print("Error occurred in add Env Type: ", str(e))
            self.send_failed_Snow_Resonse (event['RequestEventData']['RequestTaskNo'], event['ProvisionedProduct']['Name'])
            return False
        return True

    ## Append Env Type
    def add_sso_parameters(self, event):
        try:
            event['SSMParameters']['irm_permission_set_name'] = "platform_IRM"
            event['SSMParameters']['platform_irm_group_name'] = "platform_IRM"
            event['SSMParameters']['platform_readonly_permission_set_name'] = "AWSReadOnlyAccess"
            event['SSMParameters']['platform_readonly_group_name'] = "AZ-AWAS-GRP-"+(event['Env_type']).upper()+"-PlatformReadOnly"
            event['SSMParameters']['itom_readonly_permission_set_name'] = "business_ServiceNow_ITOM"
            event['SSMParameters']['itom_readonly_group_name'] = "AZ-AWAS-GRP-"+(event['Env_type']).upper()+"-ServiceNow-ITOM-Discovery"
        except Exception as e:
            print("Error occurred in add SSO Parameters: ", str(e))
            self.send_failed_Snow_Resonse (event['RequestEventData']['RequestTaskNo'], event['ProvisionedProduct']['Name'])
            return False
        return True

    ## Append allow listed EKS AMIs
    def add_eks_amis(self, event):
        try:
            print("Add EKS AMIs..")
            if "Private" in self.Environment or "Hybrid" in self.Environment :
                print("Its private connectivity account")
                event['SSMParameters']['eksamisallowedlist'] = "amazon-eks-node-1.18*,amazon-eks-gpu-node-1.18*,amazon-eks-arm64-node-1.18*,amazon-eks-node-1.19*,amazon-eks-gpu-node-1.19*,amazon-eks-arm64-node-1.19*,amazon-eks-node-1.20*,amazon-eks-gpu-node-1.20*,amazon-eks-arm64-node-1.20*,amazon-eks-node-1.21*,amazon-eks-gpu-node-1.21*,amazon-eks-arm64-node-1.21*,amazon-eks-node-1.22*,amazon-eks-gpu-node-1.22*,amazon-eks-arm64-node-1.22*,amazon-eks-node-1.23*,amazon-eks-gpu-node-1.23*,amazon-eks-arm64-node-1.23*,amazon-eks-node-1.24*,amazon-eks-gpu-node-1.24*,amazon-eks-arm64-node-1.24*,amazon-eks-node-1.25*,amazon-eks-gpu-node-1.25*,amazon-eks-arm64-node-1.25*,amazon-eks-node-1.26*,amazon-eks-gpu-node-1.26*,amazon-eks-arm64-node-1.26*,amazon-eks-node-1.27*,amazon-eks-gpu-node-1.27*,amazon-eks-arm64-node-1.27*,amazon-eks-node-1.28*,amazon-eks-gpu-node-1.28*,amazon-eks-arm64-node-1.28*,amazon-eks-node-1.29*,amazon-eks-gpu-node-1.29*,amazon-eks-arm64-node-1.29*,bottlerocket-aws-k8s*"
            else:
                print("Its public connectivity account")
                event['SSMParameters']['eksamisallowedlist'] = "amazon-eks-node-1.18*,amazon-eks-gpu-node-1.18*,amazon-eks-arm64-node-1.18*,amazon-eks-node-1.19*,amazon-eks-gpu-node-1.19*,amazon-eks-arm64-node-1.19*,amazon-eks-node-1.20*,amazon-eks-gpu-node-1.20*,amazon-eks-arm64-node-1.20*,amazon-eks-node-1.21*,amazon-eks-gpu-node-1.21*,amazon-eks-arm64-node-1.21*,amazon-eks-node-1.22*,amazon-eks-gpu-node-1.22*,amazon-eks-arm64-node-1.22*,amazon-eks-node-1.23*,amazon-eks-gpu-node-1.23*,amazon-eks-arm64-node-1.23*,amazon-eks-node-1.24*,amazon-eks-gpu-node-1.24*,amazon-eks-arm64-node-1.24*,amazon-eks-node-1.25*,amazon-eks-gpu-node-1.25*,amazon-eks-arm64-node-1.25*,amazon-eks-node-1.26*,amazon-eks-gpu-node-1.26*,amazon-eks-arm64-node-1.26*,amazon-eks-node-1.27*,amazon-eks-gpu-node-1.27*,amazon-eks-arm64-node-1.27*,amazon-eks-node-1.28*,amazon-eks-gpu-node-1.28*,amazon-eks-arm64-node-1.28*,amazon-eks-node-1.29*,amazon-eks-gpu-node-1.29*,amazon-eks-arm64-node-1.29*,bottlerocket-aws-k8s*"
        except Exception as e:
            print("Error occurred in add EKS AMIs List: ", str(e))
            self.send_failed_Snow_Resonse (event['RequestEventData']['RequestTaskNo'], event['ProvisionedProduct']['Name'])
            return False
        return True

    ## Prepare and append IP addresses
    def create_cidr_dictionaries (self, event):
        try:
            for region, ip in event['RegionIpDictionary'].items():
                if region.strip() in self.private_regions:
                    requiredregion = region.strip()
                    regionkey =  "us" if requiredregion == "us-east-1" else ("eu" if requiredregion == "eu-west-1" else ("sg" if requiredregion == "ap-southeast-1" else "NA"))
                    hostedzone_ids_param = "hostedzone_id_"+regionkey
                    RegionIpDictionary = "RegionIpDictionary_"+regionkey.upper()
                    NonRoutableSubnetRequested = "Non_routable_requested_"+regionkey.upper()
                    if ip != "No-VPC" :
                        print("region name : {} IP adress requested {}".format(region , ip))
                        ip_cidr_dict = {}
                        cidr_returned = self.get_cidr(event, requiredregion,ip)
                        if  cidr_returned:
                            print("CIDR returned", cidr_returned)
                            if "Hybrid" in event["ProvisionedProduct"]['OU'] :
                                print("Account is hybrid hence creating four subnets")
                                subnet_list = list(ipaddress.ip_network(cidr_returned).subnets(prefixlen_diff=2))
                                ip_cidr_dict['cidr'] = cidr_returned 
                                ip_cidr_dict['Subnet_cidr_1'] = str(subnet_list[0])
                                ip_cidr_dict['Subnet_cidr_2'] = str(subnet_list[1])
                                ip_cidr_dict['Subnet_cidr_3'] = str(subnet_list[2])
                                ip_cidr_dict['Subnet_cidr_4'] = str(subnet_list[3])
                                ip_cidr_dict['hostedzone_ids'] = self.ssm_client.get_parameter(Name=hostedzone_ids_param)['Parameter']['Value']
                            elif "Private" in event["ProvisionedProduct"]['OU'] :
                                print("Account is private hence creating two subnets")
                                subnet_list = list(ipaddress.ip_network(cidr_returned).subnets())
                                ip_cidr_dict['cidr'] = cidr_returned
                                ip_cidr_dict['Subnet_cidr_1'] = str(subnet_list[0])
                                ip_cidr_dict['Subnet_cidr_2'] = str(subnet_list[1])
                                ip_cidr_dict['hostedzone_ids'] = self.ssm_client.get_parameter(Name=hostedzone_ids_param)['Parameter']['Value']
                            else:
                                print("Its neither Private or Hybrid connectivity, Hence terminating the flow")
                        else :
                            print("CIDR not rteruned, hence changing status of the request and Terminating Process")
                            self.send_failed_Snow_Resonse (event['RequestEventData']['RequestTaskNo'], event['ProvisionedProduct']['Name'])
                            return False
                        event[RegionIpDictionary] = {}
                        event[RegionIpDictionary][requiredregion] = ip_cidr_dict
                        if event["RequestEventData"]['IsNonroutableSubnets'].strip() == "Yes":
                            event[NonRoutableSubnetRequested] = "Yes"
                        else:
                            event[NonRoutableSubnetRequested] = "No"
                    else:
                        event[RegionIpDictionary] = {}
                        event[NonRoutableSubnetRequested] = "No"
        except Exception as e:
            print("Error occurred in fetching region: ", str(e))
            self.send_failed_Snow_Resonse (event['RequestEventData']['RequestTaskNo'], event['ProvisionedProduct']['Name'])
            return False
        return True
    
    ## Prepare and append IP addresses
    def create_extend_cidr_dictionaries (self, event):
        try:
            for region, ip in event['CurrentVPCUpdateRequest'].items():
                if region.strip() in ['NVirginia', 'Ireland', 'Singapore']:
                    
                    requiredregion = "us-east-1" if region.strip() == "NVirginia" else ("eu-west-1" if region.strip() == "Ireland" else ("ap-southeast-1" if region.strip() == "Singapore" else "NA"))
                    regionkey =  "us" if requiredregion == "us-east-1" else ("eu" if requiredregion == "eu-west-1" else ("sg" if requiredregion == "ap-southeast-1" else "NA"))
                    RegionIpDictionary = "RegionIpDictionary_"+regionkey.upper()
                    NonRoutableSubnetRequested = "Non_routable_requested_"+regionkey.upper()
                    
                    if requiredregion in self.private_regions and ip.strip() != "No-VPC" and event['CurrentVPCUpdateRequest']['TaskType'] == "VPC Extension":
                        extendIndex = str(int(event["VPC_cidr_extend_number_"+regionkey.upper()])+1)
                        print("region name : {} IP adress requested {} for VPC extension".format(requiredregion , ip))
                        cidr_returned = self.get_cidr(event, requiredregion,ip)
                        if  cidr_returned:
                            print("CIDR returned", cidr_returned)
                            if "Hybrid" in event["ProvisionedProduct"]['OU'] :
                                print("Account is hybrid hence creating four subnets")
                                subnet_list = list(ipaddress.ip_network(cidr_returned).subnets(prefixlen_diff=2))
                                event[RegionIpDictionary][requiredregion]["extend_cidr_"+extendIndex] = cidr_returned
                                event[RegionIpDictionary][requiredregion]["extend_"+extendIndex+"_subnet_cidr_1"] = str(subnet_list[0])
                                event[RegionIpDictionary][requiredregion]["extend_"+extendIndex+"_subnet_cidr_2"] = str(subnet_list[1])
                                event[RegionIpDictionary][requiredregion]["extend_"+extendIndex+"_subnet_cidr_3"] = str(subnet_list[2])
                                event[RegionIpDictionary][requiredregion]["extend_"+extendIndex+"_subnet_cidr_4"] = str(subnet_list[3])
                                event["VPC_cidr_extend_number_"+regionkey.upper()] = extendIndex
                            elif "Private" in event["ProvisionedProduct"]['OU'] :
                                print("Account is private hence creating two subnets")
                                subnet_list = list(ipaddress.ip_network(cidr_returned).subnets())
                                event[RegionIpDictionary][requiredregion]["extend_cidr_"+extendIndex] = cidr_returned
                                event[RegionIpDictionary][requiredregion]["extend_"+extendIndex+"_subnet_cidr_1"] = str(subnet_list[0])
                                event[RegionIpDictionary][requiredregion]["extend_"+extendIndex+"_subnet_cidr_2"] = str(subnet_list[1])
                                event["VPC_cidr_extend_number_"+regionkey.upper()] = extendIndex
                            else:
                                print("Its neither Private or Hybrid connectivity, Hence terminating the flow")
                        else:
                            print("CIDR not rteruned for VPC extension request, hence changing status of the request and Terminating Process")
                            self.send_failed_Snow_Resonse (event['CurrentVPCUpdateRequest']['RequestTaskNo'], event['CurrentVPCUpdateRequest']['AccountName'])
                            return False

                    if event['CurrentVPCUpdateRequest']['TaskType'] == "Non-routable subnets for existing VPC":
                        if ip.strip() == "Yes" :
                            print("region name : {} Non-routable VPC extension".format(requiredregion))
                            event[NonRoutableSubnetRequested] = "Yes"
                        else:
                            print("Looks like Non routable not asked for region: ",region)
                            event[NonRoutableSubnetRequested] = "No"
                    
        except Exception as e:
            print("Error occurred in fetching region: ", str(e))
            self.send_failed_Snow_Resonse (event['CurrentVPCUpdateRequest']['RequestTaskNo'], event['CurrentVPCUpdateRequest']['AccountName'])
            return False
        return True

    ## Get IP addresses
    def get_cidr(self,event, region,ip):
        '''Get IP from IP Management Table'''
        try:
            is_allocated = "FALSE"
            environmentkey = "private" if "Private" in self.Environment  else ("hybrid" if "Hybrid" in self.Environment else "NA")
            print("Environment of CIDR is", environmentkey)
            consolidated_key = ip + "|" + region + "|" + environmentkey.lower()
            print("consolidated key",consolidated_key)
            print("cidr table index : {} and cidr table name : {} ".format(self.cidr_table_index,self.cidr_table_name))
            query_response = self.dynamodb_client.query(TableName=self.cidr_table_name,
                                                        IndexName=self.cidr_table_index,
                                                        Select='ALL_PROJECTED_ATTRIBUTES', ConsistentRead=False,
                                                        KeyConditionExpression="consolidated_key = :ck AND is_allocated = :ia",
                                                        ExpressionAttributeValues={":ck": {"S": consolidated_key},
                                                                                    ":ia": {"S": is_allocated}})
            print("Query response: ", query_response)
            if len(query_response['Items']) < 1:
                print("No free CIDR ranges available to provision the VPC")
                print("VPC creation process will fail")
                self.send_email(consolidated_key,self.Business_account)
                self.send_failed_Snow_Resonse (event['RequestEventData']['RequestTaskNo'], event['ProvisionedProduct']['Name'])
                return False
            insert_response = self.dynamodb_client.put_item(
                TableName=self.cidr_table_name,
                Item={
                    'cidr': {"S": query_response['Items'][0]['cidr']['S']},
                    'available_ips': {"S": ip},
                    'is_allocated': {"S": 'FLAG'},
                    'region': {"S": region},
                    'consolidated_key': {"S": consolidated_key},
                    'environment': {"S": environmentkey}
                })
            print("Dynamo DB record is updated ", insert_response)
            return query_response['Items'][0]['cidr']['S']
        except Exception as e:
            print("Error occurred in Get CIDR function: ", str(e))
            self.send_failed_Snow_Resonse (event['RequestEventData']['RequestTaskNo'], event['ProvisionedProduct']['Name'])
            return False

    ## Store the parameters.json in S3 bucket
    def CreateRecordInS3bucket(self, event):
        print("Recording with event {}".format(event))
        try:
            print("Inside function to create the dynamic .json file...")
            s3_file_name =  event['ProvisionedProduct']['AccountNumber'] + "/parameters.json"
            print("s3 bucket path to store account parameter.json file would be  {}".format(s3_file_name))
            local_file_path = "/tmp/payload.json"
            print("file path:{}".format(local_file_path))
            with open(local_file_path, 'w') as fp:
                json.dump(event, fp)
            print("event is stored in local json file")
            self.s3_client.meta.client.upload_file(local_file_path,self.githubaction_parameter_bucket, s3_file_name)
            print("file uploaded successfully..")
            os.remove(local_file_path)
            print("File deleted after upload to s3 bucket")
        except Exception as exception:
            print("Exception in Lambda Handler and error is {}".format(exception))
            self.send_failed_Snow_Resonse (event['RequestEventData']['RequestTaskNo'], event['ProvisionedProduct']['Name'])

    ## Get Secrets from AWS secrete manager service name "IntegrationCreds"
    def get_secret(self, secret_name):
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

    ## Get SIMAAS Bearer Token
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

    ## Send Failed snow reponse
    def send_failed_Snow_Resonse (self, RequestTask, accountname):
        try:
            note = "Account request processing falied, please check integration workflow errors for account name:"+accountname
            api_data = json.loads(self.get_secret("IntegrationCreds-RARS"))
            if api_data :
                print("retrieved AWS secret manager data..")
                Bearer_token_data = self.get_SIMAAS_BearerToken(api_data['SIMAAS_URL'], api_data['SIMAAS_client_id'], api_data['SIMAAS_client_secret'],api_data['SIMAAS_username'],api_data['SIMAAS_password'])
                if Bearer_token_data :
                    print("SIMAAS bearer toaken is retrieved ...")
                    dynamicnowdata = datetime.datetime.now().strftime("%Y-%m-%d %I:%M:%S")
                    print("dynamic now date is framed..")
                    payload = json.dumps({
                            "u_supplier_reference": RequestTask,
                            "ice4u_target_id": RequestTask,
                            "u_work_notes": note,
                            "u_close_notes": "",
                            "u_state": "-5",
                            "u_short_description": "",
                            "u_description": "",
                            "u_due_date": dynamicnowdata,
                            "u_comments": ""
                        })
                    headers = { 'Authorization': 'Bearer '+Bearer_token_data['access_token'] , 'Content-Type': 'application/json'}
                    response = requests.request("POST", api_data['RARS_URL'], headers=headers, data=payload)
                    print(response.status_code)
                else:
                    print("Failed to get SIMAAS bearer toaken...")
            else:
                print("failed at getting required secrets from AWS secret manager..")
        except Exception as exception:
            print("Exception while sending response to Snow and error is {}".format(exception))
        else:
            if response.status_code :
                print("RARS API response status has been returned and value is:{}".format(response.status_code))
                return response.status_code
            else :
                print("No status code has been returned...")  

    ## Send cidr emails
    def send_email(self, ip,account_name):
        try:
            # This address must be verified with Amazon SES.
            sender_id = self.sender_id
            session = boto3.session.Session()
            ses_client = session.client('ses')

            # The email body for recipients with non-HTML email clients.
            body_text = "Hello Team,\r\n VPC Creation/Extension for Account " + account_name+\
                        " failed as the CIDR blocks for " + str(ip) + " exhausted.\
                        Please add more IPs to IP Management table in master account and update the network product."

            # The HTML body of the email.
            body_html = """
                                <html>
                                <head></head>
                                <body>
                                <h2>Hello Team,</h2>
                                <p>VPC Creation/Extension for Account """ + account_name+\
                                 """ failed as the CIDR blocks for """ + str(ip) + """ exhausted.\
                                  Please add more IPs to IP Management table in master account and update the network product.</p>
                                <p>Regards,</p>
                                <p>Cloud Services Team</p>
                                </body>
                                </html>
                                """

            # Provide the contents of the email.
            send_mail_response = ses_client.send_email(
                Source=sender_id,
                Destination={
                    'ToAddresses': [self.operations_dl]
                },
                Message={
                    'Subject': {
                        'Data': 'VPC Creation/extension Failed'

                    },
                    'Body': {
                        'Text': {
                            'Data': body_text

                        },
                        'Html': {
                            'Data': body_html

                        }
                    }
                }
            )
            print(send_mail_response)
            return send_mail_response
        except Exception as e:
            print(str(e))
            return str(e)

def lambda_handler(event, context):
    try:
        print("event data is: {}".format(json.dumps(event)))
        print("Received a {} Request".format(event['RequestType']))
        GetParamenterObject = GetParameters(event, context)
        GetParamenterObject.prepare_ssm_parameters_dict(event)
        GetParamenterObject.get_region_ip(event)
        GetParamenterObject.add_security_hub_control_IDs(event)
        GetParamenterObject.add_env_type(event)
        GetParamenterObject.add_eks_amis(event)
        GetParamenterObject.add_sso_parameters(event)
        if event["RequestType"] == "Create" :
            print("Its Create request hence creating Region IP adress dictionary dynamically.")
            if GetParamenterObject.create_cidr_dictionaries(event):
                print("Creating required IP Address dictionary is successful..")
                GetParamenterObject.add_vpc_extension_index(event, 0)
                event['IsParametersFileComplete'] = True
            else :
                print("Creating required IP Address dictionary is Failed..")
                event['IsParametersFileComplete'] = False
        elif event["RequestType"] == "Update" :
            print("Request type is Update hence adding parameters as True")
            event['IsParametersFileComplete'] = True
        elif event["RequestType"] == "Delete" :
            print("Request type is Delete hence adding parameters as True")
            event['IsParametersFileComplete'] = True
        else:
            print("Request type is Not allowed hence adding parameters as False")
            event['IsParametersFileComplete'] = False
        if 'CurrentVPCUpdateRequest' in event :
            print("Its update request for VPC extension hence.")
            if GetParamenterObject.create_extend_cidr_dictionaries(event):
                print("Creating required IP Address dictionary is successful..")
                event['IsParametersFileComplete'] = True
            else :
                print("Creating required IP Address dictionary is Failed..")
                event['IsParametersFileComplete'] = False
        GetParamenterObject.CreateRecordInS3bucket(event)
    except Exception as exception:
        print("exception happend in parameters lambda: ", exception)
        event['IsParametersFileComplete'] = False
    return event