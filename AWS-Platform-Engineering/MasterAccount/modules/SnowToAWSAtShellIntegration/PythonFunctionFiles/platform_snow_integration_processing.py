# This lambda was updated as part of RARS Migration from 1.0 to 2.0
import boto3
import datetime
import json
import os
from botocore.exceptions import ClientError
import base64
import requests

class UpdateChildAccount(object):

    ## init function
    def __init__(self, event, context):
        try:
            self.reason_data = ""
            self.event = event
            self.context = context
            SESSION = boto3.Session()
            self.servicecatalogclient = SESSION.client('servicecatalog' , region_name="us-east-1")
            self.cloudformationclient = SESSION.client('cloudformation' , region_name="us-east-1")  
            self.sqs_client = SESSION.client('sqs', region_name="us-east-1")
            self.secretManager_client = SESSION.client('secretsmanager', region_name="us-east-1")
            self.s3_client = boto3.resource('s3')
            SSM_client = SESSION.client('ssm', region_name="us-east-1")
            avm_productid  = SSM_client.get_parameter(Name='AVMproductid')
            self.avm_productid = avm_productid['Parameter']['Value']
            snow_integration_log_bucket  = SSM_client.get_parameter(Name='SnowIntegrationLogBucket')
            self.snow_integration_log_bucket = snow_integration_log_bucket['Parameter']['Value']
        except Exception as exception:
            self.reason_data = "Missing required property %s" % exception
    
    ## Create log file s3 bucket for tracking.
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

    ## Get provisioned product parameters from stack
    def get_provisionedproduct_parameters(self, stackid, event):
        try:
            parameters_list = [ ] 
            stacksdata =  self.cloudformationclient.describe_stacks(StackName=stackid)
            if (stacksdata['Stacks']) :
                for eachstack in stacksdata['Stacks']:
                    eachstackparameters = eachstack['Parameters']
                    if(eachstackparameters):
                        keyvaluepairs = {}
                        for parameters in eachstackparameters:
                            if(parameters['ParameterKey'] == "UpdateIndex"):
                                keyvaluepairs.update({ parameters['ParameterKey']: str(int(parameters['ParameterValue']) + 1)})
                            elif (parameters['ParameterKey'] in event):
                                keyvaluepairs.update({ parameters['ParameterKey']: event[parameters['ParameterKey']]})
                            else:
                                keyvaluepairs.update({ parameters['ParameterKey']: parameters['ParameterValue']})
                        parameters_list.append(keyvaluepairs)
            return parameters_list
        except Exception as ex:
            print("Exception occured while running get_provisionedproduct_parameters and error is {}".format(ex)) 

    ## Get newly provisioned  account number from stack if "AVAILABLE" status from stack
    def get_newlyprovisioned_accountnumber(self, stackid):
        try:
            stacksdata =  self.cloudformationclient.describe_stacks(StackName=stackid)
            if (stacksdata['Stacks']) :
                for eachstack in stacksdata['Stacks']:
                    eachstackoutputs = eachstack['Outputs']
                    if(eachstackoutputs):
                        for outputs in eachstackoutputs:
                            if outputs['OutputKey'] == "AccountNumber" :
                                return outputs['OutputValue']
            return False   
        except Exception as ex:
            print("Exception occured while running get_provisionedproduct_outputs and error is {}".format(ex))

    ## Get provisioned product outputs from stack
    def get_provisionedproduct_outputs(self, stackid, AccountNumber):
        try:
            stacksdata =  self.cloudformationclient.describe_stacks(StackName=stackid)
            if (stacksdata['Stacks']) :
                for eachstack in stacksdata['Stacks']:
                    eachstackoutputs = eachstack['Outputs']
                    if(eachstackoutputs):
                        for outputs in eachstackoutputs:
                            if(outputs['OutputKey'] == "AccountNumber" and outputs['OutputValue'] == (AccountNumber.strip())):
                                return True
            return False   
        except Exception as ex:
            print("Exception occured while running get_provisionedproduct_outputs and error is {}".format(ex)) 

    ## Get provisioned products with status "Active"
    def get_available_product(self):
        try:
            account_list = []
            response = self.servicecatalogclient.search_provisioned_products(Filters={"SearchQuery":["productName:platform_avm_product"]})
            result = response['ProvisionedProducts']
            while 'NextPageToken' in response:
                response = self.servicecatalogclient.scan(Filters={"SearchQuery":["productName:platform_avm_product"]}, PageToken=response['NextPageToken'])
                result.extend(response['ProvisionedProducts'])
            if (result):
                for item in result:
                    if item['Status'] == 'AVAILABLE':
                        account_list.append(item)
            return account_list
        except Exception as ex:
            print("Exception occured while running search_provisioned_products and error is {}".format(ex))

    ## Create product info dictionary when it is account to be updated.
    def get_available_product_info(self, listofpp, event):
        try:
            product_list = {"RequestType" : "Update", "RequestEventData": event, "RequestNo" : event['RequestNo'], "IsUpdateComplete": False, "ProvisionedProductList":[]}
            for eachproduct in listofpp:
                if(self.get_provisionedproduct_outputs(eachproduct['PhysicalId'], event['AccountNumber'])):
                    requireddatadict = {}
                    parameterslist = self.get_provisionedproduct_parameters(eachproduct['PhysicalId'],event)
                    requireddatadict.update({ "Name" : eachproduct['Name'], 
                                            "Id": eachproduct['Id'], 
                                            "ProductId": eachproduct['ProductId'], 
                                            "ProductName": eachproduct['ProductName'],
                                            "ProvisioningArtifactId": eachproduct['ProvisioningArtifactId'],
                                            "ParametersList": parameterslist,
                                            "IsUpdated": False,
                                            "IsUpdateGoing": False,
                                            "StatusAfterUpdate": "",
                                            "AccountNumber" : event['AccountNumber']
                                            })
                    product_list['ProvisionedProductList'].append(requireddatadict)
                    break
            return product_list
        except Exception as ex:
            print("Exception occured while running get_available_product_info and error is {}".format(ex))

    ## Invoking provisoned products update task.
    def invoke_update_provision_product(self, event, account):
        try:
            provision_artifact = " "
            pa_res = self.servicecatalogclient.list_provisioning_artifacts(ProductId=account['ProductId'])
            for pa in pa_res['ProvisioningArtifactDetails']:
                if pa['Active']:
                    provision_artifact = pa['Id']
                    print("Provisioning Artifact ID:", pa['Id'])
            response = " "
            if(provision_artifact):
                print("I am here in last IF condition of Invoking provisoned products update task....")
                response = self.servicecatalogclient.update_provisioned_product(
                    ProvisionedProductId=account['Id'],
                    ProductId=account['ProductId'],
                    ProvisioningArtifactId=provision_artifact,
                    ProvisioningParameters=[
                        {
                            "Key": "SoldToCode",
                            "Value": account['ParametersList'][0]['SoldToCode']
                        },
                        {
                            "Key": "NVirginia",
                            "Value": account['ParametersList'][0]['NVirginia']
                        },
                        {
                            "Key": "CustodianUserFirstName",
                            "Value": account['ParametersList'][0]['CustodianUserFirstName']
                        },
                        {
                            "Key": "UpdateIndex",
                            "Value": account['ParametersList'][0]['UpdateIndex']
                        },
                        {
                            "Key": "RequestorEmail",
                            "Value": account['ParametersList'][0]['RequestorEmail']
                        },
                        {
                            "Key": "CustodianUser",
                            "Value": account['ParametersList'][0]['CustodianUser']
                        },
                        {
                            "Key": "SupportDL",
                            "Value": account['ParametersList'][0]['SupportDL']
                        },
                        {
                            "Key": "Ireland",
                            "Value": account['ParametersList'][0]['Ireland']
                        },
                        {
                            "Key": "Singapore",
                            "Value": account['ParametersList'][0]['Singapore']
                        },                        
                        {
                            "Key": "RootDL",
                            "Value": account['ParametersList'][0]['RootDL']
                        },
                        {
                            "Key": "ApexID",
                            "Value": account['ParametersList'][0]['ApexID']
                        },
                        {
                            "Key": "Environment",
                            "Value": account['ParametersList'][0]['Environment']
                        },
                        {
                            "Key": "CustodianUserLastName",
                            "Value": account['ParametersList'][0]['CustodianUserLastName']
                        },
                        {
                            "Key": "Budget",
                            "Value": account['ParametersList'][0]['Budget']
                        },
                        {
                            "Key": "AccountMigration",
                            "Value": account['ParametersList'][0]['AccountMigration']
                        },
                        {
                            "Key": "LOB",
                            "Value": account['ParametersList'][0]['LOB']
                        },
                        {
                            "Key": "RequestNo",
                            "Value": account['ParametersList'][0]['RequestNo']
                        },
                        {
                            "Key": "AccountName",
                            "Value": account['ParametersList'][0]['AccountName']
                        },
                        {
                            "Key": "WorkloadType",
                            "Value": account['ParametersList'][0]['WorkloadType']
                        },
                        {
                            "Key": "BusinessContributors",
                            "Value": account['ParametersList'][0]['BusinessContributors']
                        },
                        {
                            "Key": "BusinessOperators",
                            "Value": account['ParametersList'][0]['BusinessOperators']
                        },
                        {
                            "Key": "BusinessLimitedOperators",
                            "Value": account['ParametersList'][0]['BusinessLimitedOperators']
                        },
                        {
                            "Key": "BusinessReadOnly",
                            "Value": account['ParametersList'][0]['BusinessReadOnly']
                        },
                        {
                            "key": "BusinessCustom",
                            "Value": account['ParametersList'][0]['BusinessCustom']
                        },
                        {
                            "Key": "SOXrelevant",
                            "Value": account['ParametersList'][0]['SOXrelevant']
                        },
                        {
                            "Key": "ActiveBIAid",
                            "Value": account['ParametersList'][0]['ActiveBIAid']
                        },
                        {
                            "Key": "DataClassification",
                            "Value": account['ParametersList'][0]['DataClassification']
                        },
                        {
                            "Key": "AccountTenancy",
                            "Value": account['ParametersList'][0]['AccountTenancy']
                        },
                        {
                            "Key": "IsIOTAccount", ## Is IOT Account
                            "Value": account['ParametersList'][0]['IsIOTAccount']
                        },
                        {
                            "Key": "IsRESPCAccount", ## Is RESPC Account
                            "Value": account['ParametersList'][0]['IsRESPCAccount']
                        },
                        {
                            "Key": "IsNonroutableSubnets", ## Is Non Routable Subnet
                            "Value": account['ParametersList'][0]['IsNonroutableSubnets']
                        },
                        {
                            "Key": "HybridRESPCAccountDomainJoinOUName", ## Hybrid RESPC Account Domain Join OU Name
                            "Value": account['ParametersList'][0]['HybridRESPCAccountDomainJoinOUName']
                        },
                        {
                            "Key": "IsDatabricksAccount",
                            "Value": account['ParametersList'][0]['IsDatabricksAccount']
                        },
                        {
                            "Key": "DatabricksEnvironment",
                            "Value": account['ParametersList'][0]['DatabricksEnvironment']
                        },
                        {
                            "Key": "DatabricksVolumeRequired",
                            "Value": account['ParametersList'][0]['DatabricksVolumeRequired']
                        },
                        {
                            "Key": "DatabricksS3Region",
                            "Value": account['ParametersList'][0]['DatabricksS3Region']
                        },
                        {
                            "Key": "DatabricksProjectID",
                            "Value": account['ParametersList'][0]['DatabricksProjectID']
                        }                                            
                    ]  
                )
                print(response)
            else:
                print("Provisioning Artifact ID not found for account : {}".format(account['Name']))
                exit()
        except Exception as exception:
            print("Exception occured while running invoke_update_provision_product and error is {}".format(exception))
            self.send_failed_Snow_Resonse(event['RequestTaskNo'], account['ParametersList'][0]['AccountName'])
        status = response['RecordDetail']['Status']
        if status == "FAILED" or status == "IN_PROGRESS_IN_ERROR" :
            self.send_failed_Snow_Resonse(event['RequestTaskNo'], account['ParametersList'][0]['AccountName'])
        return response

    ## Invoking provisoned products creation task.
    def invoke_create_provision_product(self, event):
        try:
            provision_artifact = " "
            # initializing bad_chars_list
            bad_chars = [";", ":", "!", "*", "@", "#", "$", "%", "^", "&", "(", ")", "[", "]", "{", "}", "?", "/", ".", "_"]
            pa_res = self.servicecatalogclient.list_provisioning_artifacts(ProductId=self.avm_productid)
            for pa in pa_res['ProvisioningArtifactDetails']:
                if pa['Active']:
                    provision_artifact = pa['Id']
                    print("Provisioning Artifact ID:", pa['Id'])
            response = " "
            if(provision_artifact):
                Apex_Environment = "PROD" if event['Apex_Environment'] == "Production" else ("UAT" if event['Apex_Environment'] == "Acceptance"  else ("BCKP" if event['Apex_Environment'] == "Backup"  else("DEV" if event['Apex_Environment'] == "Development" else ("HA" if event['Apex_Environment'] == "Fall-back"  else ("DR" if event['Apex_Environment'] == "Disaster recovery" else ("TST" if event['Apex_Environment'] == "Test"  else "DFLT"))))))
                AccountName = event['AccountName'].replace(" ", "-")
                if 'Public' in event['Environment']:
                    print("Account getting onboarded is public...")
                    dynamic_account_name = 'AWS-'+Apex_Environment+'-PUB-'+event['ApexID'][-6:]+'-'+AccountName
                    print("Account name created is : {}".format(dynamic_account_name))
                    print ("checking if characterlimits crassing 40...")
                    if len(dynamic_account_name) > 40 :
                        print("found that account name is crossing 40 character limit hence trimming to take only 40")
                        dynamic_account_name = dynamic_account_name[:40]
                    else :
                        print("Found account name character limit is within 40 hence it will be using same....")
                
                elif 'Hybrid' in event['Environment']:
                    print("Account getting onboarded is Hybrid...")
                    dynamic_account_name = 'AWS-'+Apex_Environment+'-HYB-'+event['ApexID'][-6:]+'-'+AccountName
                    print("Account name created is : {}".format(dynamic_account_name))
                    print ("checking if characterlimits crassing 40...")
                    if len(dynamic_account_name) > 40 :
                        print("found that account name is crossing 40 character limit hence trimming to take only 40")
                        dynamic_account_name = dynamic_account_name[:40]
                    else :
                        print("Found account name character limit is within 40 hence it will be using same....")
                
                else:
                    print("Account getting onboarded is private...")
                    dynamic_account_name = 'AWS-'+Apex_Environment+'-PVT-'+event['ApexID'][-6:]+'-'+AccountName
                    print("Account name created is : {}".format(dynamic_account_name))
                    print ("checking if characterlimits crassing 40...")
                    if len(dynamic_account_name) > 40 :
                        print("found that account name is crossing 40 character limit hence trimming to take only 40")
                        dynamic_account_name = dynamic_account_name[:40]
                    else :
                        print("Found account name character limit is within 40 hence it will be using same....")
                
                dynamic_account_name = ''.join(i for i in dynamic_account_name if not i in bad_chars)
                print ("Resultant account name framed is : " + str(dynamic_account_name))
                print("I am here in last IF condition of Invoking provisoned products creation task ....")
                response = self.servicecatalogclient.provision_product(
                    ProductId=self.avm_productid,
                    ProvisioningArtifactId=provision_artifact,
                    ProvisionedProductName= dynamic_account_name,
                    ProvisioningParameters=[
                        {
                            "Key": "SoldToCode", ## Sold to code.
                            "Value": event['SoldToCode']
                        },
                        {
                            "Key": "NVirginia", ## Ip address size that needs to be created in North virginia
                            "Value": event['NVirginia']
                        },
                        {
                            "Key": "CustodianUserFirstName", ## custodian email
                            "Value": event['CustodianUserFirstName']
                        },
                        {
                            "Key": "UpdateIndex",
                            "Value": "1"
                        },
                        {
                            "Key": "RequestorEmail", ## open on behalf of this user
                            "Value": event['RequestorEmail']
                        },
                        {
                            "Key": "CustodianUser", ##  custodian email
                            "Value": event['CustodianUser']
                        },
                        {
                            "Key": "SupportDL", ## Application distrubution list
                            "Value": event['SupportDL']
                        },
                        {
                            "Key": "Ireland", ## Ip address size that needs to be created in North Ireland
                            "Value": event['Ireland']
                        },
                        {
                            "Key": "Singapore", ## Ip address size that needs to be created in Singapore
                            "Value": event['Singapore']
                        },                        
                        {
                            "Key": "AccountMigration", ##  No for MVP1 delivery
                            "Value": event['Migration']
                        },
                        {
                            "Key": "ApexID", ## Application deploy deployment ( data - Application Service ID -  only last six digits)
                            "Value": event['ApexID']
                        },
                        {
                            "Key": "Environment", ## Private-Production , Public-production or Hybrid-Account based on VPC data provided
                            "Value": event['Environment']
                        },
                        {
                            "Key": "CustodianUserLastName", ##  custodian email
                            "Value": event['CustodianUserLastName']
                        },
                        {
                            "Key": "Budget", ## Monthly consumptionbudget USD
                            "Value": event['Budget']
                        },
                        {
                            "Key": "LOB", ## Line of busines
                            "Value": event['LOB']
                        },
                        {
                            "Key": "RequestNo", ## Rquest number
                            "Value": event['RequestNo']
                        },
                        {
                            "Key": "AccountName", ## AWS-<Apex_Environment>-<PUB/PVT>-<Apex_ID last six digit>-<Apex_ID Name> , AWS account name 40 character limit.                          
                            "Value": dynamic_account_name ## Examples: AWS-PRD-PVT-114202-MFG-SAMPLEMANAGER-AM-PRD
                        },
                        {
                            "Key": "RootDL",
                            "Value": ""
                        },
                        {
                            "Key": "WorkloadType",
                            "Value": event['WorkLoadType']
                        },
                        {
                            "Key": "BusinessContributors", ## BusinessContributors Email IDs
                            "Value": event['BusinessContributors']
                        },   
                        {
                            "Key": "BusinessOperators", ## BusinessOperators Email IDs
                            "Value": event['BusinessOperators']
                        },  
                        {
                            "Key": "BusinessLimitedOperators", ## BusinessLimitedOperators Email IDs
                            "Value": event['BusinessLimitedOperators']
                        }, 
                        {
                            "Key": "BusinessReadOnly", ## BusinessReadOnly Email IDs
                            "Value": event['BusinessReadOnly']
                        },
                        {
                            "Key": "BusinessCustom", ## BusinessCustom Email IDs
                            "Value": event['BusinessCustom']
                        },
                        {
                            "Key": "SOXrelevant", ## SOX revelnce of Application CI
                            "Value": event['SOXrelevant']
                        },
                        {
                            "Key": "ActiveBIAid", ## Active BIA of Application CI
                            "Value": event['ActiveBIAid']
                        },
                        {
                            "Key": "DataClassification", ## Data Classification of Application CI
                            "Value": event['DataClassification']
                        },
                        {
                            "Key": "AccountTenancy", ## Account tenancy
                            "Value": event['AccountTenancy']
                        },
                        {
                            "Key": "IsIOTAccount", ## Is IOT Account
                            "Value": event['IsIOTAccount']
                        },
                        {
                            "Key": "IsRESPCAccount", ## Is RESPC Account
                            "Value": event['IsRESPCAccount']
                        },
                        {
                            "Key": "IsNonroutableSubnets", ## Is Non-Routable subnets
                            "Value": event['IsNonroutableSubnets']
                        },
                        {
                            "Key": "HybridRESPCAccountDomainJoinOUName", ## Hybrid RESPC Account Domain Join OU Name
                            "Value": event['HybridRESPCAccountDomainJoinOUName']
                        },
                        {
                            "Key": "IsDatabricksAccount", 
                            "Value": event['IsDatabricksAccount']
                        },
                        {
                            "Key": "DatabricksEnvironment",
                            "Value": event['DatabricksEnvironment']
                        },
                        {
                            "Key": "DatabricksVolumeRequired",
                            "Value": event['DatabricksVolumeRequired']
                        },
                        {
                            "Key": "DatabricksS3Region",
                            "Value": event['DatabricksS3Region']
                        },
                        {
                            "Key": "DatabricksProjectID",
                            "Value": event['DatabricksProjectID']
                        }
                        
                    ]  
                )
                print(response)
            else:
                print("Provisioning Artifact ID not found for request : {}, hence exits now".format(event['change_request_number']))
                exit()
        except Exception as exception:
            print("failed execute provision_product api for request :{}, , hence exits now ".format(str(exception)))
            self.send_failed_Snow_Resonse(event['RequestTaskNo'], dynamic_account_name)
        status = response['RecordDetail']['Status']
        if status == "FAILED" or status == "IN_PROGRESS_IN_ERROR" :
            self.send_failed_Snow_Resonse(event['RequestTaskNo'], dynamic_account_name)
        return response

    ## check status of provision product
    def check_status_provisionproduct(self, ppid):
        try:
            status = ""
            search_filter = "id:" + ppid
            search_response = self.servicecatalogclient.search_provisioned_products(Filters={"SearchQuery": [search_filter]})
            print(search_response)
            return search_response['ProvisionedProducts'][0]
        except Exception as exception:
            print("failed executing search_provisioned_products api and error is : {} ".format(exception))

    ## check status of AFPP provision product
    def check_status_afpp_provisionproduct(self, ppname):
        try:
            status = ""
            AFPPName = "AFPP-"+ppname
            search_filter = "name:" + AFPPName
            search_response = self.servicecatalogclient.search_provisioned_products(Filters={"SearchQuery": [search_filter]})
            print(search_response)
            return search_response['ProvisionedProducts'][0]
        except Exception as exception:
            print("failed executing search_provisioned_products api and error is : {} ".format(exception))

    ## check status of Network provision product in case of provate
    def check_status_network_provisionproduct(self, ppname):
        try:
            status = ""
            NetworkPPName = "Network-"+ppname
            search_filter = "name:" + NetworkPPName
            search_response = self.servicecatalogclient.search_provisioned_products(Filters={"SearchQuery": [search_filter]})
            print(search_response)
        except Exception as exception:
            print("failed executing search_provisioned_products api and error is : {} ".format(exception))
            return {"Status" : "NotYet"}
        if len(search_response['ProvisionedProducts']) == 0:
            return {"Status" : "NotYet"}
        else:
            return search_response['ProvisionedProducts'][0]


    ## Get Secrets from AWS secrete manager service name "IntegrationCreds"
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
            api_data = json.loads(self.get_secret())
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

    ## Get queue URL
    def getQueueURL(self):
        try:
            queue_url = self.sqs_client.get_queue_url(QueueName="platform_snow_response_box.fifo").get('QueueUrl')
            print("Queue URL is {}".format(queue_url))
            return queue_url
        except Exception as exception:
            print("Exception occured while getQueueURL of Response box{}".format(exception))

    ## Send response message to response queue box
    def recordAqueueMessage(self, event):
        try:
            print("Recording event data in log before sending to queue and content are -  : {}".format(event))
            queueurl = self.getQueueURL()
            print("Got queue URL {}".format(queueurl))
            response = self.sqs_client.send_message(QueueUrl=queueurl, MessageBody=json.dumps(event), MessageGroupId="Test")
            print("Send result: {}".format(response))
            return response
        except Exception as exception:
            print("Exception occured while sending message to Response box{}".format(exception))

