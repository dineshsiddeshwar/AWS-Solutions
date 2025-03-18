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
            self.ou_client = boto3.client('organizations')
            SSM_client = SESSION.client('ssm', region_name="us-east-1")
            snow_integration_log_bucket  = SSM_client.get_parameter(Name='SnowIntegrationLogBucket')
            self.snow_integration_log_bucket = snow_integration_log_bucket['Parameter']['Value']
            print("snow integration log bcuket is :", self.snow_integration_log_bucket)
            AFproductid  = SSM_client.get_parameter(Name='AFproductid')
            self.af_productid = AFproductid['Parameter']['Value']
            print("AF ProductId is :", self.af_productid)
            dlTableName  = SSM_client.get_parameter(Name='dlTableName')
            self.dl_table_name = dlTableName['Parameter']['Value']
            print("DL Table name :", self.dl_table_name)
            successOperationDL = SSM_client.get_parameter(Name='success_operation_dl')
            self.success_operation_dl = successOperationDL['Parameter']['Value']
            print("Successful Operation DL :", self.success_operation_dl)
            senderId = SSM_client.get_parameter(Name='sender_id')
            self.sender_id = senderId['Parameter']['Value']
            print("Sender Email ID is :", self.sender_id)
            adminAccount = SSM_client.get_parameter(Name='admin_account')
            self.admin_account = adminAccount['Parameter']['Value']
            print("Admin account is :", self.admin_account)
            self.dd_client = SESSION.client('dynamodb', region_name="us-east-1")
            self.ses_client = SESSION.client('ses', region_name="us-east-1")
            self.request_type = self.event['RequestType']
            print ("request type is", self.request_type)
            self.s3_client = boto3.client('s3')
            self.ManagedOrganizationalUnit = ""
        except Exception as exception:
            self.reason_data = "Missing required property %s" % exception
    
    ## Update DL table
    def update_request_details(self, account_number,account_name,dl_for_new_account, status):
        try:
            print("inside updateDLDetails")
            if status:
                item_list = {
                    'AccountNumber': {"S": account_number},
                    'AccountName': {"S": account_name},
                    'DLEmailId': {"S": dl_for_new_account},
                    'CreationDate': {"S": datetime.datetime.now().strftime('%d-%m-%Y')},
                    'IsUsed': {"BOOL": True},
                    'InProgress': {"BOOL": False}
                }
            else:
                item_list = {
                    'AccountNumber': {"S": ""},
                    'AccountName': {"S": ""},
                    'DLEmailId': {"S": dl_for_new_account},
                    'CreationDate': {"S": ""},
                    'IsUsed': {"BOOL": False},
                    'InProgress': {"BOOL": False}
                }

            if self.request_type == 'Update':
                print("Inside update dl flag")
                item_list.update(
                    {'UpdationDate': {"S": str(datetime.datetime.now().strftime('%d-%m-%Y'))}})
                print("UPDATE ITEM>>", item_list)

            elif self.request_type == 'Delete':
                print("Inside Delete dl flag")
                item_list.update(
                    {'DeletionDate': {"S": str(datetime.datetime.now().strftime('%d-%m-%Y'))}})
                print("Delete ITEM>>", item_list)

            else:
                print("It is a Create dl flag")
                print("Create ITEM>>", item_list)
            self.dd_client.put_item(
                TableName=self.dl_table_name,
                Item=item_list
            )
            return True
        except Exception as exception:
            print("DynamoDB DL update failed with exception : ", exception)
            return False

    ## Fetch DL name
    def fetch_dl_name(self):
        print("inside fetchDLName")
        try:
            scan_response = self.dd_client.scan(TableName=self.dl_table_name)
            items_list = scan_response.get('Items')
            if self.verify_dl_usage(items_list) < 1:
                print("No free DLs left to create new Dedicated Account. Hence exiting!!!")
                return False
            dl_mail_id = ""
            dl_fetched = False
            for item_list in items_list:
                is_used = (item_list.get('IsUsed')).get('BOOL')
                in_progress = (item_list.get('InProgress')).get('BOOL')
                dl_mail_id = (item_list.get('DLEmailId')).get('S')
                if is_used is False and in_progress is False:
                    self.dl_for_new_account = dl_mail_id
                    print("{} to be used for creation of new child account!".format(dl_mail_id))
                    print("Putting lock on the DL to avoid usage by other accounts")
                    item_list["InProgress"] = True
                    self.dd_client.update_item(
                            TableName=self.dl_table_name,
                            Key={'DLEmailId': {'S' : self.dl_for_new_account}},
                            UpdateExpression="SET InProgress=:b",
                            ExpressionAttributeValues={
                                 ':b': {"BOOL": True}},
                            ReturnValues="ALL_NEW")
                    print(f"InProgress set to True for DL {dl_mail_id}")
                    print(f"DL fetched {dl_fetched}")
                    break
            return self.dl_for_new_account
        except Exception as exception:
            print("Exception occured while retrieving DL for onboarding and error is: ",exception)
            return False
    
    ## Verify DL Usage
    def verify_dl_usage(self, items_list):
        print("inside verifyDLUsage")
        count = 0
        try:
            for item_list in items_list:
                is_used = (item_list.get('IsUsed')).get('BOOL')
                in_progress = (item_list.get('InProgress')).get('BOOL')

                if is_used is False and in_progress is False:
                    count += 1
            if count < 10:
                print("Only {} unused DLs left. Please add more DLs to the Table for creating new Dedicated Accounts!!!".format(count))
                self.send_fetch_dl_email()
            print("DL Count is", count)
            return count
        except Exception as exception:
            print("ERROR verifyDLUsage", exception)
            return False
        
    ## Send DL emails
    def send_fetch_dl_email(self):
        try:
            # This address must be verified with Amazon SES.
            sender_id = self.sender_id

            # The email body for recipients with non-HTML email clients.
            body_text = """Important Action Required\r\n AWS@Shell –  Free DL’s are less than 10.\r\n What’s happening?\r\n You are receiving this notification because the AWS@Shell “DL_Details” table has less the 10 available DL’s for Account Creation. \r\nWhat is expected from you?\r\n
Please get the DLs for Dedicated Accounts Project created in the format “GXITSOCloudServices-AWS-Shell-[Sequence Number]” and add the DLs to the “DL_Details” table in Master Account with “AccountID" """ + str(
                self.admin_account) +""" for creating new Dedicated Accounts.\r\nBest Regards,\r\n
Cloud Services Team
"""

            # The HTML body of the email.
            body_html = """
             <html>
                                <head></head>
                                <body>
                                <p style="color:red;font-family:'Futura Medium'"><b>Important: Action Required</b></p>
								<p style="color:#1F497D;font-family:'Futura Medium'"><b>AWS@Shell –  Free DL’s are less than 10.</b></p>
								<p style="color:red;font-family:'Futura Medium'">What’s happening?</p>
                                <p style="font-family:'Futura Medium'">You are receiving this notification because the AWS@Shell “DL_Details” has less the 10 available DL’s for Account Creation.</p>
								<p style="color:red;font-family:'Futura Medium'">What is expected from you?</p>
								<p style="font-family:'Futura Medium'">
								   Please get the DLs for AWS@Shell service created in the format “GXITSOCloudServices-AWS-Shell-[Sequence Number]” and add the DLs to the “DL_Details” table in Master Account with AccountID \"""" + str(
                self.admin_account) + """\" for creating new AWS@Shell Accounts.
								</p>
                                <p style="font-family:'Futura Medium'">Best Regards,</p>
                                <p style="font-family:'Futura Medium'">Cloud Services Team</p>
                                </body>
                                </html>
                             """

            # Provide the contents of the email.
            send_mail_response = self.ses_client.send_email(
                Source=sender_id,
                Destination={
                    'ToAddresses': [self.success_operation_dl]
                },
                Message={
                    'Subject': {
                        'Data': 'Action Required: AWS@Shell Free DL’s are less than 10 '

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
        except Exception as e:
            print("Send email for DL scarcity and exception is: ",str(e))

    ## Invoking provisoned products update task.
    def invoke_update_provision_product(self, event):
        try:
            print("Inside update Provision Product")
            provision_artifact = " "
            self.ou_item = self.return_ou_id(event['ProvisionedProduct']['OU'])
            pa_res = self.servicecatalogclient.list_provisioning_artifacts(ProductId=self.af_productid)
            for pa in pa_res['ProvisioningArtifactDetails']:
                if pa['Active']:
                    provision_artifact = pa['Id']
                    print("Product Artifact ID:", pa['Id'])
            response = " "
            if provision_artifact:
                print("I am here in last IF condition of Invoking update provisoned products update task....")
                response = self.servicecatalogclient.update_provisioned_product(
                    ProvisionedProductId=event['ProvisionedProduct']['Id'],
                    ProductId=self.af_productid,
                    ProvisioningArtifactId=provision_artifact,
                    ProvisioningParameters=[
                        {
                            "Key": "AccountName",
                            "Value": event['ProvisionedProduct']['Name']
                        },
                        {
                            "Key": "AccountEmail",
                            "Value": event['ProvisionedProduct']['AccountDL']
                        },
                        {
                            "Key": "SSOUserFirstName",
                            "Value": event['RequestEventData']['CustodianUserFirstName']
                        },
                        {
                            "Key": "SSOUserLastName",
                            "Value": event['RequestEventData']['CustodianUserLastName']
                        },
                        {
                            "Key": "SSOUserEmail",
                            "Value": event['RequestEventData']['CustodianUser']
                        },
                        {
                            "Key": "ManagedOrganizationalUnit",
                            "Value": event['ProvisionedProduct']['OU']+" ("+self.ou_item[0]['Id']+")"
                        }
                    ]
                )
                print(response)
            else:
                print("Provisioning Artifact ID not found for account : {}".format(event['accountname']))
                return False
        except Exception as exception:
            print("Exception occured while running invoke_update_provision_product and error is {}".format(exception))
            return False
        status = response['RecordDetail']['Status']
        if status == "FAILED" or status == "IN_PROGRESS_IN_ERROR" :
            return False
        return response

    ## Invoking provisoned products Delete task.
    def invoke_delete_provision_product(self, event):
        try:
            print("In decomission provision Account Factory provision product..")
            response = self.servicecatalogclient.terminate_provisioned_product(
                ProvisionedProductId=event['ProvisionedProduct']['Id']
            )
            print(response)
        except Exception as exception:
            print("Exception occured while running invoke_delete_provision_product and error is {}".format(exception))
            return False
        return response

    def get_list_ous_for_parent (self, id):
        try:
            results =  []
            response = self.ou_client.list_organizational_units_for_parent(ParentId=id)
            if response['ResponseMetadata']['HTTPStatusCode'] ==  200:
                results = response['OrganizationalUnits']
                while 'NextToken' in response:
                        response = self.ou_client.list_organizational_units_for_parent(
                                    ParentId=id,
                                    NextToken= response['NextToken']
                                )
                        results.extend(response['OrganizationalUnits'])
            return results
        except Exception as exception:
            return False

    def return_ou_id (self, ou):
        try:
            FinalResult = []
            i = 0
            while i < 6 :
                if i == 0:
                    RootLayerResult = self.get_list_ous_for_parent(self.ou_client.list_roots()['Roots'][0]['Id'])
                    if RootLayerResult:
                        FinalResult.extend(RootLayerResult) 
                        i+=1
                    else:
                        break
                else:
                    LayerResult = []
                    for item in RootLayerResult:
                        Result = self.get_list_ous_for_parent(item['Id'])
                        if Result:
                            LayerResult.extend(Result)
                            FinalResult.extend(Result)
                        else:
                            continue
                    RootLayerResult = LayerResult
                    i+=1
            return [ item for item in FinalResult if item['Name'] == ou ]
        except Exception as exception:
            return False
    ## Invoking provisoned products creation task.
    def invoke_create_provision_product(self, event):
        try:
            provision_artifact = " "
            # initializing bad_chars_list
            bad_chars = [";", ":", "!", "*", "@", "#", "$", "%", "^", "&", "(", ")", "[", "]", "{", "}", "?", "/", ".", "_"]
            provision_artifact = " "
            pa_res = self.servicecatalogclient.list_provisioning_artifacts(
                ProductId=self.af_productid
            )
            for pa in pa_res['ProvisioningArtifactDetails']:
                if pa['Active'] == True:
                    provision_artifact = pa['Id']
                    print(pa['Id'])
            response = " "
            if provision_artifact:
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
                    print("Creating OU where the account has to sit")
                    if Apex_Environment == 'PROD':
                        self.ManagedOrganizationalUnit = 'Prod-Public-'+event['WorkLoadType'].upper()
                        print("OU identified is :  ", self.ManagedOrganizationalUnit)
                    else:
                        self.ManagedOrganizationalUnit = 'NON-Prod-Public-'+event['WorkLoadType'].upper()
                        print("OU identified is : ", self.ManagedOrganizationalUnit)
                
                elif 'Hybrid' in event['Environment']:
                    print("Account getting onboarded is Hybrid...")
                    dynamic_account_name = 'AWS-'+Apex_Environment+'-HYB-'+event['ApexID'][-6:]+'-'+AccountName
                    print("Account name created is : ".format(dynamic_account_name))
                    print ("checking if characterlimits crassing 40...")
                    if len(dynamic_account_name) > 40 :
                        print("found that account name is crossing 40 character limit hence trimming to take only 40")
                        dynamic_account_name = dynamic_account_name[:40]
                    else :
                        print("Found account name character limit is within 40 hence it will be using same....")
                    if Apex_Environment == 'PROD':
                        self.ManagedOrganizationalUnit = 'Prod-Hybrid-'+event['WorkLoadType'].upper()
                        print("OU identified is :  ", self.ManagedOrganizationalUnit)
                    else:
                        self.ManagedOrganizationalUnit = 'NON-Prod-Hybrid-'+event['WorkLoadType'].upper()
                        print("OU identified is : ", self.ManagedOrganizationalUnit)
                
                elif 'Private' in event['Environment']:
                    print("Account getting onboarded is private...")
                    dynamic_account_name = 'AWS-'+Apex_Environment+'-PVT-'+event['ApexID'][-6:]+'-'+AccountName
                    print("Account name created is : {}".format(dynamic_account_name))
                    print ("checking if characterlimits crassing 40...")
                    if len(dynamic_account_name) > 40 :
                        print("found that account name is crossing 40 character limit hence trimming to take only 40")
                        dynamic_account_name = dynamic_account_name[:40]
                    else :
                        print("Found account name character limit is within 40 hence it will be using same....")
                    if Apex_Environment == 'PROD':
                        self.ManagedOrganizationalUnit = 'Prod-Private-'+event['WorkLoadType'].upper()
                        print("OU identified is : ", self.ManagedOrganizationalUnit)
                    else:
                        self.ManagedOrganizationalUnit = 'NON-Prod-Private-'+event['WorkLoadType'].upper()
                        print("OU identified is : ", self.ManagedOrganizationalUnit)
                else: 
                    print("Account environment is not found...hence udatin snow task")
                    return False
                dynamic_account_name = ''.join(i for i in dynamic_account_name if not i in bad_chars)
                self.account_name = dynamic_account_name
                print ("Resultant account name framed is : " + str(dynamic_account_name))
                print("I am here in last IF condition of Invoking provisoned products creation task ....")
                self.ou_item = self.return_ou_id(self.ManagedOrganizationalUnit)
                response = self.servicecatalogclient.provision_product(
                    ProductId=self.af_productid,
                    ProvisioningArtifactId=provision_artifact,
                    ProvisionedProductName="AFPP-" + dynamic_account_name,
                    ProvisioningParameters=[
                        {
                            "Key": "AccountName",
                            "Value": dynamic_account_name
                        },
                        {
                            "Key": "AccountEmail",
                            "Value": self.dl_for_new_account
                        },
                        {
                            "Key": "SSOUserFirstName",
                            "Value": event['CustodianUserFirstName']
                        },
                        {
                            "Key": "SSOUserLastName",
                            "Value": event['CustodianUserLastName']
                        },
                        {
                            "Key": "SSOUserEmail",
                            "Value": event['CustodianUser']
                        },
                        {
                            "Key": "ManagedOrganizationalUnit",
                            "Value": self.ManagedOrganizationalUnit+" ("+self.ou_item[0]['Id']+")"
                        }
                    ]
                )
                print(response)
            else:
                print("Provisioning Artifact ID not found for request : {}, hence exits now".format(event['change_request_number']))
                return '',"NA"
        except Exception as exception:
            print("failed execute provision_product api for request :{}, , hence exits now ".format(str(exception)))
            return '', "NA"
        status = response['RecordDetail']['Status']
        if status == "FAILED" or status == "IN_PROGRESS_IN_ERROR" :
            return'', "NA"
        return response, self.ManagedOrganizationalUnit

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

    ## Upload in Integration S3 bucket
    def Upload_in_S3bucket(self, accountparams):
        print("All account data {}".format(accountparams))
        try:
            print("Inside function to create the dynamic .json file...")
            dynamicfilename = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
            print("filename format created is {}".format(dynamicfilename))
            s3_file_name = accountparams['ProvisionedProduct']['AccountNumber']+"/" + dynamicfilename + "/parameters.json"
            print("s3 bucket path in bucket platform-snow-integration-logs-dev/uat/prod would be  {}".format(s3_file_name))
            local_file_path = "/tmp/UpdateAccount.json"
            print("file path:{}".format(local_file_path))
            with open(local_file_path, 'w') as fp:
                json.dump(accountparams, fp)
            print("all account data is stored in local json file")
            self.s3_client.upload_file(local_file_path, self.snow_integration_log_bucket, s3_file_name)
            print("file uploaded successfully..")
            os.remove(local_file_path)
            print("File deleted after upload to s3 bucket")
        except Exception as exception:
            print("Exception in Lambda Handler and error is {}".format(exception))
            return False
        return True

    ## Download a file from a Integration S3 bucket.
    def download_from_S3bucket(self, event):
        s3_client = boto3.client('s3')
        try:
            S3ObjectName = event['AccountNumber'].strip()+"/parameters.json"
            PathToDownload = "/tmp/"+event['AccountNumber'].strip()+".json"
            print("object to download from s3 bucket {} is {}".format(self.snow_integration_log_bucket, S3ObjectName))
            s3_client.download_file(self.snow_integration_log_bucket, S3ObjectName, PathToDownload)
            fileOpen = open(PathToDownload)
            AccountParametersdata = json.load(fileOpen)
            fileOpen.close()
            print("Parameters data are read", AccountParametersdata)
        except Exception as exception:
            print("failed at download_from_S3bucket and error is :{} ".format(str(exception)))
            return False
        return AccountParametersdata

    ## Updates paramter.json meta data 
    def Update_Parameters(self, event , accountparams):
        print("Aaccount parameters.json data {}".format(accountparams))
        print("Aaccount udpate request data {}".format(event))
        try:
            print("Inside function to Update Parameters data...")
            accountparams['RequestType'] = "Update"
            accountparams['IsSupportTagComplete'] = False
            accountparams['IsTFCWorkspaceComplete'] = False
            accountparams['IsParametersFileComplete'] = False
            for key, value in event.items():
                if key not in ['AccountNumber','AccountName'] and value != "NA":
                    accountparams['RequestEventData'][key] = value
        except Exception as exception:
            print("Exception in Lambda Handler and error is {}".format(exception))
            return False
        return accountparams
    
    ## Updates paramter.json VPC data 
    def Update_VPC_Parameters(self, event , accountparams):
        print("Aaccount parameters.json data {}".format(accountparams))
        print("Aaccount udpate request data {}".format(event))
        try:
            print("Inside function to Update Parameters data with current VPC update request data...")
            accountparams['RequestType'] = "Update"
            accountparams['IsSupportTagComplete'] = False
            accountparams['IsTFCWorkspaceComplete'] = False
            accountparams['IsParametersFileComplete'] = False
            accountparams['CurrentVPCUpdateRequest'] = event
        except Exception as exception:
            print("Exception in Lambda Handler and error is {}".format(exception))
            return False
        return accountparams

def lambda_handler(event, context):
    createupdateaccount = UpdateChildAccount(event, context)
    try:
        if event['RequestType'] == "Update":
            print("request is identified as the update request...")
            if 'TaskType' not in event :
                print("Its metadata update request...")
                if "IsProcessingComplete" in event and not event['IsProcessingComplete']:
                    print("account update has been started currently checking for the status...")
                    next_item = event['ProvisionedProduct']
                    if next_item:
                        print("found one account with status where Update is Going true hence checking its current status..")
                        statuscheckoutput = createupdateaccount.check_status_provisionproduct(next_item['Id'])
                        if statuscheckoutput['Status'] in ["AVAILABLE","TAINTED","ERROR"]:
                            print("found account creation results as follows...")
                            print(statuscheckoutput)
                            next_item.update({"IsCreateGoing": False})
                            next_item.update({"IsCreated": True})
                            next_item.update({"StatusAfterCreate": statuscheckoutput['Status']})
                            event.update({"IsProcessingComplete": True})
                            if statuscheckoutput['Status'] == "AVAILABLE" :
                                print("Update completed with AVAILABLE status..")
                            else:
                                print("Update completed with ERROR or TAINTED status.")
                            return event
                        else:
                            print("Account update process is still in progress hence it is in waiting stage...!")
                            return event
                else:
                    print("Below is event data when first update invoked")
                    print(event)
                    DownloadOutput = createupdateaccount.download_from_S3bucket(event)
                    if DownloadOutput:
                        print("Download succeeded , now updating parameters as update request")
                        Parameters = createupdateaccount.Update_Parameters(event, DownloadOutput)
                        if Parameters:
                            invokeoutput = createupdateaccount.invoke_update_provision_product(Parameters)
                            if invokeoutput :
                                print("Invoked provisioned product update.. waiting for it to get completed....")
                                Parameters['ProvisionedProduct'].update({"IsCreateGoing": True})
                                Parameters.update({"IsProcessingComplete": False})
                                return Parameters
                            else:
                                print("Error occured while invoking the update provisioned product..")
                                Parameters['ProvisionedProduct'].update({"IsCreateGoing": False})
                                Parameters['ProvisionedProduct'].update({"IsCreated": False})
                                Parameters['ProvisionedProduct'].update({"StatusAfterCreate": 'ERROR'})
                                Parameters.update({"IsProcessingComplete": False})
                                print("Account update failed, hence changing the snow task status..")
                                createupdateaccount.send_failed_Snow_Resonse (Parameters['RequestEventData']['RequestTaskNo'], Parameters['ProvisionedProduct']['Name'])
                                return Parameters
                        else:
                            print("Error occured while doing invoking Update_Parameters..")
                            event['ProvisionedProduct'].update({"IsCreateGoing": False})
                            event['ProvisionedProduct'].update({"IsCreated": False})
                            event['ProvisionedProduct'].update({"StatusAfterCreate": 'ERROR'})
                            event.update({"IsProcessingComplete": False})
                            print("Account update failed, hence changing the snow task status..")
                            createupdateaccount.send_failed_Snow_Resonse (event['RequestTaskNo'], event['AccountName'])
                            return event
                    else:
                        print("Error occured while doing invoking download_from_S3bucket..")
                        event['ProvisionedProduct'].update({"IsCreateGoing": False})
                        event['ProvisionedProduct'].update({"IsCreated": False})
                        event['ProvisionedProduct'].update({"StatusAfterCreate": 'ERROR'})
                        event.update({"IsProcessingComplete": True})
                        print("Account update failed, hence changing the snow task status..")
                        createupdateaccount.send_failed_Snow_Resonse (event['RequestTaskNo'], event['AccountName'])
                        return event
            elif 'TaskType' in event : 
                print("Its VPC Update request...")
                print("Below is event data when first update invoked")
                print(event)
                DownloadOutput = createupdateaccount.download_from_S3bucket(event)
                if DownloadOutput:
                    print("Download succeeded , now updating parameters as update request")
                    Parameters = createupdateaccount.Update_VPC_Parameters(event, DownloadOutput)
                    if Parameters:
                        print("Udated VPC update request data in parameters object")
                        Parameters['ProvisionedProduct'].update({"IsCreateGoing": False})
                        Parameters['ProvisionedProduct'].update({"IsCreated": True})
                        Parameters['ProvisionedProduct'].update({"StatusAfterCreate": 'AVAILABLE'})
                        Parameters.update({"IsProcessingComplete": True})
                        return Parameters
                    else:
                        print("Error occured while doing invoking Update_VPC_Parameters..")
                        event['ProvisionedProduct'].update({"IsCreateGoing": False})
                        event['ProvisionedProduct'].update({"IsCreated": False})
                        event['ProvisionedProduct'].update({"StatusAfterCreate": 'ERROR'})
                        event.update({"IsProcessingComplete": False})
                        print("Account update failed, hence changing the snow task status..")
                        createupdateaccount.send_failed_Snow_Resonse (event['RequestTaskNo'], event['AccountName'])
                        return event
                else:
                    print("Error occured while doing invoking download_from_S3bucket..")
                    event['ProvisionedProduct'].update({"IsCreateGoing": False})
                    event['ProvisionedProduct'].update({"IsCreated": False})
                    event['ProvisionedProduct'].update({"StatusAfterCreate": 'ERROR'})
                    event.update({"IsProcessingComplete": False})
                    print("Account update failed, hence changing the snow task status..")
                    createupdateaccount.send_failed_Snow_Resonse (event['RequestTaskNo'], event['AccountName'])
                    return event
            else:
                print("Its Not supported update request...")
        elif event['RequestType'] == "Create":
            print("request is identified as the create request...")
            if "IsProcessingComplete" in event and not event['IsProcessingComplete']:
                print("account creation has been started currently checking for the status...")
                next_item = event['ProvisionedProduct']
                if next_item:
                    print("found one account with status IsCreateGoing true hence checking its current status..")
                    statuscheckoutput = createupdateaccount.check_status_provisionproduct(next_item['Id'])
                    if statuscheckoutput['Status'] in ["AVAILABLE","TAINTED","ERROR"]:
                        if statuscheckoutput['Status'] == "AVAILABLE":
                            print("found account creation results successfull.....")
                            print(statuscheckoutput)
                            next_item.update({"IsCreateGoing": False})
                            next_item.update({"IsCreated": True})
                            next_item.update({"StatusAfterCreate": statuscheckoutput['Status']})
                            event.update({"IsProcessingComplete": True})
                            if statuscheckoutput['Status'] == "AVAILABLE" :
                                AccountNumberCreated = statuscheckoutput['PhysicalId']
                                next_item.update({"AccountNumber": AccountNumberCreated})
                                if createupdateaccount.update_request_details(AccountNumberCreated,next_item['Name'],next_item['AccountDL'], True):
                                    print("DL table is updated successfully..")
                                else:
                                    print("DL table update failled..!!!")
                            return event
                        else:
                            print("Account creation results found unsuccessfull or error hence closing task.....")
                            print(statuscheckoutput)
                            next_item.update({"IsCreateGoing": False})
                            next_item.update({"IsCreated": False})
                            next_item.update({"StatusAfterCreate": statuscheckoutput['Status']})
                            event.update({"IsProcessingComplete": True})
                            print("Account creation failed hence Updating Snow task..")
                            if createupdateaccount.update_request_details("","", next_item['AccountDL'],False):
                                print("DL table is updated successfully..")
                            else:
                                print("DL table update failled..!!!")
                            createupdateaccount.send_failed_Snow_Resonse (event['RequestEventData']['RequestTaskNo'], next_item['Name'])
                            return event
                    else:
                        print("Account creation process is still in progress hence it is in waiting stage...!")
                        return event
                else:
                    print("Error occured while checking the status of the AFPP..")
                    exit()
            else:
                print("Below is event data when first create invoked")
                print(event)
                accountDL = createupdateaccount.fetch_dl_name()
                if accountDL:
                    print("DL is fetched from DL_Details tables..", accountDL)
                    create_accounts_request,OU = createupdateaccount.invoke_create_provision_product(event)
                    if create_accounts_request['RecordDetail']['Status'] not in ["FAILED", "IN_PROGRESS_IN_ERROR"]:
                        print("account creation is successfull..")
                        product_list = {"RequestType" : "Create", "RequestEventData": event, "RequestNo" : event['RequestNo'], "IsProcessingComplete": False}
                        requireddatadict = {}
                        requireddatadict.update({ 
                                                "Name" : create_accounts_request['RecordDetail']['ProvisionedProductName'], 
                                                "Id": create_accounts_request['RecordDetail']['ProvisionedProductId'], 
                                                "ProductId": create_accounts_request['RecordDetail']['ProductId'], 
                                                "IsCreated": False,
                                                "IsCreateGoing": True,
                                                "StatusAfterCreate": "",
                                                "AccountNumber" : "",
                                                "AccountDL": accountDL,
                                                "OU" : OU
                                                })
                        product_list['ProvisionedProduct'] = requireddatadict
                        return product_list
                    else:
                        print("Error occured while invoking the create new AFPP..")
                        product_list = {"RequestType" : "Create", "RequestEventData": event, "RequestNo" : event['RequestNo'], "IsProcessingComplete": True}
                        requireddatadict = {}
                        requireddatadict.update({ 
                                                "Name" : "NotCreated", 
                                                "Id": "NotCreated", 
                                                "ProductId": "NotCreated", 
                                                "IsCreated": False,
                                                "IsCreateGoing": False,
                                                "StatusAfterCreate": "CreateAccount-FAILED",
                                                "AccountNumber" : "NA",
                                                "AccountDL": "NA",
                                                "OU" : OU
                                                })
                        product_list['ProvisionedProduct'] = requireddatadict
                        print("Account creation failed, hence sending snow response")
                        if createupdateaccount.update_request_details("","","",accountDL ,False):
                            print("DL table is updated successfully..")
                        else:
                            print("DL table update failled..!!!")
                        createupdateaccount.send_failed_Snow_Resonse(event['RequestTaskNo'], "AFPP-Failed")
                        return product_list
                else:
                    print("Fetch required DL is failed hence tasks also fails..!!")
                    product_list = {"RequestType" : "Create", "RequestEventData": event, "RequestNo" : event['RequestNo'], "IsProcessingComplete": True}
                    requireddatadict = {}
                    requireddatadict.update({ 
                                            "Name" : "NotCreated", 
                                            "Id": "NotCreated", 
                                            "ProductId": "NotCreated", 
                                            "IsCreated": False,
                                            "IsCreateGoing": False,
                                            "StatusAfterCreate": "FetchDL-FAILED",
                                            "AccountNumber" : "NA",
                                            "AccountDL": "NA",
                                            "OU" : "NA"
                                            })
                    product_list['ProvisionedProduct'] = requireddatadict
                    print("Account creation failed, hence sending snow response")
                    createupdateaccount.send_failed_Snow_Resonse(event['RequestTaskNo'], "AFPP-Failed-Fetch-DL")
                    return product_list
        elif event['RequestType'] == "Delete":
            print("Account delete request is being processed....")
            if createupdateaccount.invoke_delete_provision_product(event):
                print("Provision product delete is succeeded..")
                event.update({"IsProcessingComplete": True})
                event['ProvisionedProduct'].update({"StatusAfterCreate": 'COMPLETED'})
                return event
            else: 
                print("Provision product delete is Failed..!!")
                event.update({"IsProcessingComplete": True})
                event['ProvisionedProduct'].update({"StatusAfterCreate": 'ERROR'})
                createupdateaccount.send_failed_Snow_Resonse (event['RequestEventData']['RequestTaskNo'], event['ProvisionedProduct']['Name'])
                return event
        else:
            print("Request not belongs to 'Create', 'Update', 'Delete' request type...")
    except Exception as exception:
        print("Exception occured lambda handler and error is : {}".format(exception))
        return exception