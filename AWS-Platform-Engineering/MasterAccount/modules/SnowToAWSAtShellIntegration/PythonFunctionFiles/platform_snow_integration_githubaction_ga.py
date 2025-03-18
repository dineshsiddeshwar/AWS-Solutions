# This lambda was updated as part of RARS Migration from 1.0 to 2.0
import json
import boto3
import requests
import datetime
import time
import base64
from botocore.exceptions import ClientError

class Invoke_AVM_GitHubAction(object):

    def __init__(self, event, context):
        self.exception = []
        self.event = event
        self.context = context
        self.session_client = boto3.session.Session()
        self.ssm_client = self.session_client.client('ssm')
        self.secretManager_client = self.session_client.client('secretsmanager', region_name="us-east-1")
        avm_workflowName = self.ssm_client.get_parameter(Name='avm_workflowName')
        self.avm_workflowName = avm_workflowName['Parameter']['Value']
        avm_repoName = self.ssm_client.get_parameter(Name='avm_repoName')
        self.avm_repoName = avm_repoName['Parameter']['Value']
        avm_githubOwner = self.ssm_client.get_parameter(Name='avm_githubOwner')
        self.avm_githubOwner = avm_githubOwner['Parameter']['Value']
        self.env_type = self.ssm_client.get_parameter(Name='platform_Env_type')['Parameter']['Value']
        print("Env type ", self.env_type )
    
    ## Get Secrets from AWS secrete manager service name "GitHubPATTOKEN"
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

    ## Invoke Github Action
    def invoke_github_action(self,event):
        try:   
            print("Invoking GitHub Actions dynamically...")
            github_action_data = json.loads(self.get_secret("GitHubPATTOKEN"))
            if github_action_data:
                url = "https://api.github.com/repos/"+self.avm_githubOwner+"/"+self.avm_repoName+"/dispatches"
                headers = {
                    "Accept": "application/vnd.github+json",
                    "Authorization": "token "+github_action_data['PAT_TOKEN'],
                    "X-GitHub-Api-Version": "2022-11-28"
                }
                branch_name = "develop" if self.env_type == "dev" else ("release" if self.env_type == "uat" else ("master" if self.env_type == "prod" else "NA"))
                customevent = {
                    "EnvType" : self.env_type,
                    "branchName" : branch_name,
                    "accountNumber" : event['ProvisionedProduct']['AccountNumber'],
                    "admin_account" : event['SSMParameters']['admin_account'],
                    "ConnectivityType" : "Private" if "Private" in event['ProvisionedProduct']['OU'] or "Hybrid" in event['ProvisionedProduct']['OU'] else "Public"
                }
                
                print("custom event ", customevent)

                data = {
                    "event_type": "AWS@Shell-Platform-AVM-"+event['RequestType']+"-"+event['ProvisionedProduct']['AccountNumber'],
                    "client_payload": customevent
                }

                ResponseValue=requests.post(url,json=data,headers=headers)
                print(ResponseValue)
                if  ResponseValue.status_code == 204:
                    print("retrieved the response..")
                    print(ResponseValue)
                    return True
                else:
                    print(ResponseValue)
                    print("Did not get the required response") 
                    return False  
            else:
                print("failed at getting required secrets from AWS secret manager..")  
                return False      
        except Exception as e:
            print("Error occurred in invoke_github_action: ", str(e))
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
        object_github = Invoke_AVM_GitHubAction(event, context)
        if object_github.invoke_github_action(event):
            print("GitHub Action invoked successfully..")
        else:
            print("GitHub Action invoked failed..!!")
            object_github.send_failed_Snow_Resonse (event['RequestEventData']['RequestTaskNo'], event['ProvisionedProduct']['Name'])
    except Exception as exception:
        print("exception happend in Invoke_AVM_GitHubAction lambda: ", exception)
    return event