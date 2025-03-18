# This lambda was updated as part of RARS Migration from 1.0 to 2.0
import json
import boto3
import requests
import datetime
import time
import base64
import random
from botocore.exceptions import ClientError

class TFCWorkSpaces(object):

    def __init__(self, event, context):
        try:
            self.exception = []
            self.event = event
            self.context = context
            self.session_client = boto3.session.Session()
            self.secretManager_client = self.session_client.client('secretsmanager', region_name="us-east-1")
            self.ssm_client = self.session_client.client('ssm')
            avm_tfc_org = self.ssm_client.get_parameter(Name='tfcorganizations')
            self.avm_TFCOrg = avm_tfc_org['Parameter']['Value']
            print("AVM TFC ORG ", self.avm_TFCOrg)
            avm_tfc_org_project = self.ssm_client.get_parameter(Name='tfcorganizationsProject')
            self.avm_TFCOrg_Project = avm_tfc_org_project['Parameter']['Value']
            print("AVM TFC ORG Project ID ", self.avm_TFCOrg_Project)
            avm_tfc_org_project_name = self.ssm_client.get_parameter(Name='tfcorganizationsProjectName')
            self.avm_tfc_org_project_name = avm_tfc_org_project_name['Parameter']['Value']
            print("AVM TFC ORG Project Name ", self.avm_tfc_org_project_name)
            self.sts_master_client = self.session_client.client('sts')
            self.child_account_session_name = "ChildAccountSession-" + str(random.randint(1, 100000))
            self.child_account_role_arn = "arn:aws:iam::" + str(event['ProvisionedProduct']['AccountNumber']) + ":role/AWSControlTowerExecution"
            self.account_number = event['ProvisionedProduct']['AccountNumber']
            child_account_role_creds = self.sts_master_client.assume_role(RoleArn=self.child_account_role_arn,RoleSessionName=self.child_account_session_name)
            child_credentials = child_account_role_creds.get('Credentials')
            child_access_key_id = child_credentials.get('AccessKeyId')
            child_secret_access_key = child_credentials.get('SecretAccessKey')
            child_session_token = child_credentials.get('SessionToken')
            self.child_assume_role_session = boto3.Session(child_access_key_id, child_secret_access_key,child_session_token)
            self.iam_childaccount_client = self.child_assume_role_session.client('iam')
        except Exception as e:
            print(str(e))
    
    ## Check if IAM OIDC exist
    def check_IAMOIDCIdentityExists(self,OpenIDConnectProviderArn):
        try:   
            print("checking IAM OIDC Identity for TFC Exists dynamically...")
            responseCheckIAMOIDCIdentity = self.iam_childaccount_client.get_open_id_connect_provider(OpenIDConnectProviderArn=OpenIDConnectProviderArn)
            if responseCheckIAMOIDCIdentity['ResponseMetadata']['HTTPStatusCode'] == 200:
                print("retrived the response for check_IAMOIDCIdentityExists exists.")
                return True
            else:
                print("failed at getting required response from AWS get_open_id_connect_provider..") 
                return False        
        except Exception as e:
            print("Error occurred in check_IAMOIDCIdentityExists: ", str(e))
            return False
        
    ## Create IAM OIDC identity
    def create_IAMOIDCIdentity(self, url, ClientID):
        try:   
            print("Creating the TFC workspace IAM identity dynamically...")
            responseCreateIAMOIDCIdentity = self.iam_childaccount_client.create_open_id_connect_provider(
                                            Url=url, #'https://app.terraform.io'
                                            ClientIDList=[ClientID,], #'aws.workload.identity'
                                            ThumbprintList=['9e99a48a9960b14926bb7f3b02e22da2b0ab7280'],
                                            Tags=[
                                                {
                                                    'Key': 'platform_donotdelete',
                                                    'Value': 'yes'
                                                },
                                            ]
                                        )
            if responseCreateIAMOIDCIdentity['ResponseMetadata']['HTTPStatusCode'] == 200:
                print("retrived the response for IAM  role check_IAMOIDCIdentityExists exists.")
                return True
            else:
                print("failed at getting response from AWS create_open_id_connect_provider API..") 
                return False        
        except Exception as e:
            print("Error occurred in create_open_id_connect_provider: ", str(e))
            return False

    ## Delete IAM OIDC identity
    def delete_IAMOIDCIdentity(self,OpenIDConnectProviderArn):
        try:   
            print("Deleting TFC IAM identity dynamically...")
            self.iam_childaccount_client.delete_open_id_connect_provider(OpenIDConnectProviderArn=OpenIDConnectProviderArn)    
        except Exception as e:
            print("Error occurred in delete_open_id_connect_provider: ", str(e))
            return False
        return True

    ## Check if IAM Role exist
    def check_IAMRoleExists(self):
        try:   
            print("Checking the TFC workspace OIDC IAM role exists dynamically...")
            responseCheckIAMRoles = self.iam_childaccount_client.get_role( RoleName='platform_tfc_OIDC_role')
            if responseCheckIAMRoles['ResponseMetadata']['HTTPStatusCode'] == 200:
                print("retrived the response for IAM  role platform_tfc_OIDC_role exists.")
                return True
            else:
                print("failed at getting required secrets from AWS secret manager..") 
                return False        
        except Exception as e:
            print("Error occurred in check_IAMRoleExists: ", str(e))
            return False
    
    ## Create IAM Role exist
    def create_IAMRole(self, event):
        try:   
            FederatedString = "arn:aws:iam::"+str(event['ProvisionedProduct']['AccountNumber'])+":oidc-provider/app.terraform.io"
            TerraformWorkspaceAccess = "organization:"+self.avm_TFCOrg+":project:"+self.avm_tfc_org_project_name+":workspace:"+str(event['ProvisionedProduct']['AccountNumber'])+":run_phase:*"

            trustPolicy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                "Effect": "Allow",
                "Principal": {
                    "Federated": FederatedString
                },
                "Action": "sts:AssumeRoleWithWebIdentity",
                "Condition": {
                    "StringEquals": {
                        "app.terraform.io:aud": "aws.workload.identity"
                    },
                    "StringLike": {
                        "app.terraform.io:sub": TerraformWorkspaceAccess
                    }
                }
                }
            ]
            }

            responseCreateRole = self.iam_childaccount_client.create_role(RoleName="platform_tfc_OIDC_role",
                                                AssumeRolePolicyDocument=json.dumps(trustPolicy),
                                                Description='platform tfc OIDC role')

            print("Create role response: ", responseCreateRole)
            if responseCreateRole['Role']:
                print("Created IAM  role platform_tfc_OIDC_role.")
                return True
            else:
                print("failed create IAM  role platform_tfc_OIDC_role") 
                return False        
        except Exception as e:
            print("Error occurred in create_tfc_workspace: ", str(e))
            return False
    
    ## Delete IAM Role exist
    def delete_IAMRole(self):
        try:  
            print("Deleting IAM role from chid account") 
            self.iam_childaccount_client.delete_role(RoleName="platform_tfc_OIDC_role")
        except Exception as e:
            print("Error occurred in create_tfc_workspace: ", str(e))
            return False
        return True

    ## Check if IAM Policy exist
    def check_IAMPolicyExists(self, event):
        try:   
            print("checking TFC IAM role Policy Exists dynamically...")
            policyARN = "arn:aws:iam::"+str(event['ProvisionedProduct']['AccountNumber'])+":policy/platform_tfc_policy"
            responseCheckIAMpolicy = self.iam_childaccount_client.get_policy( PolicyArn=policyARN)
            if responseCheckIAMpolicy['ResponseMetadata']['HTTPStatusCode'] == 200:
                print("retrived the response for IAM  role platform_tfc_policy exists.")
                return True
            else:
                print("failed at getting required secrets from AWS secret manager..") 
                return False        
        except Exception as e:
            print("Error occurred in check_IAMPolicyExists: ", str(e))
            return False
        
    ## Create IAM Role policy
    def create_IAMPolicy(self):
        try:   
            print("Creating the TFC workspace dynamically...")
            PolicyDocument = {
                                "Version": "2012-10-17",
                                "Statement": [
                                    {
                                        "Effect": "Allow",
                                        "Action": "*",
                                        "Resource": "*"
                                    }
                                ]
                            }
            responseCreateIAMRolePolicy = self.iam_childaccount_client.create_policy(
                                        PolicyName='platform_tfc_policy',
                                        PolicyDocument=json.dumps(PolicyDocument),
                                        Description='platform tfc policy',
                                        Tags=[
                                            {
                                                'Key': 'platform_donotdelete',
                                                'Value': 'yes'
                                            },
                                        ]
                                    )
            if responseCreateIAMRolePolicy['Policy']:
                print("retrived the response for IAM  role platform_tfc_policy create.")
                return True
            else:
                print("failed at getting required response for IAM  role platform_tfc_policy create.") 
                return False        
        except Exception as e:
            print("Error occurred in create_tfc_workspace: ", str(e))
            return False

    ## Detach role policy
    def detach_RolePolicy(self, event):
        try:   
            print("Detaching role policy...")
            policyARN = "arn:aws:iam::"+str(event['ProvisionedProduct']['AccountNumber'])+":policy/platform_tfc_policy"
            self.iam_childaccount_client.detach_role_policy(RoleName="platform_tfc_OIDC_role", PolicyArn=policyARN)     
        except Exception as e:
            print("Error occurred in detach_RolePolicy: ", str(e))
            return False
        return True
    
    ## Delete IAM Policy
    def delete_IAMPolicy(self, event):
        try:   
            print("Deleting IAM role policy dynamically...")
            policyARN = "arn:aws:iam::"+str(event['ProvisionedProduct']['AccountNumber'])+":policy/platform_tfc_policy"
            self.iam_childaccount_client.delete_policy( RoleName=policyARN)
        except Exception as e:
            print("Error occurred in delete_IAMPolicy: ", str(e))
            return False
        return True
    
    ## Attach IAM role policy 
    def attach_role_policy_routine(self, event):
        print ("attach_role_policy_routine function has been started")
        child_role_policy_arn = "arn:aws:iam::"+str(event['ProvisionedProduct']['AccountNumber'])+":policy/platform_tfc_policy"
        retries = 0
        retry_policy_attach_status = 'False'      
        try:
            while retries < 4 and retry_policy_attach_status == 'False':
                response = self.iam_childaccount_client.attach_role_policy(RoleName="platform_tfc_OIDC_role", PolicyArn=child_role_policy_arn) 
                temp_res_code = response['ResponseMetadata']['HTTPStatusCode']
                if temp_res_code == 200:
                    retry_policy_attach_status = 'True'
                    print(" Policy %s has been attached successfully", str("platform_tfc_OIDC_role"))
                else:
                    time_to_sleep = 2 ** retries
                    retries += 1
                    time.sleep(time_to_sleep)   
            return True
        except Exception as exception_object:
            print(str(exception_object))
            print("Error occurred while retry Attach Role Policy %s", str(exception_object))
            return False

    ## Get Secrets from AWS secrete manager service name "TFCTOKEN"
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

    ## TFC create workspace
    def create_tfc_workspace(self,event):
        try:   
            print("Creating the TFC workspace dynamically...")
            tfc_data = json.loads(self.get_secret("AVMTFCTOKEN"))
            if tfc_data:
                print("retrived the tfc token from secret manager")
                url = 'https://app.terraform.io/api/v2/organizations/'+self.avm_TFCOrg+'/workspaces'
                headers = {'Authorization': 'Bearer '+tfc_data['TFC_TOKEN'],
                           'Content-Type': 'application/vnd.api+json'
                          }
                payload={
                    "data": {
                        "type": "workspaces",
                        "attributes": {
                        "name": event['ProvisionedProduct']['AccountNumber']
                        },
                        "relationships": {
                        "project": {
                            "data": {
                            "type": "projects",
                            "id": self.avm_TFCOrg_Project
                            }
                        }
                        }
                    }
                }
                TFCCreateresponse = requests.request("POST", url, headers=headers, data=json.dumps(payload))
                if  TFCCreateresponse.status_code == 201:
                    print("retrieved the response..")
                    print(TFCCreateresponse)
                    return json.loads(TFCCreateresponse.content)
                else:
                    print(TFCCreateresponse)
                    print("Did not get the required response") 
                    return False
            else:
                print("failed at getting required secrets from AWS secret manager..") 
                return False        
        except Exception as e:
            print("Error occurred in create_tfc_workspace: ", str(e))
            return False
        
    ## TFC Check workspace
    def check_tfc_workspace(self):
        try:   
            print("Checking the TFC workspace dynamically...")
            tfc_data = json.loads(self.get_secret("AVMTFCTOKEN"))
            if tfc_data:
                print("retrived the tfc token from secret manager")
                url = 'https://app.terraform.io/api/v2/organizations/'+self.avm_TFCOrg+'/workspaces/'+self.account_number
                headers = {'Authorization': 'Bearer '+tfc_data['TFC_TOKEN'],
                        'Content-Type': 'application/vnd.api+json'
                        }
                TFCCheckresponse = requests.request("GET", url, headers=headers)
                if  TFCCheckresponse.status_code == 200:
                    print("retrieved the response..")
                    print(TFCCheckresponse)
                    return json.loads(TFCCheckresponse.content)
                else:
                    print(TFCCheckresponse)
                    print("Did not get the required response") 
                    return False
            else:
                print("failed at getting required secrets from AWS secret manager..") 
                return False        
        except Exception as e:
            print("Error occurred in create_tfc_workspace: ", str(e))
            return False

    ## TFC update workspace 
    def update_tfc_workspace(self, event):
        try:
            print("Updating the TFC workspace dynamically...")
            tfc_data = json.loads(self.get_secret("AVMTFCTOKEN"))
            if tfc_data:
                print("retrived the tfc token from secret manager")
                url = 'https://app.terraform.io/api/v2/organizations/'+self.avm_TFCOrg+'/workspaces/'+event['ProvisionedProduct']['AccountNumber']
                headers = {'Authorization': 'Bearer '+tfc_data['TFC_TOKEN'],
                           'Content-Type': 'application/vnd.api+json'
                          }
                payload={
                    'data': {
                        'attributes': {
                            'name': event['ProvisionedProduct']['AccountNumber']
                        },
                        'type': 'workspaces'
                    },
                    "relationships": {
                        "project": {
                            "data": {
                                "type": "projects",
                                "id": self.avm_TFCOrg_Project
                            }
                        }
                   }
                }
                TFCUpdateresponse = requests.request("PATCH", url, headers=headers, data=json.dumps(payload))
                if  TFCUpdateresponse.status_code == 200:
                    print("Updated successfully..")
                    print(TFCUpdateresponse)
                    return True
                else:
                    print(TFCUpdateresponse)
                    print("Did not get the required response")
                    return False
            else:
                print("failed at getting required secrets from AWS secret manager..")  
                return False             
        except Exception as e:
            print("Error occurred in update_tfc_workspace: ", str(e))
            return False

    ## Validate if WorkSpace has required vars
    def validate_workspace_vars(self, data_list):
        try:
            print("In validate workspace vars...")
            if type(data_list) == list:
                i = 0
                for data in data_list:
                    if data['attributes']['key'] == "TFC_AWS_RUN_ROLE_ARN" or data['attributes']['key'] == "TFC_AWS_PROVIDER_AUTH" or data['attributes']['key'] == "TF_CLI_ARGS_plan" :
                        i +=1
                if i >= 3:
                    print ("required variables are set the on workspace")
                    return True
                else:
                    print ("required variables NOT are set the on workspace")
                    return False
            else:
                print("Data is not list hence retuns False")
                return False
        except Exception as e:
            print("Error occurred in create_tfc_workspace: ", str(e))
            return False   

    ## GET TFC WorkSpace Environmental variables
    def check_tfc_workspace_vars(self,Work_SpaceID):
        try:   
            print("Checking the TFC workspace vars dynamically...")
            tfc_data = json.loads(self.get_secret("AVMTFCTOKEN"))
            if tfc_data:
                print("retrived the tfc token from secret manager")
                url = 'https://app.terraform.io/api/v2/workspaces/'+Work_SpaceID+'/vars'
                headers = {'Authorization': 'Bearer '+tfc_data['TFC_TOKEN'],
                        'Content-Type': 'application/vnd.api+json'
                        }
                TFCGETVarsResponse = requests.request("GET", url, headers=headers)
                if  TFCGETVarsResponse.status_code == 200:
                    print("retrieved the response..")
                    print(TFCGETVarsResponse)
                    if self.validate_workspace_vars(json.loads(TFCGETVarsResponse.content)['data']):
                        return True
                    else:
                        return False
                else:
                    print(TFCGETVarsResponse)
                    print("Did not get the required response") 
                    return False
            else:
                print("failed at getting required secrets from AWS secret manager..") 
                return False        
        except Exception as e:
            print("Error occurred in create_tfc_workspace: ", str(e))
            return False
  
    ## TFC create workspace vars
    def create_tfc_workspace_vars(self, Work_SpaceID, Key , Value):
        try:   
            print("Creating the TFC workspace vars dynamically...")
            tfc_data = json.loads(self.get_secret("AVMTFCTOKEN"))
            if tfc_data:
                print("retrived the tfc token from secret manager")
                url = 'https://app.terraform.io/api/v2/workspaces/'+Work_SpaceID+'/vars'
                headers = {'Authorization': 'Bearer '+tfc_data['TFC_TOKEN'],
                           'Content-Type': 'application/vnd.api+json'
                          }
                payload={
                            "data": {
                                "type":"vars",
                                "attributes": {
                                "key": Key,
                                "value": Value,
                                "description":"TFC vars for AWSatShell",
                                "category":"env",
                                "hcl":False,
                                "sensitive":False
                                }
                            }
                        }
                TFCVarCreateresponse = requests.request("POST", url, headers=headers, data=json.dumps(payload))
                if  TFCVarCreateresponse.status_code == 201:
                    print("retrieved the response..")
                    print(TFCVarCreateresponse)
                    return True
                else:
                    print(TFCVarCreateresponse)
                    print("Did not get the required response") 
                    return False
            else:
                print("failed at getting required secrets from AWS secret manager..") 
                return False        
        except Exception as e:
            print("Error occurred in create_tfc_workspace_vars: ", str(e))
            return False

    ## TFC Delete workspace
    def delete_tfc_workspace(self,event):
        try:   
            print("Deleting the TFC workspace dynamically...")
            tfc_data = json.loads(self.get_secret("AVMTFCTOKEN"))
            if tfc_data:
                print("retrived the tfc token from secret manager")
                url = 'https://app.terraform.io/api/v2/organizations/'+self.avm_TFCOrg+'/workspaces/'+event['ProvisionedProduct']['AccountNumber']
                headers = {'Authorization': 'Bearer '+tfc_data['TFC_TOKEN'],
                        'Content-Type': 'application/vnd.api+json'
                        }
                TFCDeleteresponse = requests.request("DELETE", url, headers=headers)
                if  TFCDeleteresponse.status_code == 204:
                    print("retrieved the response..")
                    print(TFCDeleteresponse)
                    return True
                else:
                    print(TFCDeleteresponse)
                    print("Did not get the required response") 
                    return False
            else:
                print("failed at getting required secrets from AWS secret manager..") 
                return False        
        except Exception as e:
            print("Error occurred in create_tfc_workspace: ", str(e))
            return False
        
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