def lambda_handler(event, context):
    createupdateaccount = UpdateChildAccount(event, context)
    try:
        if event['RequestType'] == "Update":
            print("request is identified as the update request...")
            if "IsUpdateComplete" in event and not event['IsUpdateComplete']:
                print("account update has been started currently checking for the status...")
                next_item = next(iter(item for item in event['ProvisionedProductList'] if item['IsUpdateGoing'] == True), None)
                if next_item:
                    print("found one account with status IsUpdateGoing true hence checking its current status..")
                    statuscheckoutput = createupdateaccount.check_status_provisionproduct(next_item['Id'])
                    if statuscheckoutput['Status'] in ["AVAILABLE","TAINTED","ERROR"]:
                        print("found account creation results as follows...")
                        print(statuscheckoutput)
                        next_item.update({"IsUpdateGoing": False})
                        next_item.update({"IsUpdated": True})
                        next_item.update({"StatusAfterUpdate": statuscheckoutput['Status']})
                        event.update({"IsUpdateComplete": True})
                        if statuscheckoutput['Status'] == "AVAILABLE" :
                            AccountNumberCreated = createupdateaccount.get_newlyprovisioned_accountnumber(statuscheckoutput['PhysicalId'])
                            next_item.update({"AccountNumber": AccountNumberCreated})
                        print("Update complete , invoking send results in form of queue message..")
                        queue_response = createupdateaccount.recordAqueueMessage(event)
                        if queue_response :
                            print ("Account update message is sent to response queue box")
                            createupdateaccount.CreateRecordInS3bucket(event)
                            print("Processed data stored in s3 bucket..")
                        return event
                    else:
                        print("Account update process is still in progress hence it is in waiting stage...!")
                        return event
            else:
                print("Below is event data when first update invoked")
                print(event)
                accounts_list = createupdateaccount.get_available_product()
                final_accountlist = createupdateaccount.get_available_product_info(accounts_list, event)
                if final_accountlist['ProvisionedProductList'][0] :
                    print("Found account number to be updated..so now it updates the provisioned product..")
                    invokeoutput = createupdateaccount.invoke_update_provision_product(event, final_accountlist['ProvisionedProductList'][0])
                    if invokeoutput :
                        print("Invoked provisioned product update.. waiting for it to get completed....")
                        final_accountlist['ProvisionedProductList'][0].update({"IsUpdateGoing": True})
                        return final_accountlist
                    else:
                        print("Error occured while invoking the update provisioned product..")
                else:
                    print("No matching account number found for the request.. please validate it..")

        elif event['RequestType'] == "Create":
            print("request is identified as the create request...")
            if "IsUpdateComplete" in event and not event['IsUpdateComplete']:
                print("account creation has been started currently checking for the status...")
                next_item = next(iter(item for item in event['ProvisionedProductList'] if item['IsUpdateGoing'] == True), None)
                if next_item:
                    print("found one account with status IsUpdateGoing true hence checking its current status..")
                    statuscheckoutput = createupdateaccount.check_status_provisionproduct(next_item['Id'])
                    afpp_statuscheckoutput = createupdateaccount.check_status_afpp_provisionproduct(next_item['Name'])
                    if event['RequestEventData']['Environment'] == "Private-Production" or event['RequestEventData']['Environment'] == "Hybrid-Account":
                        network_statuscheckoutput = createupdateaccount.check_status_network_provisionproduct(next_item['Name'])
                    else:
                        network_statuscheckoutput = {"Status": "AVAILABLE"}
                    if statuscheckoutput['Status'] in ["AVAILABLE","TAINTED","ERROR"] and afpp_statuscheckoutput['Status'] in ["AVAILABLE","TAINTED","ERROR"] and network_statuscheckoutput['Status'] in ["AVAILABLE","TAINTED","ERROR"]:
                        if statuscheckoutput['Status'] == "AVAILABLE" and afpp_statuscheckoutput['Status'] == "AVAILABLE" and network_statuscheckoutput['Status'] == "AVAILABLE":
                            print("found account creation results successfull.....")
                            print(statuscheckoutput)
                            next_item.update({"IsUpdateGoing": False})
                            next_item.update({"IsUpdated": True})
                            next_item.update({"StatusAfterUpdate": statuscheckoutput['Status']})
                            event.update({"IsUpdateComplete": True})
                            if statuscheckoutput['Status'] == "AVAILABLE" :
                                AccountNumberCreated = createupdateaccount.get_newlyprovisioned_accountnumber(statuscheckoutput['PhysicalId'])
                                next_item.update({"AccountNumber": AccountNumberCreated})
                            print("Creation complete , invoking send results in form of queue message..")
                            queue_response = createupdateaccount.recordAqueueMessage(event)
                            if queue_response :
                                print ("Account update message is sent to response queue box")
                                createupdateaccount.CreateRecordInS3bucket(event)
                                print("Processed data stored in s3 bucket..")
                            return event
                        else:
                            print("found account creation results found unsuccessfull or error hence closing task.....")
                            event.update({"IsUpdateComplete": True})
                            failresponse = createupdateaccount.send_failed_Snow_Resonse (event['RequestEventData']['RequestTaskNo'], next_item['Name'])
                            if failresponse :
                                print("sent failed response successfully..")
                            return event
                    else:
                        print("Account creation process is still in progress hence it is in waiting stage...!")
                        return event
            else:
                print("Below is event data when first create invoked")
                print(event)
                create_accounts_request = createupdateaccount.invoke_create_provision_product(event)
                if create_accounts_request:
                    print("account creation is successfull..")
                    product_list = {"RequestType" : "Create", "RequestEventData": event, "RequestNo" : event['RequestNo'], "IsUpdateComplete": False, "ProvisionedProductList":[]}
                    requireddatadict = {}
                    requireddatadict.update({ 
                                            "Name" : create_accounts_request['RecordDetail']['ProvisionedProductName'], 
                                            "Id": create_accounts_request['RecordDetail']['ProvisionedProductId'], 
                                            "ProductId": create_accounts_request['RecordDetail']['ProductId'], 
                                            "IsUpdated": False,
                                            "IsUpdateGoing": True,
                                            "StatusAfterUpdate": "",
                                            "AccountNumber" : ""
                                            })
                    product_list['ProvisionedProductList'].append(requireddatadict)
                    return product_list
                else:
                    print("Error occured while invoking the create new AVM provisioned product..")

        elif  event['RequestType'] == "Delete":
            print("Place holder for account delete request in future..")
        else:
            print("Request not belongs to 'Create', 'Update', 'Delete' request type...")
    except Exception as exception:
        print("Exception occured lambda handler and error is : {}".format(exception))
        return exception
