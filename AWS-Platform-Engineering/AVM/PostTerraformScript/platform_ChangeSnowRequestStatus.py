# This lambda was updated as part of RARS Migration from 1.0 to 2.0
import boto3
import json
import datetime
import base64
import requests
import sys
from botocore.exceptions import ClientError

class SendResponseOfRequests():

    def __init__(self, event, context):
        self.exception = []
        self.event = event
        self.context = context
        session_client = boto3.session.Session()
        self.secretManager_client = session_client.client('secretsmanager', region_name="us-east-1")

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

    def send_Snow_Resonse (self, event):
        try:
            if event['ProvisionedProduct']['StatusAfterCreate'] == "AVAILABLE":
                statecode = "3"
                close_notes = "Account request is processed with success status.."
            else:
                statecode = "-5"
                close_notes = "Account request is processed with failed status.."
            api_data = json.loads(self.get_secret())
            if api_data :
                print("retrieved AWS secret manager data..")
                Bearer_token_data = self.get_SIMAAS_BearerToken(api_data['SIMAAS_URL'], api_data['SIMAAS_client_id'], api_data['SIMAAS_client_secret'],api_data['SIMAAS_username'],api_data['SIMAAS_password'])
                if Bearer_token_data :
                    print("SIMAAS bearer toaken is retrieved ...")
                    dynamicnowdata = datetime.datetime.now().strftime("%Y-%m-%d %I:%M:%S")
                    print("dynamic now date is framed..")
                    payload = json.dumps({
                            "u_supplier_reference": event['RequestEventData']['RequestTaskNo'] if event['RequestType'] == "Create" else event['CurrentVPCUpdateRequest']['RequestTaskNo'],
                            "ice4u_target_id": event['RequestEventData']['RequestTaskNo'] if event['RequestType'] == "Create" else event['CurrentVPCUpdateRequest']['RequestTaskNo'],
                            "u_work_notes": "Work Note - Payload processing completed..",
                            "u_close_notes": close_notes,
                            "u_state": statecode,
                            "u_short_description": event['ProvisionedProductList'][0]['AccountNumber'],
                            "u_description": event['ProvisionedProductList'][0]['Name'],
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

try:
    local_file_path = str(sys.argv[1])+"parameters.json"
    print("Parameters local file path: ", local_file_path)
    with open(local_file_path) as json_data:
        parameters_data = json.load(json_data)
    print(parameters_data)
    if parameters_data :
        TagAMI = SendResponseOfRequests(parameters_data)
        print("object is created for class SendResponseOfRequests..")
        ResponseToSnow = TagAMI.send_Snow_Resonse(parameters_data)
        if ResponseToSnow :
            print("response is sent back to snow and now sending eamil...")
        else:
            print("failed to send response to snow...")
except Exception as ex:
    print("There is an error sending Snow Response %s", str(ex))