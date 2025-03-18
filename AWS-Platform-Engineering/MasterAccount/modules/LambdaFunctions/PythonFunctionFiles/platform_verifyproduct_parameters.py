import json
import logging
import boto3
import requests
import datetime
import time

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
LOGGER.addHandler(CH)
SUCCESS = "SUCCESS"
FAILED = "FAILED"

"""
This Lambda function is used to Verify if the parameter set the service catalog are correct.
"""


class VerifyParameters(object):
    def __init__(self, event, context):
        self.exception = []
        self.event = event
        self.context = context
        self.request_type = event['RequestType']
        self.resource_properties = self.event["ResourceProperties"]
        self.Environment = self.resource_properties["Environment"]
        self.completedTimeStamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.reason_data = ""
        self.response_data = {}
        self.str_parameter_is_verified = "Parameters are verified"
        session_client = boto3.session.Session()
        self.ssm_client = session_client.client('ssm')


    def prepare_ssm_parametres_dict(event):
        """
        aim: prepare ssm obejct andappend it to the event for reuse by upcoming states
        param : self
        return: event with updated ssm parametres
        """
        LOGGER.info("Start SSM Parametres preparation")
        ssm_parametres_dict = {}
        agent_rapid7_parametres = ["platform_pub_rapid7_linuxpath","platform_rapid7_linux_filename","platform_pvt_rapid7_linuxpath","platform_pub_rapid7_winpath","platform_rapid7_win_filename","platform_pvt_rapid7_winpath","failure_operation_dl"]
        agent_falcon_parametres = ["platform_pub_falcon_linuxpath","platform_falcon_linux_filename","platform_pvt_falcon_linuxpath","platform_pub_falcon_winpath","platform_falcon_win_filename","platform_pvt_falcon_winpath"]
        agent_cloudhealth_parametres = ["platform_cloudhealth_external_id","platform_cloudhealth_account","platform_pub_ch_linuxpath","platform_ch_linux_filename","platform_pvt_ch_linuxpath","platform_pub_ch_winpath","platform_ch_win_filename","platform_pvt_ch_winpath"]
        agent_flexera_parametres = ["platform_pub_flexera_linuxpath","platform_pvt_flexera_linuxpath_us","platform_pvt_flexera_linuxpath_eu","platform_flexera_linux_filename","platform_pub_flexera_winpath","platform_pvt_flexera_winpath_us","platform_pvt_flexera_winpath_eu","platform_flexera_win_filename"]
        domain_join_parametres = ["domainjoin_linuxpreURL","domainjoin_linuxpath", "domainjoin_linux_prefilename","domainjoin_windows_url","domainjoin_windows_path", "domainjoin_windows_filename"]
        opeartions_parametres = ["accountDetailTableName","dlTableName","success_operation_dl","sender_id","create_case_ccadress","domainjoin_linuxmainURL","domainjoin_linux_mainfilename","Private_whitelisted_region","platform_pub_flexera_winpath","whitelisted_regions"]
        organizational_units_parametres = ["Private-Production","Private-Staging","Private-Exception","Public-Exception","Public-Staging","Public-Production","Data-Management","platform_ou_decommission","Hybrid-Account", "Migration-Account"]
        ami_parametres = ["TOE_Complaint_OS_Flavours_Public","TOE_Complaint_OS_Flavours_Private","ami_owner_account","ami_tags"]
        admin_parametres_part1 = ["whitelisted_regions_private","whitelisted_regions_public","AFproductid","admin_account","iam_mgmnt_account","audit_account","platform_network_product_id","platform_agent_bucket","execution_timeout","agent_bucket"]
        admin_parametres_part2 = ["platform_linux_dirpath","platform_execution_timeout","platform_win_dirpath"]
        ssm_parametres = {}
        ssm_parametres["Flexera"] = agent_flexera_parametres
        ssm_parametres["Rapid7"] = agent_rapid7_parametres
        ssm_parametres["Cloudhealth"] = agent_cloudhealth_parametres
        ssm_parametres["Falcon"] = agent_falcon_parametres
        ssm_parametres["OU"] = organizational_units_parametres
        ssm_parametres["DomainJoin"] = domain_join_parametres
        ssm_parametres["Admin1"] = admin_parametres_part1
        ssm_parametres["Admin2"] =admin_parametres_part2
        ssm_parametres["AMI"] = ami_parametres
        ssm_parametres["Opeartions"] = opeartions_parametres
        for parametre in ssm_parametres:
            ssm_param_client = boto3.client('ssm')
            retries = 0
            get_param_status = 'False'
            try:
                while retries < 4 and get_param_status == 'False':
                    #get ssm here
                    response = ssm_param_client.get_parameters(
                        Names=ssm_parametres[parametre],
                        WithDecryption=True)
                    temp_res_code = response['ResponseMetadata']['HTTPStatusCode']
                    if temp_res_code == 200:
                        get_param_status = 'True'
                        response_parametres = response['Parameters']
                        for param in response_parametres:
                            ssm_parametres_dict[param['Name']] = param['Value']
                    else: 
                        time_to_sleep = 2 ** retries
                        retries += 1
                        time.sleep(time_to_sleep)
                    
            except Exception as exception:
                LOGGER.error(exception)
        event['SSMParametres'] = ssm_parametres_dict
    
    def get_region_ip(self):
        '''
        Method to get the region and ip, add regions here in case of more region to be updated
        '''
        try:
            ssm = boto3.client('ssm')
            region_ip_dict = {}
            LOGGER.info("Inside get region ip")
            if "Private" in self.Environment:
                print("its private account...")
                for region_name in self.resource_properties.keys():
                    if region_name == 'NVirginia' and self.resource_properties[region_name] != "No-VPC":
                        region_ip_dict.update({"us-east-1": self.resource_properties[region_name]})
                    if region_name == 'Ireland' and self.resource_properties[region_name] != "No-VPC":
                        region_ip_dict.update({"eu-west-1": self.resource_properties[region_name]})
                    if region_name == 'Singapore' and self.resource_properties[region_name] != "No-VPC":
                        region_ip_dict.update({"ap-southeast-1": self.resource_properties[region_name]})                       
                print(region_ip_dict)
            if "Hybrid-Account" in self.Environment:
                print("its hybrid-account account...")
                for region_name in self.resource_properties.keys():
                    if region_name == 'NVirginia' and self.resource_properties[region_name] != "No-VPC":
                        region_ip_dict.update({"us-east-1": self.resource_properties[region_name]})
                    if region_name == 'Ireland' and self.resource_properties[region_name] != "No-VPC":
                        region_ip_dict.update({"eu-west-1": self.resource_properties[region_name]})
                    if region_name == 'Singapore' and self.resource_properties[region_name] != "No-VPC":
                        region_ip_dict.update({"ap-southeast-1": self.resource_properties[region_name]}) 
                print(region_ip_dict)
            elif "Public" in self.Environment:
                public_region = self.event['SSMParametres']['whitelisted_regions_public'].split(",")
                for pub_region in public_region:
                    region_ip_dict.update({pub_region: "No-VPC"})
                print(region_ip_dict)
            elif "Migration" in self.Environment:
                migration_region = self.event['SSMParametres']['whitelisted_regions_public'].split(",")
                for mg_region in migration_region:
                    region_ip_dict.update({mg_region: "No-VPC"})
                print(region_ip_dict)
            elif "Managed_Services" in self.Environment:
                bea_region = self.event['SSMParametres']['whitelisted_regions_public'].split(",")
                for priv_region in bea_region:
                    region_ip_dict.update({priv_region: "No-VPC"})
                print(region_ip_dict)
            elif "Data-Management" in self.Environment:
                bea_region = self.event['SSMParametres']['whitelisted_regions_public'].split(",")
                for priv_region in bea_region:
                    region_ip_dict.update({priv_region: "No-VPC"})
                print(region_ip_dict)                
            self.event['region_ip_dict'] = region_ip_dict
            self.Region = list(region_ip_dict.keys())
            print(self.Region)
            return region_ip_dict
        except Exception as e:
            print("Error occurred in fetching region", str(e))

    """Fetch the OU"""
    def fetchAccountOU(self, email_id):
        account_organization = ""
        old_region = ""
        try:
            self.account_details_table = self.event['SSMParametres']['accountDetailTableName']
            self.dl_table = self.event['SSMParametres']['dlTableName']
            client = boto3.client('dynamodb')
            response = client.get_item(
                TableName=self.dl_table,
                Key={
                    'DLEmailId': {
                        'S': email_id}})
            print("DL_Details", response)
            if 'Item' in response and 'AccountNumber' in response['Item']:
                response = client.get_item(
                    TableName=self.account_details_table,
                    Key={
                        'AccountNumber': {
                            'S': response['Item']['AccountNumber']['S']}})
                print("Account_Details", response)
                if 'Item' in response and 'Organization' in response['Item']:
                    account_organization = response['Item']['Organization']['S']
                    old_region = response['Item']['EnabledRegion']['S']
                    return account_organization, old_region
            self.event['fetchAccountOU'] = "PASSED"
            return account_organization, old_region
        except Exception as e:
            print(str(e))
            self.exception.append(str(e))
            return account_organization, old_region

    """
    Check if the account creation request is correct based on if private account have the correct
    whitelisted regions into which the VPC listed will be created.
    """
    def verify_create_request(self):
        print("Inside Create Request")
        try:
            if "Private" in self.Environment :
                self.event["ResourceProperties"]["AccountType"] = "private"
                # Verify region only for Private
                isVerifiedRegion = self.verifyCreateRegion()
                if isVerifiedRegion == True:
                    isVerified = True
                    message = self.str_parameter_is_verified
                else:
                    isVerified = False
                    message = "Error accrued in the region field, Please make sure that the region is whitelisted for public or private account type"
            elif "Hybrid-Account" in self.Environment :
                self.event["ResourceProperties"]["AccountType"] = "hybrid"
                # Verify region only for Private
                isVerifiedRegion = self.verifyCreateRegion()
                if isVerifiedRegion == True:
                    isVerified = True
                    message = self.str_parameter_is_verified
                else:
                    isVerified = False
                    message = "Error accrued in the region field, Please make sure that the region is whitelisted for public or private/hybrid account type"
            elif "Public" in self.Environment:
                self.event["ResourceProperties"]["AccountType"] = "public"
                # For Public directly verify the region as we are not creating any VPCs
                self.event['verifyCreateRegion'] = "PASSED"
                isVerified = True
                message = self.str_parameter_is_verified
            elif "Migration" in self.Environment:
                self.event["ResourceProperties"]["AccountType"] = "public"
                # For Public directly verify the region as we are not creating any VPCs
                self.event['verifyCreateRegion'] = "PASSED"
                isVerified = True
                message = self.str_parameter_is_verified
            elif "Managed_Services" in self.Environment:
                self.event["ResourceProperties"]["AccountType"] = "Managed_Services"
                # For Be.Agile directly verify the region as we are not creating any VPCs
                self.event['verifyCreateRegion'] = "PASSED"
                isVerified = True
                message = self.str_parameter_is_verified            
            elif "Data-Management" in self.Environment:
                self.event["ResourceProperties"]["AccountType"] = "Data-Management"
                # For Data Management directly verify the region as we are not creating any VPCs
                self.event['verifyCreateRegion'] = "PASSED"
                isVerified = True
                message = self.str_parameter_is_verified
            self.event['verify_create_request'] = "PASSED"
        except Exception as e:
            print(e)
            isVerified = False
            message = "Error accrued in the region field, Please make sure that the region is whitelisted for public or private account type"
            self.exception.append(str(e))
        return isVerified, message

    """
    Check if update request has valid regions
    """
    def verify_update_request(self, old_region, oldenvlist, newenvlist):
        print("Inside verify_update_request")
        try:
            if oldenvlist[0] == newenvlist[0]:
                if "Public" in self.Environment:
                    self.event["ResourceProperties"]["AccountType"] = "public"
                    isVerified = True
                    self.event['verifyUpdateRegion'] = "PASSED"
                    self.event['verify_all_regions_valid'] = "PASSED"
                    message = self.str_parameter_is_verified

                elif "Private" in self.Environment:
                    self.event["ResourceProperties"]["AccountType"] = "private"
                    isVerifiedRegion = self.verifyUpdateRegion(old_region)
                    print("isVerifiedRegion", isVerifiedRegion)
                    if (isVerifiedRegion == True):
                        isVerified = True
                        message = self.str_parameter_is_verified
                    else:
                        isVerified = False
                        message = "Error accrued in region field, Please make sure that the old regions are listed " \
                                  "in the new region field and make sure that the region is whitelisted for public" \
                                  "or private account type"
                elif "Hybrid-Account" in self.Environment:
                    self.event["ResourceProperties"]["AccountType"] = "hybrid"
                    isVerifiedRegion = self.verifyUpdateRegion(old_region)
                    print("isVerifiedRegion", isVerifiedRegion)
                    if (isVerifiedRegion == True):
                        isVerified = True
                        message = self.str_parameter_is_verified
                    else:
                        isVerified = False
                        message = "Error accrued in region field, Please make sure that the old regions are listed " \
                                  "in the new region field and make sure that the region is whitelisted for public" \
                                  "or private/hybrid account type"
                elif "Managed_Services" in self.Environment:
                       self.event["ResourceProperties"]["AccountType"] = "Managed_Services"
                       isVerified = True
                       self.event['verifyUpdateRegion'] = "PASSED"
                       self.event['verify_all_regions_valid'] = "PASSED"
                       message = self.str_parameter_is_verified
                elif "Data-Management" in self.Environment:
                       self.event["ResourceProperties"]["AccountType"] = "Data-Management"
                       isVerified = True
                       self.event['verifyUpdateRegion'] = "PASSED"
                       self.event['verify_all_regions_valid'] = "PASSED"
                       message = self.str_parameter_is_verified
                elif "Migration" in self.Environment:
                       self.event["ResourceProperties"]["AccountType"] = "public"
                       isVerified = True
                       self.event['verifyUpdateRegion'] = "PASSED"
                       self.event['verify_all_regions_valid'] = "PASSED"
                       message = self.str_parameter_is_verified
            elif oldenvlist[0] == 'Migration' and newenvlist[0] == 'Public':
                self.event["ResourceProperties"]["AccountType"] = "public"
                isVerified = True
                self.event['verifyUpdateRegion'] = "PASSED"
                self.event['verify_all_regions_valid'] = "PASSED"
                message = self.str_parameter_is_verified
            elif oldenvlist[0] == 'Hybrid' and newenvlist[0] == 'Private':
                self.event["ResourceProperties"]["AccountType"] = "private"
                isVerified = True
                self.event['verifyUpdateRegion'] = "PASSED"
                self.event['verify_all_regions_valid'] = "PASSED"
                message = self.str_parameter_is_verified
            elif oldenvlist[0] == 'Hybrid' and newenvlist[0] == 'Managed_Services':
                self.event["ResourceProperties"]["AccountType"] = "Managed_Services"
                isVerified = True
                self.event['verifyUpdateRegion'] = "PASSED"
                self.event['verify_all_regions_valid'] = "PASSED"
                message = self.str_parameter_is_verified
            elif oldenvlist[0] == 'Private' and newenvlist[0] == 'Managed_Services':
                self.event["ResourceProperties"]["AccountType"] = "Managed_Services"
                isVerified = True
                self.event['verifyUpdateRegion'] = "PASSED"
                self.event['verify_all_regions_valid'] = "PASSED"
                message = self.str_parameter_is_verified
            elif oldenvlist[0] == 'Public' and newenvlist[0] == 'Managed_Services':
                self.event["ResourceProperties"]["AccountType"] = "Managed_Services"
                isVerified = True
                self.event['verifyUpdateRegion'] = "PASSED"
                self.event['verify_all_regions_valid'] = "PASSED"
                message = self.str_parameter_is_verified
            else:
                isVerified = False
                message = "Account type  can not be changed from public to private or vice-versa"
            self.event['verify_update_request'] = "PASSED"
        except Exception as e:
            print("Execption")
            print(str(e))
            isVerified = False
            message = str(e)
            self.exception.append(str(e))
        print("Done verify_update_request")
        print(isVerified, message)
        return isVerified, message

    def verifyEnvironment(self):
        isVerified = False
        message = ""
        try:
            print("inside verifyEnvironment")
            """
            Verify if the Account is created or updated on based on if the PPID and Account Number are present in the event
            """
            if self.request_type == "Create" or (
                    self.event['ppid'] == "No-ppid" and self.event['accountNumber'] == "No-AccountID"):
                # if self.request_type == "Create":
                self.event['RequestType'] = "Create"
                isVerified, message = self.verify_create_request()

            elif self.request_type == "Update":
                account_organization, old_region = self.fetchAccountOU(self.event['dlForNewAccount'])
                print("OU", "Region")
                print(account_organization, old_region)
                if account_organization != "" and len(old_region) > 0:
                    oldenvlist = account_organization.split("-")
                    newenvlist = self.Environment.split("-")
                    isVerified, message = self.verify_update_request(old_region, oldenvlist, newenvlist)
                else:
                    isVerified = False
                    message = "Account type or region details are not available in Account Detail Table"
            elif self.request_type == "Delete":
                isVerified = True
                message = self.str_parameter_is_verified
        except Exception as e:
            print(str(e))
            isVerified = False
            message = str(e)
            self.exception.append(str(e))

        print(message)
        """
        *
        *If the Verification fails send the below resopnse.
        *
        """
        self.reason_data = message
        if (isVerified == False and self.request_type == "Create"):
            print(isVerified, "Create", "isVerified")
            self.response_data = {
                'AccountName': self.event['ResourceProperties']['AccountName'],
                'Ppid': "No-ppid",
                'DistributionID': "No-DL",
                "AccountNumber": "No-AccountID",
                'CompletedTimestamp': self.completedTimeStamp

            }
            self.send_status(SUCCESS)
        elif (isVerified == False and self.request_type == "Update"):
            print(isVerified, "Update", "isVerified")
            self.response_data = {
                'AccountName': self.event['ResourceProperties']['AccountName'],
                'Ppid': self.event['ppid'],
                'DistributionID': self.event['dlForNewAccount'],
                "AccountNumber": self.event['accountNumber'],
                'CompletedTimestamp': self.completedTimeStamp
            }
            self.send_status(SUCCESS)
        # elif (isVerified == False and self.request_type == "Delete"):
        #     print (isVerified,"Delete","isVerified")
        #     response_data = {
        #         'AccountName': self.event['ResourceProperties']['AccountName'],
        #         'Ppid': self.event['ppid'],
        #         'DistributionID': self.event['dlForNewAccount'],
        #         "AccountNumber": self.event['accountNumber'],
        #         'CompletedTimestamp': self.completedTimeStamp
        #     }
        #     self.send(event=self.event, context=self.context, response_status=SUCCESS, response_data=response_data,
        #               reason_data=reason_data)
        self.event['verifyEnvironment'] = "PASSED"
        return self.event, isVerified, message

    """
    Verify if the region is whitelisted if the Account is private 
    """
    def verifyCreateRegion(self):
        isVerified = False
        try:
            regionList = self.Region
            print(regionList)
            ssm = boto3.client('ssm')
            account_type = self.event["ResourceProperties"]["AccountType"]
            SSM_REGION = None
            #if (account_type == "public"):
                #parameter = ssm.get_parameter(Name='whitelisted_regions_public')
                #SSM_REGION = parameter['Parameter']['Value']
            if (account_type == "private"):
                SSM_REGION= self.event['SSMParametres']['whitelisted_regions_private']

            if (account_type == "hybrid"):
                SSM_REGION= self.event['SSMParametres']['whitelisted_regions_private']

            if SSM_REGION != None:
                for region in regionList:
                    if region not in SSM_REGION:
                        isVerified = False
                        break
                    else:
                        isVerified = True
            else:
                isVerified = False
            self.event['verifyCreateRegion'] = "PASSED"
        except Exception as e:
            print(e)
            isVerified = False

        return isVerified

    """
    Check if the regions listed are correct and white listed
    """
    def verify_all_regions_valid(self, regionList):
        isVerified = False
        try:
            ssm = boto3.client('ssm')
            account_type = self.event["ResourceProperties"]["AccountType"]
            SSM_REGION = None
            #if (account_type == "public"):
                #parameter = ssm.get_parameter(Name='whitelisted_regions_public')
                #SSM_REGION = parameter['Parameter']['Value']
            if (account_type == "private"):
                SSM_REGION = self.event['SSMParametres']['whitelisted_regions_private']

            if (account_type == "hybrid"):
                SSM_REGION = self.event['SSMParametres']['whitelisted_regions_private']

            if SSM_REGION != None:
                for region in regionList:
                    if region not in SSM_REGION:
                        isVerified = False
                        self.event['verify_all_regions_valid'] = "PASSED"
                        break
                    else:
                        isVerified = True
            else:
                isVerified = False
            self.event['verify_all_regions_valid'] = "PASSED"
        except Exception as e:
            print(str(e))
            isVerified = False

        return isVerified

    def verifyUpdateRegion(self, old_regions):
        print("Inside Verify Region")
        isVerified = False
        try:
            regionList = self.Region
            oldRegionList = [x.strip(' ') for x in old_regions.split(",")]

            print(regionList)
            print(oldRegionList)
            isAllOldRegionsPresent = True
            for old_region_item in oldRegionList:
                if old_region_item not in regionList:
                    isAllOldRegionsPresent = False
                    break

            if isAllOldRegionsPresent == True:
                isVerified = self.verify_all_regions_valid(regionList)
            else:
                isVerified = False
            self.event['verifyUpdateRegion'] = "PASSED"
        except Exception as e:
            print(e)
            isVerified = False
        return isVerified

    def send_status(self, pass_or_fail):
        '''
        Send the status of the Child Account Creation to  Cloudformation Template.
        '''
        self.send1(
            event=self.event,
            context=self.context,
            response_status=pass_or_fail,
            response_data=self.response_data,
            reason_data=self.reason_data
        )

    def send1(self, event, context, response_status, response_data, reason_data):
        '''
        Called by send status to send the status
        '''
        print("Inside send method")
        response_url = event['ResponseURL']

        response_body = {}
        response_body['Status'] = response_status
        response_body['Reason'] = reason_data + \
                                  ' See the details in CloudWatch Log Stream: ' + context.log_stream_name
        response_body['PhysicalResourceId'] = context.log_stream_name
        response_body['StackId'] = event['StackId']
        response_body['RequestId'] = event['RequestId']
        response_body['LogicalResourceId'] = event['LogicalResourceId']
        response_body['Data'] = response_data

        json_response_body = json.dumps(response_body)

        print("Response body:{}".format(json_response_body))

        headers = {
            'content-type': '',
            'content-length': str(len(json_response_body))
        }

        try:
            response = requests.put(response_url,
                                    data=json_response_body,
                                    headers=headers)
            print("Status code:{} ".format(response.reason))
            self.event['send1'] = "PASSED"
        except Exception as exception:
            print("send(..) failed executing requests.put(..):{} ".format(
                str(exception)))


def lambda_handler(event, context):
    try:
        LOGGER.info(json.dumps(event))
        print("Received a {} Request".format(event['RequestType']))
        verifyParamenters = VerifyParameters(event, context)
        VerifyParameters.prepare_ssm_parametres_dict(event)
        verifyParamenters.get_region_ip()
        event, isVerified, message = verifyParamenters.verifyEnvironment()
        event['VerifiedParameters'] = isVerified
        print(message)
        if isVerified == False:
            event['emailParameter'] = []
            event['emailParameter'].append("VerifiedParameterFailure")
            event['VerifiedParametersError'] = message
        print(json.dumps(event))

    except Exception as exception:
        print(exception)
        event['VerifiedParameters'] = False
        event['emailParameter'] = []
        event['emailParameter'].append("VerifiedParameterFailure")
        event['VerifiedParametersError'] = str(exception)

    return event