def lambda_handler(event, context):
    try:
        print("event data is: {}".format(json.dumps(event)))
        object_tfc = TFCWorkSpaces(event, context)
        failCheckFlag = 0
        if event['RequestType'] == 'Create':
            print ("Currently create account event..")
            TFIODCARN = "arn:aws:iam::"+event['ProvisionedProduct']['AccountNumber']+":oidc-provider/app.terraform.io"
            print(TFIODCARN)
            if object_tfc.create_IAMOIDCIdentity("https://app.terraform.io", "aws.workload.identity"):
                print("terraform IODC identity provider created successfully..")
                if object_tfc.create_IAMRole(event):
                    print("Terraform OIDC role created succesfully..!!")
                    if object_tfc.create_IAMPolicy():
                        print("IAM role policy created. attaching role policies now")
                        if object_tfc.attach_role_policy_routine(event):
                            print("role policy attachment succeeded..!")
                            print("creating TFC workspce now..")
                            WorkSpace_result = object_tfc.create_tfc_workspace(event)
                            if  WorkSpace_result:
                                print("TFC workspace created successfully..")
                                if object_tfc.check_tfc_workspace_vars(WorkSpace_result['data']['id']):
                                    print("TFC workspace vars exist..!!")
                                else:
                                    print("TFC workspace vars NOT exist..!!, hence creating now..")
                                    ROLEARN = "arn:aws:iam::"+event['ProvisionedProduct']['AccountNumber']+":role/platform_tfc_OIDC_role"
                                    if object_tfc.create_tfc_workspace_vars(WorkSpace_result['data']['id'],"TFC_AWS_RUN_ROLE_ARN",ROLEARN) and object_tfc.create_tfc_workspace_vars(WorkSpace_result['data']['id'],"TFC_AWS_PROVIDER_AUTH","true") and object_tfc.create_tfc_workspace_vars(WorkSpace_result['data']['id'],"TF_CLI_ARGS_plan","-var-file=parameters.json"):
                                        print("Required variables are set on the Worksapce for AWS IODC..")
                                    else:
                                        print("Setting TFC workspace vars failed..")
                                        object_tfc.send_failed_Snow_Resonse (event['RequestEventData']['RequestTaskNo'], event['ProvisionedProduct']['Name'])
                                        failCheckFlag +=1
                            else:
                                print("TFC workspace creation failed..")
                                object_tfc.send_failed_Snow_Resonse (event['RequestEventData']['RequestTaskNo'], event['ProvisionedProduct']['Name'])
                                failCheckFlag +=1
                        else:
                            print("role policy attachment failed..!")
                            object_tfc.send_failed_Snow_Resonse (event['RequestEventData']['RequestTaskNo'], event['ProvisionedProduct']['Name'])
                            failCheckFlag +=1
                    else:
                        print("IAM role policy creation failed.")
                        object_tfc.send_failed_Snow_Resonse (event['RequestEventData']['RequestTaskNo'], event['ProvisionedProduct']['Name'])
                        failCheckFlag +=1
                else:
                    print("terraform IODC role creation failed..")
                    object_tfc.send_failed_Snow_Resonse (event['RequestEventData']['RequestTaskNo'], event['ProvisionedProduct']['Name'])
                    failCheckFlag +=1
            else: 
                print("terraform IODC identity provider created failed..")
                object_tfc.send_failed_Snow_Resonse (event['RequestEventData']['RequestTaskNo'], event['ProvisionedProduct']['Name'])
                failCheckFlag +=1
        elif event['RequestType'] == 'Update':
            print ("Currently update account event..")
            TFIODCARN = "arn:aws:iam::"+event['ProvisionedProduct']['AccountNumber']+":oidc-provider/app.terraform.io"
            print(TFIODCARN)
            if object_tfc.check_IAMOIDCIdentityExists(TFIODCARN):
                print("Terraform IODC identity already exist..")
            else:
                print("Terraform IODC identity provider does not exist hence creating now")
                if object_tfc.create_IAMOIDCIdentity("https://app.terraform.io", "aws.workload.identity"):
                    print("terraform IODC identity provider created successfully..")
                else: 
                    print("terraform IODC identity provider created failed..")
                    object_tfc.send_failed_Snow_Resonse (event['RequestEventData']['RequestTaskNo'], event['ProvisionedProduct']['Name'])
                    failCheckFlag +=1
            
            if object_tfc.check_IAMRoleExists():
                print("Terraform IODC role already exist..")
            else:
                print("Terraform IODC role does not exist hence creating now")
                if object_tfc.create_IAMRole(event):
                    print("terraform IODC role created successfully..")
                else: 
                    print("terraform IODC role creation failed..")
                    object_tfc.send_failed_Snow_Resonse (event['RequestEventData']['RequestTaskNo'], event['ProvisionedProduct']['Name'])
                    failCheckFlag +=1
            
            if object_tfc.check_IAMPolicyExists(event):
                print("Terraform IODC role  policy already exist..")
            else:
                print("Terraform IODC role policy does not exist hence creating now")
                if object_tfc.create_IAMPolicy():
                    print("terraform IODC role policy created successfully..")
                    if object_tfc.attach_role_policy_routine(event):
                        print("role policy attachment succeeded..!")
                    else:
                        print("terraform IODC role policy attachment failed..")
                        object_tfc.send_failed_Snow_Resonse (event['RequestEventData']['RequestTaskNo'], event['ProvisionedProduct']['Name'])
                        failCheckFlag +=1
                else: 
                    print("terraform IODC role policy creation failed..")
                    object_tfc.send_failed_Snow_Resonse (event['RequestEventData']['RequestTaskNo'], event['ProvisionedProduct']['Name'])
                    failCheckFlag +=1
            
            tfc_workspace_id = ""
            tfc_check_workspace_result = object_tfc.check_tfc_workspace()
            if tfc_check_workspace_result:
                print("Terraform workspace already exist..")
                tfc_workspace_id = tfc_check_workspace_result['data']['id']
            else:
                print("Terraform workspace does not exist hence creating now")
                tfc_create_workspace_result = object_tfc.create_tfc_workspace(event)
                if tfc_create_workspace_result:
                    tfc_workspace_id = tfc_check_workspace_result['data']['id']
                    print("Terraform workspace created successfully..")
                else: 
                    print("Terraform workspace creation failed..")
                    object_tfc.send_failed_Snow_Resonse (event['RequestEventData']['RequestTaskNo'], event['ProvisionedProduct']['Name'])
                    failCheckFlag +=1
                
            if object_tfc.check_tfc_workspace_vars(tfc_workspace_id):
                print("Terraform workspace vars already exist..")
            else:
                print("TFC workspace vars NOT exist..!!, hence creating now..")
                ROLEARN = "arn:aws:iam::"+event['ProvisionedProduct']['AccountNumber']+":role/platform_tfc_OIDC_role"
                if object_tfc.create_tfc_workspace_vars(WorkSpace_result['data'][id],"TFC_AWS_RUN_ROLE_ARN",ROLEARN) and object_tfc.create_tfc_workspace_vars(WorkSpace_result['data'][id],"TFC_AWS_PROVIDER_AUTH","true") and object_tfc.create_tfc_workspace_vars(WorkSpace_result['data'][id],"TF_CLI_ARGS_plan","-var-file=parameters.json"):
                    print("Required variables are set on the Worksapce for AWS IODC..")
                else:
                    print("Setting TFC workspace vars failed..")
                    object_tfc.send_failed_Snow_Resonse (event['RequestEventData']['RequestTaskNo'], event['ProvisionedProduct']['Name'])
                    failCheckFlag +=1
        elif event['RequestType'] == 'Delete':  
            print ("Currently delete account event..")
            TFIODCARN = "arn:aws:iam::"+event['ProvisionedProduct']['AccountNumber']+":oidc-provider/app.terraform.io"
            print(TFIODCARN)
            if object_tfc.delete_IAMOIDCIdentity(TFIODCARN):
                print ("Terraform IODC identity deleted successfully..")

            if object_tfc.detach_RolePolicy(event):
               print ("Detach Role Policy successfully..")

            if object_tfc.delete_IAMRole():
                print ("Terraform IODC role deleted successfully..")

            if object_tfc.delete_IAMPolicy(event):
               print ("Terraform IODC role  policy deleted successfully..")

            if object_tfc.delete_tfc_workspace():
                print ("Terraform workspace deleted successfully..")
        else:
            print ("NA event..")
        if failCheckFlag == 0:
            event['IsTFCWorkspaceComplete'] = True
        else:
            event['IsTFCWorkspaceComplete'] = False
        return event
    except Exception as exception:
        print("exception happend in TFCWorkSpaces lambda: ", exception)
        event['IsTFCWorkspaceComplete'] = False
        return event