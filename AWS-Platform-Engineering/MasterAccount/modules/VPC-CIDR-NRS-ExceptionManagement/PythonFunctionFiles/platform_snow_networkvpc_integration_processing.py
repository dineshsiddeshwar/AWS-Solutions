# This lambda was updated as part of RARS Migration from 1.0 to 2.0
import boto3
import datetime
import json
import os
from botocore.exceptions import ClientError
import base64
import requests

class UpdateNetworkProduct(object):

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
            self.ses_client = SESSION.client('ses', region_name="us-east-1")
            SSM_client = SESSION.client('ssm', region_name="us-east-1")
            network_productid  = SSM_client.get_parameter(Name='platform_network_product_id')
            self.network_productid = network_productid['Parameter']['Value']
            snow_integration_log_bucket  = SSM_client.get_parameter(Name='SnowNerworkVPCIntegrationLogBucket')
            self.snow_integration_log_bucket = snow_integration_log_bucket['Parameter']['Value']
            AccountName = event['AccountName'].replace(" ", "-")
            self.network_product_name = 'Network'+'-'+AccountName
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
                            elif (parameters['ParameterKey'] == "NVirginia" or parameters['ParameterKey'] == "Ireland" or parameters['ParameterKey'] == "Singapore"):
                                keyvaluepairs.update( {parameters['ParameterKey']:parameters['ParameterValue']} )
                            elif (parameters['ParameterKey'] in event):
                                keyvaluepairs.update({ parameters['ParameterKey']: event[parameters['ParameterKey']]})
                            else:
                                keyvaluepairs.update({ parameters['ParameterKey']: parameters['ParameterValue']})
                        parameters_list.append(keyvaluepairs)
            return parameters_list
        except Exception as ex:
            print("Exception occured while running get_provisionedproduct_parameters and error is {}".format(ex)) 

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
            pp_list = []
            response = self.servicecatalogclient.search_provisioned_products(Filters={"SearchQuery":["productName:platform_network_request_product"]})
            result = response['ProvisionedProducts']
            while 'NextPageToken' in response:
                response = self.servicecatalogclient.search_provisioned_products(Filters={"SearchQuery":["productName:platform_network_request_product"]}, PageToken=response['NextPageToken'])
                result.extend(response['ProvisionedProducts'])
            if (result):
                for item in result:
                    if item['Status'] == 'AVAILABLE' and item['Name'] == self.network_product_name:
                        pp_list.append(item)
            print("Available network provisioned product", pp_list)
            return pp_list
        except Exception as ex:
            print("Exception occured while running search_provisioned_products and error is {}".format(ex))

    ## Create product info dictionary when it is account to be updated.
    def get_available_product_info(self, listofpp, event):
        try:
            product_list = {"RequestType" : "Update", "TaskType": event['TaskType'],"RequestEventData": event, "RequestNo" : event['RequestTaskNo'], "IsUpdateComplete": False, "ProvisionedProductList":[]}
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
                                            "AccountNumber" : event['AccountNumber']
                                            })
                    product_list['ProvisionedProductList'].append(requireddatadict)
                    break
            return product_list
        except Exception as ex:
            print("Exception occured while running get_available_product_info and error is {}".format(ex))

    ## Invoking provisoned products update task.
    def invoke_update_provision_product_cidr_extension(self, event, network):
        try:
            provision_artifact = " "
            pa_res = self.servicecatalogclient.list_provisioning_artifacts(ProductId=self.network_productid)
            for pa in pa_res['ProvisioningArtifactDetails']:
                if pa['Active']:
                    provision_artifact = pa['Id']
                    print("Provisioning Artifact ID:", pa['Id'])
            response = " "
            region_name = ""
            for key,value in event.items():
                if key == "NVirginia" and value != "No-VPC":
                    region_name = "NVirginia"
                    print("region",region_name)
                elif key == "Ireland" and value != "No-VPC":
                    region_name = "Ireland"
                    print("region",region_name)
                elif key == "Singapore" and value != "No-VPC":
                    region_name = "Singapore"
                    print("region",region_name)

            for key,value in network['ParametersList'][0].items():
                if key == "VPCID1" and value == "":
                    network['ParametersList'][0].update({"VPCID1": event["VPCId"], "IPSize1": event[region_name]})
                    break
                if key == "VPCID2" and value == "":
                    network['ParametersList'][0].update({"VPCID2": event["VPCId"], "IPSize2": event[region_name]})
                    break                
                if key == "VPCID3" and value == "":
                    network['ParametersList'][0].update({"VPCID3": event["VPCId"], "IPSize3": event[region_name]})
                    break
                if key == "VPCID4" and value == "":
                    network['ParametersList'][0].update({"VPCID4": event["VPCId"], "IPSize4": event[region_name]})
                    break
            print("Updated network provisoned parameter list", network['ParametersList'][0])
            if(provision_artifact):
                print("Network provisioned product name created is : {}".format(self.network_product_name))
                print("I am here in last IF condition of Invoking provisoned products creation task ....")
                response = self.servicecatalogclient.update_provisioned_product(
                    ProductId=network['ProductId'],
                    ProvisioningArtifactId=provision_artifact,
                    ProvisionedProductId= network['Id'],
                    ProvisioningParameters=[
                        {
                            "Key": "AccountNumber", ## Account number.
                            "Value": event['AccountNumber']
                        },
                        {
                            "Key": "Environment", ## Environment type
                            "Value": network['ParametersList'][0]['Environment']
                        },
                        {
                            "Key": "NVirginia",
                            "Value": network['ParametersList'][0]['NVirginia']
                        },
                        {
                            "Key": "UpdateIndex",
                            "Value": network['ParametersList'][0]['UpdateIndex']
                        },
                        {
                            "Key": "Ireland",
                            "Value": network['ParametersList'][0]['Ireland']
                        },
                        {
                            "Key": "Singapore",
                            "Value": network['ParametersList'][0]['Singapore']
                        },
                        {
                            "Key": "RequestNo",
                            "Value": network['ParametersList'][0]['RequestNo']
                        },
                        {
                            "Key": "IsNonroutableSubnets", ## Is IOT Account
                            "Value": network['ParametersList'][0]['IsNonroutableSubnets']
                        },
                        {
                            "Key": "VPCIDnonroutable", ## Is RESPC Account
                            "Value": network['ParametersList'][0]['VPCIDnonroutable']
                        },
                        {
                            "Key": "VPCID1", ## Is Non Routable Subnet
                            "Value": network['ParametersList'][0]['VPCID1']
                        },
                        {
                            "Key": "IPSize1", ## Hybrid RESPC Account Domain Join OU Name
                            "Value": network['ParametersList'][0]['IPSize1']
                        },
                        {
                            "Key": "VPCID2", ## Is Non Routable Subnet
                            "Value": network['ParametersList'][0]['VPCID2']
                        },
                        {
                            "Key": "IPSize2", ## Hybrid RESPC Account Domain Join OU Name
                            "Value": network['ParametersList'][0]['IPSize2']
                        },
                        {
                            "Key": "VPCID3", ## Is Non Routable Subnet
                            "Value": network['ParametersList'][0]['VPCID3']
                        },
                        {
                            "Key": "IPSize3", ## Hybrid RESPC Account Domain Join OU Name
                            "Value": network['ParametersList'][0]['IPSize3']
                        },
                        {
                            "Key": "VPCID4", ## Is Non Routable Subnet
                            "Value": network['ParametersList'][0]['VPCID4']
                        },
                        {
                            "Key": "IPSize4", ## Hybrid RESPC Account Domain Join OU Name
                            "Value": network['ParametersList'][0]['IPSize4']
                        }                       
                    ]  
                )
                print(response)
            else:
                print("Provisioning Artifact ID not found for account : {}".format(network['Name']))
                exit()
        except Exception as exception:
            print("Exception occured while running invoke_update_provision_product and error is {}".format(exception))
            self.send_failed_Snow_Resonse(event['RequestTaskNo'], event['AccountName'])
        status = response['RecordDetail']['Status']
        if status == "FAILED" or status == "IN_PROGRESS_IN_ERROR" :
            self.send_failed_Snow_Resonse(event['RequestTaskNo'], event['AccountName'])
        return response

    ## Invoking provisoned products creation task.
    def invoke_update_provision_product_non_routable(self, event,network):
        try:
            provision_artifact = " "
            pa_res = self.servicecatalogclient.list_provisioning_artifacts(ProductId=self.network_productid)
            for pa in pa_res['ProvisioningArtifactDetails']:
                if pa['Active']:
                    provision_artifact = pa['Id']
                    print("Provisioning Artifact ID:", pa['Id'])
            response = " "
            for key,value in network['ParametersList'][0].items():
                if key == "IsNonroutableSubnets":
                    network['ParametersList'][0].update({"IsNonroutableSubnets": "Yes"})

            print("Updated network provisoned parameter list", network['ParametersList'][0])
            
            if(provision_artifact):
                print("Network provisioned product name created is : {}".format(self.network_product_name))
                print("I am here in last IF condition of Invoking provisoned products creation task ....")
                response = self.servicecatalogclient.update_provisioned_product(
                    ProductId=network['ProductId'],
                    ProvisioningArtifactId=provision_artifact,
                    ProvisionedProductId= network['Id'],
                    ProvisioningParameters=[
                        {
                            "Key": "AccountNumber", ## Account number.
                            "Value": event['AccountNumber']
                        },
                        {
                            "Key": "Environment", ## Environment type
                            "Value": network['ParametersList'][0]['Environment']
                        },
                        {
                            "Key": "NVirginia",
                            "Value": network['ParametersList'][0]['NVirginia']
                        },
                        {
                            "Key": "UpdateIndex",
                            "Value": network['ParametersList'][0]['UpdateIndex']
                        },
                        {
                            "Key": "Ireland",
                            "Value": network['ParametersList'][0]['Ireland']
                        },
                        {
                            "Key": "Singapore",
                            "Value": network['ParametersList'][0]['Singapore']
                        },
                        {
                            "Key": "RequestNo",
                            "Value": network['ParametersList'][0]['RequestNo']
                        },
                        {
                            "Key": "IsNonroutableSubnets", ## Is IOT Account
                            "Value": network['ParametersList'][0]['IsNonroutableSubnets']
                        },
                        {
                            "Key": "VPCIDnonroutable", ## Is RESPC Account
                            "Value": network['ParametersList'][0]['VPCIDnonroutable']
                        },
                        {
                            "Key": "VPCID1", ## Is Non Routable Subnet
                            "Value": network['ParametersList'][0]['VPCID1']
                        },
                        {
                            "Key": "IPSize1", ## Hybrid RESPC Account Domain Join OU Name
                            "Value": network['ParametersList'][0]['IPSize1']
                        },
                        {
                            "Key": "VPCID2", ## Is Non Routable Subnet
                            "Value": network['ParametersList'][0]['VPCID2']
                        },
                        {
                            "Key": "IPSize2", ## Hybrid RESPC Account Domain Join OU Name
                            "Value": network['ParametersList'][0]['IPSize2']
                        },
                        {
                            "Key": "VPCID3", ## Is Non Routable Subnet
                            "Value": network['ParametersList'][0]['VPCID3']
                        },
                        {
                            "Key": "IPSize3", ## Hybrid RESPC Account Domain Join OU Name
                            "Value": network['ParametersList'][0]['IPSize3']
                        },
                        {
                            "Key": "VPCID4", ## Is Non Routable Subnet
                            "Value": network['ParametersList'][0]['VPCID4']
                        },
                        {
                            "Key": "IPSize4", ## Hybrid RESPC Account Domain Join OU Name
                            "Value": network['ParametersList'][0]['IPSize4']
                        }                       
                    ]  
                )
                print(response)
            else:
                print("Provisioning Artifact ID not found for account : {}".format(network['Name']))
                exit()
        except Exception as exception:
            print("Exception occured while running invoke_update_provision_product and error is {}".format(exception))
            self.send_failed_Snow_Resonse(event['RequestTaskNo'], event['AccountName'])
        status = response['RecordDetail']['Status']
        if status == "FAILED" or status == "IN_PROGRESS_IN_ERROR" :
            self.send_failed_Snow_Resonse(event['RequestTaskNo'], event['AccountName'])
        return response

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
           
    def send_failed_email_extension(self, event):
        try:
            print("Sending failed email now....")
            # The email body for recipients with non-HTML email clients.
            body_text = """
                Hello Team,
                
                AWS@Shell VPC CIDR Extension/Non-routable subnets request is falied, below are the details and results.          
                    * Account Number : """ + event['ProvisionedProductList'][0]['AccountNumber'] + """
                    * Account Name : """ + event['RequestEventData']['AccountName'] + """
                    * Task : """ + event['RequestEventData']['TaskType'] + """
                    * North Virginia : """ + event['RequestEventData']['NVirginia'] + """
                    * Ireland : """ + event['RequestEventData']['Ireland'] + """
                    * Singapore : """ + event['RequestEventData']['Singapore'] + """                    
                    * Environment : """ + event['RequestEventData']['VPCType'] + """
                    * Snow Request Task No : """ + event['RequestEventData']['RequestTaskNo'] + """
                    * Snow Request No : """ + event['RequestEventData']['RequestNo'] + """
                    * VPC Id : """ + event['RequestEventData']['VPCId'] + """

                Kindly check the account for more details and cloudwatch logs.
                
                Best Regards,
                Cloud Services Team
                """

            # The HTML body of the email.
            body_html = """<html>
                <head>
                <style>
                    table, td {
                    border: 1px solid black;
                    border-collapse: collapse;
                    }
                    
                    
                    th {
                    border: 1px solid black;
                    border-collapse: collapse;
                    font-weight: bold
                    }
                    
                    
                    td, th {
                    padding-left: 15px;
                    text-align: left;
                    }
                </style>
                </head>
                <body>
                <p style="font-family:'Futura Medium'">Hello Team,</p>
                <p style="font-family:'Futura Medium'">AWS@Shell VPC CIDR Extension/Non-routable subnets request is falied, below are the details and results.</p>
                
                <table style="width:100%">
                    <col style="width:50%">
                    <col style="width:50%">
                  <tr bgcolor="yellow">
                    <td width="50%">Account Property Names</td>
                    <td width="50%">Account Values</td>
                  </tr>
                  <tr>
                    <td width="50%">Account Number</td>
                    <td width="50%">""" + event['ProvisionedProductList'][0]['AccountNumber'] + """</td>
                  </tr>
                  <tr>
                    <td width="50%">Account Name</td>
                    <td width="50%">""" + event['RequestEventData']['AccountName'] + """</td>
                  </tr>
                  <tr>
                    <td width="50%">Task</td>
                    <td width="50%">""" + event['RequestEventData']['TaskType'] + """</td>
                  </tr>
                  <tr>
                    <td width="50%">North Virginia</td>
                    <td width="50%">""" + event['RequestEventData']['NVirginia'] + """</td>
                  </tr>
                  <tr>
                    <td width="50%">Ireland</td>
                    <td width="50%">""" + event['RequestEventData']['Ireland'] + """</td>
                  </tr>
                  <tr>
                    <td width="50%">Singapore</td>
                    <td width="50%">""" + event['RequestEventData']['Singapore'] + """</td>
                  </tr> 
                  <tr>
                    <td width="50%">Environment</td>
                    <td width="50%">""" + event['RequestEventData']['VPCType'] + """</td>
                  </tr>
                  <tr>
                    <td width="50%">Snow Request Task No</td>
                    <td width="50%">""" + event['RequestEventData']['RequestTaskNo'] + """</td>
                  </tr>
                  <tr>
                    <td width="50%">Snow Request No</td>
                    <td width="50%">""" + event['RequestEventData']['RequestNo'] + """</td>
                  </tr>
                  <tr>
                    <td width="50%">VPC Id</td>
                    <td width="50%">""" + event['RequestEventData']['VPCId'] + """</td>
                  </tr>
                </table>

                <p><b>Kindly check the account for more details and cloudwatch logs.</b></p>
                
                <p style="font-family:'Futura Medium'">Best Regards,</p>
                <p style="font-family:'Futura Medium'">Cloud Services Team</p>
                </body>
                </html>
                """
            # Provide the contents of the email.
            send_mail_response = self.ses_client.send_email(
                Source="SITI-CLOUD-SERVICES@shell.com",
                Destination={
                    'ToAddresses': ["GX-SITI-CPE-Team-Titan@shell.com"]
                },
                Message={
                    'Subject': {
                        'Data': "FAILED :"+event['RequestNo']+": AWS@Shell VPC CIDR Extension/ Non-routable Subnets request"

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

    def send_failed_email_non_routable(self, event):
        try:
            print("Sending failed email now....")
            # The email body for recipients with non-HTML email clients.
            body_text = """
                Hello Team,
                
                AWS@Shell VPC CIDR Extension/Non-routable subnets request is falied, below are the details and results.          
                    * Account Number : """ + event['ProvisionedProductList'][0]['AccountNumber'] + """
                    * Account Name : """ + event['RequestEventData']['AccountName'] + """
                    * Task : """ + event['RequestEventData']['TaskType'] + """                   
                    * Environment : """ + event['RequestEventData']['VPCType'] + """
                    * Snow Request Task No : """ + event['RequestEventData']['RequestTaskNo'] + """
                    * Snow Request No : """ + event['RequestEventData']['RequestNo'] + """
                    * VPC Id : """ + event['RequestEventData']['VPCId'] + """

                Kindly check the account for more details and cloudwatch logs.
                
                Best Regards,
                Cloud Services Team
                """

            # The HTML body of the email.
            body_html = """<html>
                <head>
                <style>
                    table, td {
                    border: 1px solid black;
                    border-collapse: collapse;
                    }
                    
                    
                    th {
                    border: 1px solid black;
                    border-collapse: collapse;
                    font-weight: bold
                    }
                    
                    
                    td, th {
                    padding-left: 15px;
                    text-align: left;
                    }
                </style>
                </head>
                <body>
                <p style="font-family:'Futura Medium'">Hello Team,</p>
                <p style="font-family:'Futura Medium'">AWS@Shell VPC CIDR Extension/Non-routable subnets request is falied, below are the details and results.</p>
                
                <table style="width:100%">
                    <col style="width:50%">
                    <col style="width:50%">
                  <tr bgcolor="yellow">
                    <td width="50%">Account Property Names</td>
                    <td width="50%">Account Values</td>
                  </tr>
                  <tr>
                    <td width="50%">Account Number</td>
                    <td width="50%">""" + event['ProvisionedProductList'][0]['AccountNumber'] + """</td>
                  </tr>
                  <tr>
                    <td width="50%">Account Name</td>
                    <td width="50%">""" + event['RequestEventData']['AccountName'] + """</td>
                  </tr>
                  <tr>
                    <td width="50%">Task</td>
                    <td width="50%">""" + event['RequestEventData']['TaskType'] + """</td>
                  </tr>
                  <tr>
                    <td width="50%">Environment</td>
                    <td width="50%">""" + event['RequestEventData']['VPCType'] + """</td>
                  </tr>
                  <tr>
                    <td width="50%">Snow Request Task No</td>
                    <td width="50%">""" + event['RequestEventData']['RequestTaskNo'] + """</td>
                  </tr>
                  <tr>
                    <td width="50%">Snow Request No</td>
                    <td width="50%">""" + event['RequestEventData']['RequestNo'] + """</td>
                  </tr>
                  <tr>
                    <td width="50%">VPC Id</td>
                    <td width="50%">""" + event['RequestEventData']['VPCId'] + """</td>
                  </tr>
                </table>

                <p><b>Kindly check the account for more details and cloudwatch logs.</b></p>
                
                <p style="font-family:'Futura Medium'">Best Regards,</p>
                <p style="font-family:'Futura Medium'">Cloud Services Team</p>
                </body>
                </html>
                """
            # Provide the contents of the email.
            send_mail_response = self.ses_client.send_email(
                Source="SITI-CLOUD-SERVICES@shell.com",
                Destination={
                    'ToAddresses': ["GX-SITI-CPE-Team-Titan@shell.com"]
                },
                Message={
                    'Subject': {
                        'Data': "FAILED :"+event['RequestNo']+": AWS@Shell VPC CIDR Extension/ Non-routable Subnets request"

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
               
    ## Get queue URL
    def getQueueURL(self):
        try:
            queue_url = self.sqs_client.get_queue_url(QueueName="platform_snow_networkvpc_response_box.fifo").get('QueueUrl')
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
    createupdatenetwork = UpdateNetworkProduct(event, context)
    try:
        if event['RequestType'] == "Update":  
            if event['TaskType'] == "VPC Extension":
                if "IsUpdateComplete" in event and not event['IsUpdateComplete']:
                    print("vpc extension has been started currently checking for the status...")
                    if event['RequestEventData']['VPCType'] == "Private" or event['RequestEventData']['VPCType'] == "Hybrid":
                        network_statuscheckoutput = createupdatenetwork.check_status_network_provisionproduct(event['RequestEventData']['AccountName'])
                    if  network_statuscheckoutput['Status'] in ["AVAILABLE","TAINTED","ERROR"]:
                        if network_statuscheckoutput['Status'] == "AVAILABLE":
                            print("found vpc operation results successfull.....")
                            print(network_statuscheckoutput)
                            event.update({"IsUpdateComplete": True,"StatusAfterUpdate": network_statuscheckoutput['Status']})
                            print("VPC Extension complete , invoking send results in form of queue message..")
                            queue_response = createupdatenetwork.recordAqueueMessage(event)
                            if queue_response :
                                print ("Network Provisioned product update message is sent to response queue box")
                                createupdatenetwork.CreateRecordInS3bucket(event)
                                print("Processed data stored in s3 bucket..")
                            return event
                        else:
                            print("found vpc operation results found unsuccessfull or error hence closing task.....")
                            event.update({"IsUpdateComplete": True})
                            failresponse = createupdatenetwork.send_failed_Snow_Resonse (event['RequestEventData']['RequestTaskNo'], event['RequestEventData']['AccountName'])
                            if failresponse :
                                print("sent failed response successfully..")
                            sendfailedemail = createupdatenetwork.send_failed_email_extension(event)
                            if sendfailedemail:
                                print("sent failed email successfully..")
                            return event
                    else:
                        print("VPC Extension process is still in progress hence it is in waiting stage...!")
                        return event
                else:
                    print("Below is event data when first create invoked")
                    print(event)
                    network_product = createupdatenetwork.get_available_product()
                    network_product_list = createupdatenetwork.get_available_product_info(network_product, event)
                                
                        
                    if network_product_list['ProvisionedProductList']!=[]:
                        print("Found network product to be updated..so now it updates the provisioned product..")
                        print("Network provisioned product parameters",network_product_list['ProvisionedProductList'][0])
                        invokeoutput = createupdatenetwork.invoke_update_provision_product_cidr_extension(event, network_product_list['ProvisionedProductList'][0])
                        if invokeoutput :
                            print("Invoked provisioned product update.. waiting for it to get completed....")
                            network_product_list['ProvisionedProductList'][0].update({"IsUpdateGoing": True})
                            return network_product_list
                        else:
                            print("Error occured while invoking the update provisioned product..")
                            failresponse = createupdatenetwork.send_failed_Snow_Resonse (event['RequestTaskNo'], event['AccountName'])
                            if failresponse :
                                print("sent failed response successfully..")
                    else:
                        print("No matching network product found for the request.. please validate it..")
                        failresponse = createupdatenetwork.send_failed_Snow_Resonse (event['RequestTaskNo'], event['AccountName'])
                        if failresponse :
                            print("sent failed response successfully..")

            elif event['TaskType'] == "Non-routable subnets for existing VPC":
                if "IsUpdateComplete" in event and not event['IsUpdateComplete']:
                    print("Non-routable subnets for existing VPC has been started currently checking for the status...")
                    if event['RequestEventData']['VPCType'] == "Private" or event['RequestEventData']['VPCType'] == "Hybrid":
                        network_statuscheckoutput = createupdatenetwork.check_status_network_provisionproduct(event['RequestEventData']['AccountName'])
                    if  network_statuscheckoutput['Status'] in ["AVAILABLE","TAINTED","ERROR"]:
                        if network_statuscheckoutput['Status'] == "AVAILABLE":
                            print("found vpc operation results successfull.....")
                            print(network_statuscheckoutput)
                            event.update({"IsUpdateComplete": True,"StatusAfterUpdate": network_statuscheckoutput['Status']})
                            print("Non-routable subnets for existing VPC complete , invoking send results in form of queue message..")
                            queue_response = createupdatenetwork.recordAqueueMessage(event)
                            if queue_response :
                                print ("Network Provisioned product update message is sent to response queue box")
                                createupdatenetwork.CreateRecordInS3bucket(event)
                                print("Processed data stored in s3 bucket..")
                            return event
                        else:
                            print("found vpc operation results found unsuccessfull or error hence closing task.....")
                            event.update({"IsUpdateComplete": True})
                            failresponse = createupdatenetwork.send_failed_Snow_Resonse (event['RequestEventData']['RequestTaskNo'], event['RequestEventData']['AccountName'])
                            if failresponse :
                                print("sent failed response successfully..")
                            sendfailedemail = createupdatenetwork.send_failed_email_non_routable(event)
                            if sendfailedemail:
                                print("sent failed email successfully..")
                            return event
                    else:
                        print("Non-routable subnets for existing VPC process is still in progress hence it is in waiting stage...!")
                        return event
                else:
                    print("Below is event data when first create invoked")
                    print(event)
                    network_product = createupdatenetwork.get_available_product()
                    network_product_list = createupdatenetwork.get_available_product_info(network_product, event)
                    print("Network provisioned product parameters",network_product_list['ProvisionedProductList'][0])
                    if network_product_list['ProvisionedProductList'][0] :
                        print("Found network product to be updated..so now it updates the provisioned product..")
                        invokeoutput = createupdatenetwork.invoke_update_provision_product_non_routable(event, network_product_list['ProvisionedProductList'][0])
                        if invokeoutput :
                            print("Invoked provisioned product update.. waiting for it to get completed....")
                            network_product_list['ProvisionedProductList'][0].update({"IsUpdateGoing": True})
                            return network_product_list
                        else:
                            print("Error occured while invoking the update provisioned product..")
                    else:
                        print("No matching network product found for the request.. please validate it..")

        

        elif  event['RequestType'] == "Delete":
            print("Place holder for vpc delete request in future..")
        elif  event['RequestType'] == "Create":
            print("Create is not required for VPC CIDR Extension/Non-routable subnet operations..")
        else:
            print("Request not belongs to 'Create', 'Update', 'Delete' request type...")
    except Exception as exception:
        print("Exception occured lambda handler and error is : {}".format(exception))
        return exception
