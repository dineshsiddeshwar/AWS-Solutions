import os
import logging
import boto3
import csv
import datetime
import json
from datetime import datetime

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication


LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
LOGGER.addHandler(CH)

SUCCESS = "SUCCESS"

SESSION = boto3.Session()
STS_CLIENT = SESSION.client('sts')
servicecatalogclient = SESSION.client('servicecatalog')
cloudformationclient = SESSION.client('cloudformation')
simpleemailserviceclient = SESSION.client('ses')

class UpdateChildAccount(object):

    ## init function
    def __init__(self, event, context):
        self.event = event
        self.context = context
        self.s3_client = boto3.client('s3')
        SSM_client = SESSION.client('ssm', region_name="us-east-1")
        account_update_bucket  = SSM_client.get_parameter(Name='AccountUpdateBucket')
        self.account_update_bucket = account_update_bucket['Parameter']['Value']
        LOGGER.info("Event: %s" % self.event)
        LOGGER.info("Context: %s" % self.context)

    ## Get provisioned product parameters from stack
    def get_provisionedproduct_parameters(self, stackid):
        try:
            parameters_list = []
            stacksdata =  cloudformationclient.describe_stacks(StackName=stackid)
            if (stacksdata['Stacks']) :
                for eachstack in stacksdata['Stacks']:
                    eachstackparameters = eachstack['Parameters']
                    if(eachstackparameters):
                        keyvaluepairs = {}
                        for parameters in eachstackparameters:
                            if(parameters['ParameterKey'] == "UpdateIndex"):
                                keyvaluepairs.update({ parameters['ParameterKey']: str(int(parameters['ParameterValue']) + 1)})
                            else:
                                keyvaluepairs.update({ parameters['ParameterKey']: parameters['ParameterValue']})
                        parameters_list.append(keyvaluepairs)
            for parameter in parameters_list:
                if "RootDL" not in parameter:
                    parameter.update({ "RootDL": ""})
                if "WorkloadType" not in parameter:
                    parameter.update({ "WorkloadType": "Non-BC"})
                if "AccountMigration" not in parameter:
                    parameter.update({ "AccountMigration": "No"})
                if "SOXrelevant" not in parameter:
                    parameter.update({ "SOXrelevant": "NA"})
                if "ActiveBIAid" not in parameter:
                    parameter.update({ "ActiveBIAid": "NA"})
                if "DataClassification" not in parameter:
                    parameter.update({ "DataClassification": "Unrestricted"})
                if "AccountTenancy" not in parameter:
                    parameter.update({ "AccountTenancy": "Single-Tenancy"})
                if "IsIOTAccount" not in parameter:
                    parameter.update({ "IsIOTAccount": "No"})
                if "IsRESPCAccount" not in parameter:
                    parameter.update({ "IsRESPCAccount": "No"})
                if "IsNonroutableSubnets" not in parameter:
                    parameter.update({ "IsNonroutableSubnets": "No"})
                if "HybridRESPCAccountDomainJoinOUName" not in parameter:
                    parameter.update({ "HybridRESPCAccountDomainJoinOUName": "NA"})
                if "BusinessCustom" not in parameter:
                    parameter.update({ "BusinessCustom": "NotOpted"})
                if "IsDatabricksAccount" not in parameter:
                    parameter.update({ "IsDatabricksAccount": "No"})
                if "DatabricksEnvironment" not in parameter:
                    parameter.update({ "DatabricksEnvironment": "NA"})
                if "DatabricksVolumeRequired" not in parameter:
                    parameter.update({ "DatabricksVolumeRequired": "No"})
                if "DatabricksS3Region" not in parameter:
                    parameter.update({ "DatabricksS3Region": "NA"})
                if "DatabricksProjectID" not in parameter:
                    parameter.update({ "DatabricksProjectID": "NA"})

            return parameters_list
        except Exception as ex:
            print("There is an error %s", str(ex))  

    ## Get all provisioned products with status "Active"
    def get_available_product(self):
        try:
            account_list = []
            errored_account_list = []
            response = servicecatalogclient.search_provisioned_products(Filters={"SearchQuery":["productName:platform_avm_product"]})
            result = response['ProvisionedProducts']
            while 'NextPageToken' in response:
                response = servicecatalogclient.search_provisioned_products(Filters={"SearchQuery":["productName:platform_avm_product"]}, PageToken=response['NextPageToken'])
                result.extend(response['ProvisionedProducts'])
            if (result):
                for item in result:
                    # Check the status of CT product
                    ct_status = self.check_status_control_tower_product(item["Name"])
                    print(f"ct status -- {ct_status}")
                    item["CTStatusBeforeUpdate"] = ct_status
                    print(f"item {item}")

                    if item['Status'] in ['AVAILABLE', 'TAINTED']:


                        if ct_status in ['AVAILABLE', 'TAINTED']:
                            print(f"CT is in {ct_status}")
                            account_list.append(item)
                        else:
                            errored_account_list.append(item)
                            print(f"CT is in {ct_status}")
                    else:
                        errored_account_list.append(item)
                print(f"account list--{account_list}")
                print(f"errored account list--{errored_account_list}")
            return [account_list,errored_account_list]

        except Exception as ex:
            print("There is an error %s", str(ex))

    ## Create list of required paramter dictionary list provisioned product output
    def get_available_product_info(self, listofpp):
        try:
            product_list = {"IsUpdateComplete": False, "ProvisionedProductList":[]}
            for eachproduct in listofpp:
                requireddatadict = {}
                print("before paramter call")
                print(f"each product {eachproduct}")

                parameterslist = self.get_provisionedproduct_parameters(eachproduct['PhysicalId'])
                print(f"after parameter call {parameterslist}")
                requireddatadict.update({ "Name" : eachproduct['Name'], 
                                        "Id": eachproduct['Id'], 
                                        "ProductId": eachproduct['ProductId'], 
                                        "ProductName": eachproduct['ProductName'],
                                        "ProvisioningArtifactId": eachproduct['ProvisioningArtifactId'],
                                        "ParametersList": parameterslist,
                                        "IsUpdated": False,
                                        "IsUpdateGoing": False,
                                        "StatusAfterUpdate": "",
                                        "CTStatusBeforeUpdate": eachproduct["CTStatusBeforeUpdate"],
                                        "CTStatusAfterUpdate": None,
                                        "CTLastUpdateTime": None
                                        })
                product_list['ProvisionedProductList'].append(requireddatadict)
            print(f"printing product list {product_list}")
            return product_list
        except Exception as ex:
            print("There is an error %s", str(ex))

    def get_error_product_info(self, listofpp):
        try:
            product_list = {"IsUpdateComplete": False, "ProvisionedProductList":[]}
            for eachproduct in listofpp:
                requireddatadict = {}
                print("before paramter call")
                print(f"each product {eachproduct}")
                
                if eachproduct['Status'] == "ERROR":

                    requireddatadict.update({ "Name" : eachproduct['Name'], 
                                            "Id": eachproduct['Id'], 
                                            "ProductId": eachproduct['ProductId'], 
                                            "ProductName": eachproduct['ProductName'],
                                            "ProvisioningArtifactId": eachproduct['ProvisioningArtifactId'],
                                            "IsUpdated": False,
                                            "Status": eachproduct['Status'],
                                            "StatusMessage": eachproduct['StatusMessage'],
                                            "CTStatusBeforeUpdate": eachproduct["CTStatusBeforeUpdate"]
                                            })
                else:
                    requireddatadict.update({ "Name" : eachproduct['Name'], 
                        "Id": eachproduct['Id'], 
                        "ProductId": eachproduct['ProductId'], 
                        "ProductName": eachproduct['ProductName'],
                        "ProvisioningArtifactId": eachproduct['ProvisioningArtifactId'],
                        "IsUpdated": False,
                        "Status": eachproduct['Status'],
                        "CTStatusBeforeUpdate": eachproduct["CTStatusBeforeUpdate"]
                        })

                product_list['ProvisionedProductList'].append(requireddatadict)
            print(f"printing product list {product_list}")
            return product_list
        except Exception as ex:
            print("There is an error %s", str(ex))
    


    ## Invoking provisoned products one after other
    def invoke_update_provision_product(self, account):
        try:
            provision_artifact = " "
            pa_res = servicecatalogclient.list_provisioning_artifacts(ProductId=account['ProductId'])
            
            if 'BusinessOperators' in account['ParametersList'][0].keys():
                BusinessOperators = account['ParametersList'][0]['BusinessOperators']
            else:
                BusinessOperators = ""

            if 'BusinessContributors' in account['ParametersList'][0].keys():
                BusinessContributors = account['ParametersList'][0]['BusinessContributors']
            else:
                BusinessContributors = ""

            if 'BusinessReadOnly' in account['ParametersList'][0].keys():
                BusinessReadOnly = account['ParametersList'][0]['BusinessReadOnly']
            else:
                BusinessReadOnly = ""

            if 'BusinessLimitedOperators' in account['ParametersList'][0].keys():
                BusinessLimitedOperators = account['ParametersList'][0]['BusinessLimitedOperators']
            else:
                BusinessLimitedOperators = ""
            
            if 'BusinessCustom' in account['ParametersList'][0].keys():
                BusinessCustom = account['ParametersList'][0]['BusinessCustom']
            else:
                BusinessCustom = "NotOpted"

            for pa in pa_res['ProvisioningArtifactDetails']:
                if pa['Active']:
                    provision_artifact = pa['Id']
                    print("Provisioning Artifact ID:", pa['Id'])
            response = " "
            if(provision_artifact):
                print("I am here in last IF condition....")
                print(f"invoking update for {account['Id']}")
                response = servicecatalogclient.update_provisioned_product(
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
                            "Key": "IsIOTAccount",
                            "Value": account['ParametersList'][0]['IsIOTAccount']
                        },
                        {
                            "Key": "IsRESPCAccount",
                            "Value": account['ParametersList'][0]['IsRESPCAccount']
                        },
                        {
                            "Key": "IsNonroutableSubnets",
                            "Value": account['ParametersList'][0]['IsNonroutableSubnets']
                        },
                        {
                            "Key": "HybridRESPCAccountDomainJoinOUName",
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
                        },  
                        {
                            "Key": "BusinessContributors",
                            "Value": BusinessContributors
                        },
                        {
                            "Key": "BusinessOperators",
                            "Value": BusinessOperators
                        },
                        {
                            "Key": "BusinessLimitedOperators",
                            "Value": BusinessLimitedOperators
                        },
                        {
                            "Key": "BusinessReadOnly",
                            "Value": BusinessReadOnly
                        },
                        {
                            "Key": "BusinessCustom",
                            "Value": BusinessCustom
                        }     
                    ]  
                )
            else:
                print("Provisioning Artifact ID not found for account : {}".format(account['Name']))
            return response
        except Exception as exception:
            print("send(..) failed executing GET account number:{} ".format(str(exception)))

    ## check status of provision product
    def check_status_avm_provisionproduct(self, ppid):
        try:
            status = ""
            search_filter = "id:" + ppid
            search_response = servicecatalogclient.search_provisioned_products(Filters={"SearchQuery": [search_filter]})
            print(search_response)
            status = search_response['ProvisionedProducts'][0]['Status']
            return status
        except Exception as exception:
            print("send(..) failed executing GET account number:{} ".format(str(exception)))
    
    def check_status_control_tower_product(self, name):
        try:
            status = ""
            search_filter = "name:AFPP-" +name
            print(f"search_filter {search_filter}")
            search_response = servicecatalogclient.search_provisioned_products(Filters={"SearchQuery": [search_filter]})
            print(search_response)
            
            for product in search_response["ProvisionedProducts"]:
                if product['Name'] == ("AFPP-" + name):
                    status = product['Status']
                    return status
        except Exception as exception:
             print("send(..) failed executing GET account number:{} ".format(str(exception)))
             
            
    def check_control_tower_product_last_update_time(self, name):
        try:
            status = ""
            last_record_id = ""
            search_filter = "name:AFPP-" +name
            search_response = servicecatalogclient.search_provisioned_products(Filters={"SearchQuery": [search_filter]})
            print(f"search response -- {search_response}")
            
            for product in search_response["ProvisionedProducts"]:
                print(f"product name {product['Name']}")
                print(name)
                if product['Name'] == ("AFPP-" + name):
                    print("product name matches")
                    last_record_id = product['LastRecordId']
                    response = servicecatalogclient.describe_record(Id=last_record_id)
                    print(response)
                    last_updated_time = response['RecordDetail']['UpdatedTime']
                    return last_updated_time.date()
                else:
                    
                    print("product name don't matches")
        except Exception as exception:
            print("send(..) failed executing GET account number:{} ".format(str(exception)))


    ## Create csv file dynamically
    def create_send_consolidated_csv_file(self, data_list, errored_data_list):
        try:
            print("Inside function to create the dynamic .csv file...")
            dynamicfilename = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
            print("filename create is {}".format(dynamicfilename))

            # Preparing CSV file for updated accounts
            consolidated_file_name = "AccountUpdateResults_" + dynamicfilename + ".csv"
            consolidated_file_path = "/tmp/" + consolidated_file_name
            print("file path:{}".format(consolidated_file_path))

            consolidated_csvfile = open(consolidated_file_path, 'w+', newline='')
            file_writer = csv.writer(consolidated_csvfile, delimiter=",", quoting=csv.QUOTE_MINIMAL)
            file_writer.writerow(['Name', 'Id', 'ProductId', 'ProductName','ProvisioningArtifactId', 'IsUpdated', 'AVMStatusAfterUpdate', "CTStatusBeforeUpdate", "CTStatusAfterUpdate", 'CTLastUpdateTime'])
            consolidated_csvfile.flush()
            print("Header row written!!!")

            for data in data_list:
                # ct_status_after_update = self.check_status_control_tower_product(data['Name'])
                ct_last_updated_time = self.check_control_tower_product_last_update_time(data['Name'])
                file_writer.writerow([data['Name'],data['Id'],data['ProductId'],data['ProductName'],data['ProvisioningArtifactId'],data['IsUpdated'],data['StatusAfterUpdate'], data["CTStatusBeforeUpdate"], data["CTStatusAfterUpdate"], ct_last_updated_time])
                consolidated_csvfile.flush()
            consolidated_csvfile.close()

            # Preparing CSV file for non-updated accounts
            consolidated_errored_file_name = "Errored_accounts_" + dynamicfilename + ".csv"
            consolidated_errored_file_path = "/tmp/" + consolidated_errored_file_name
            print("file path:{}".format(consolidated_errored_file_path))

            consolidated_errored_csvfile = open(consolidated_errored_file_path, 'w+', newline='')
            file_writer = csv.writer(consolidated_errored_csvfile, delimiter=",", quoting=csv.QUOTE_MINIMAL)
            file_writer.writerow(['Name', 'Id', 'ProductId', 'ProductName','ProvisioningArtifactId', 'IsUpdated', 'Status', 'StatusMessage', 'CTStatusBeforeUpdate'])
            consolidated_errored_csvfile.flush()
            print("Header row written!!!")
            for data in errored_data_list:
                print(f"data---{data}")
                print(f"status---{data['Status']}")

                if data['Status'] == 'ERROR':
                    file_writer.writerow([data['Name'],data['Id'],data['ProductId'],data['ProductName'],data['ProvisioningArtifactId'],data['IsUpdated'],data['Status'], data['StatusMessage'], data["CTStatusBeforeUpdate"]])
                else:
                    file_writer.writerow([data['Name'],data['Id'],data['ProductId'],data['ProductName'],data['ProvisioningArtifactId'],data['IsUpdated'],data['Status'], "N/A", data["CTStatusBeforeUpdate"]])

                consolidated_errored_csvfile.flush()
            consolidated_errored_csvfile.close()

            self.send_mail(consolidated_file_path,consolidated_errored_file_path)
        except Exception as exception:
            print("Some error occurred: {}".format(str(exception)))

    ## Send email
    def send_mail(self, consolidated_file_path, consolidated_errored_file_path):
        try:
            # This address must be verified with Amazon SES.
            sender_id = "SITI-CLOUD-SERVICES@shell.com"
            to_recipient = ["GXSOMWIPROCLOUDAWSDA2@shell.com"]

            # The email body for recipients with non-HTML email clients.
            body_text = "Hello Team,\r\nPlease find the attachment for AWS@Shell account update results\r\nRegards,\r\nAWS@Shell Platform Automations"

            # The HTML body of the email.
            body_html = """
                            <html>
                            <head></head>
                            <body>
                            <h2>Hello Team,</h2>
                            <p>Please find the attachment for AWS@Shell account update results.</p>

                            <p>Regards,</p>
                            <p>AWS@Shell Platform Automations</p>
                            </body>
                            </html>
                            """
            try:
                # The subject line for the email.
                mail_subject = "AWS@Shell account update results"

                # The full path to the file that will be attached to the email.
                attachment_template = [consolidated_file_path, consolidated_errored_file_path]

                # Create a multipart/mixed parent container.
                msg = MIMEMultipart('mixed')

                # Add subject, from and to lines.
                msg['Subject'] = mail_subject
                msg['From'] = sender_id
                msg['To'] = ', '.join(to_recipient)

                # Create a multipart/alternative child container.
                msg_body = MIMEMultipart('alternative')

                char_set = "utf-8"
                # necessary if you're sending a message with characters outside the ASCII range.
                textpart = MIMEText(body_text.encode(char_set), 'plain', char_set)
                htmlpart = MIMEText(body_html.encode(char_set), 'html', char_set)

                # Add the text and HTML parts to the child container.
                msg_body.attach(textpart)
                msg_body.attach(htmlpart)

                # Define the attachment part and encode it using MIMEApplication.

                for attachment in attachment_template:
                    att = MIMEApplication(open(attachment, 'rb').read())

                    # Add a header to tell the email client to treat this part as an attachment,
                    # and to give the attachment a name.
                    att.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment))
                    print("att>>> ", att)

                    # Add the attachment to the parent container.
                    msg.attach(att)
                    # Attach the multipart/alternative child container to the multipart/mixed
                    # parent container.

                msg.attach(msg_body)



                mail_response = simpleemailserviceclient.send_raw_email(
                    Source=sender_id,
                    Destinations=to_recipient,
                    RawMessage={
                        'Data': msg.as_string()
                    }
                )
            # Display an error if something goes wrong.
            except Exception as exception:
                print(exception)
            else:
                print("Email sent! Message ID:")
                print(mail_response['ResponseMetadata']['RequestId'])
                os.remove(consolidated_file_path)
                print("File deleted after the email is sent")
        except Exception as exception:
            print(exception)
            print("ERROR in sending mail try", exception)

    ## Upload in S3 bucket
    def Upload_in_S3bucket(self, allaccountdata, *args):
        print("All account data {}".format(allaccountdata))
        try:
            print("Inside function to create the dynamic .json file...")
            if args:
              dynamicfilename = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p") + "_Errored_under_change"
            else:
              dynamicfilename = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
            print("filename format created is {}".format(dynamicfilename))
            file_name =  dynamicfilename + "_UpdateAccountList.json"
            print("file name is {}".format(file_name))
            s3_file_name =  dynamicfilename + "/" + file_name
            print("s3 bucket path in bucket aws@shell-account-update-logs would be  {}".format(s3_file_name))
            local_file_path = "/tmp/UpdateAccountList.json"
            print("file path:{}".format(local_file_path))
            with open(local_file_path, 'w') as fp:
                json.dump(allaccountdata, fp)
            print("all account data is stored in local json file")
            self.s3_client.upload_file(local_file_path, self.account_update_bucket, s3_file_name)
            print("file uploaded successfully..")
            os.remove(local_file_path)
            print("File deleted after upload to s3 bucket")
        except Exception as exception:
            print("Exception in Lambda Handler and error is {}".format(exception))
        return s3_file_name

    ## Download a file from a S3 bucket.
    def download_from_S3bucket(self, file_name, object_name):
        s3_client = boto3.client('s3')
        try:
            s3_client.download_file(self.account_update_bucket, object_name, file_name)
        except Exception as exception:
            print("failed at download_from_S3bucket and error is :{} ".format(str(exception)))
            return False
        return True

    ## Delete a file from a S3 bucket.
    def delete_file_S3bucket(self, key_name):
        s3_client = boto3.client('s3')
        try:
            s3_client.delete_object(Bucket=self.account_update_bucket, Key=key_name)
        except Exception as exception:
            print("failed at delete_file_S3bucket and error is :{} ".format(str(exception)))
            return False
        return True

def lambda_handler(event, context):
    updateaccount = UpdateChildAccount(event, context)
    try:
        if event:
            if updateaccount.download_from_S3bucket("/tmp/UpdateAccountList.json", event['FileName']):
                print("file is successfully downloaded from s3 bucket..")
                with open(r"/tmp/UpdateAccountList.json", "r") as read_file:
                    data = json.load(read_file)
                    print(data)
                
                updating_product_list  = [ item for item in data['ProvisionedProductList'] if item['IsUpdateGoing'] == True ]
                print(f"Update going for the accounts {updating_product_list}")
                
                if len(updating_product_list) >= 9:
                    no_of_parallel_updates = 9
                else:
                    no_of_parallel_updates = len(updating_product_list)

                for i in range(0,no_of_parallel_updates):
                 if updating_product_list[i]:
                    avm_statuscheckoutput = updateaccount.check_status_avm_provisionproduct(updating_product_list[i]['Id'])

                    control_tower_statuscheckoutput = updateaccount.check_status_control_tower_product(updating_product_list[i]['Name'])

                    print(f"control_tower_statuscheckoutput {control_tower_statuscheckoutput}")
                    print(f"checking for {updating_product_list[i]['Id']} and underlying control tower product {control_tower_statuscheckoutput} ")
                    if avm_statuscheckoutput in ["AVAILABLE","TAINTED","ERROR"] and control_tower_statuscheckoutput in ["AVAILABLE","TAINTED","ERROR"]:
                        print(f"update completed for ppid {updating_product_list[i]['Id']}")
                        
                        # ct_last_updated_time = updateaccount.check_control_tower_product_last_update_time(updating_product_list[i]['Name'])
                        
                        updating_product_list[i].update({"IsUpdateGoing": False})
                        updating_product_list[i].update({"IsUpdated": True})
                        updating_product_list[i].update({"StatusAfterUpdate": avm_statuscheckoutput})
                        updating_product_list[i].update({"CTStatusAfterUpdate": control_tower_statuscheckoutput})
                        # updating_product_list[i].update({"CTSLastUpdatedTime": ct_last_updated_time})
                        
                        print(f"updated data after {updating_product_list[i]['Id']} has completed-- {data}")
                        next_item_to_update = next(iter(item for item in data['ProvisionedProductList'] if item['IsUpdated'] == False and item['IsUpdateGoing'] == False), None)
                        if next_item_to_update :
                            updateaccount.invoke_update_provision_product(next_item_to_update)
                            next_item_to_update.update({"IsUpdateGoing": True})

                            
                        else:
                            next_item_update_in_progress = next(iter(item for item in data['ProvisionedProductList'] if item['IsUpdated'] == False and item['IsUpdateGoing'] == True), None)
                            if next_item_update_in_progress:
                                pass
                            else:
                                print(f"data when sending email -- {data}")
                                print("Update complete invoking email for results..")
                                if updateaccount.download_from_S3bucket("/tmp/Errored_UpdateAccountList.json", event['Errored_FileName']):
                                    print(f"Errored file name --- {event['FileName']}")

                                    print("file is successfully downloaded from s3 bucket..")
                                    with open(r"/tmp/Errored_UpdateAccountList.json", "r") as read_file:
                                            errored_data = json.load(read_file)
                                            print(f"errored_account_data---{errored_data}")

                                updateaccount.create_send_consolidated_csv_file(data['ProvisionedProductList'], errored_data['ProvisionedProductList'])
                                print("email sent..!!")
                                if updateaccount.delete_file_S3bucket(event['FileName']) :
                                    os.remove("/tmp/UpdateAccountList.json")
                                    print("file deleted from buckets and removed from lambda too..")
                                data['IsUpdateComplete'] == True
                                return {"FileName": updateaccount.Upload_in_S3bucket(data), "IsUpdateComplete": True, "Errored_FileName": event["Errored_FileName"]}
                    elif avm_statuscheckoutput in ["UNDER_CHANGE"] or control_tower_statuscheckoutput in ["UNDER_CHANGE"] :
                        continue
                    else:
                        print(f"There is some issue with ppid {updating_product_list[i]['Id']}")
                        updating_product_list[i].update({"IsUpdateGoing": False})
                        updating_product_list[i].update({"IsUpdated": True})
                        updating_product_list[i].update({"StatusAfterUpdate": "Issues found with ppid"})


                print(f"data after loop is finished {data}")
                if updateaccount.delete_file_S3bucket(event['FileName']) :
                        if os.path.exists('("/tmp/UpdateAccountList.json"'):
                                os.remove("/tmp/UpdateAccountList.json")
                                print("file deleted from buckets and removed from lambda too..")

                return {"FileName": updateaccount.Upload_in_S3bucket(data), "IsUpdateComplete": False, "Errored_FileName": event["Errored_FileName"]}
            else :
                print("file download failed..")

        else:
            accounts_list,errored_accounts_list = updateaccount.get_available_product()

            errored_accountlist_info = updateaccount.get_error_product_info(errored_accounts_list)
            print(f"errored_accountlist_info---{errored_accountlist_info}")

            print("Uploading Errored accounts onto S3")
            errored_file_name = updateaccount.Upload_in_S3bucket(errored_accountlist_info, "errored")
            print("Uploading of Errored account list to S3 completed")
            final_accountlist = updateaccount.get_available_product_info(accounts_list)
            print(f"account_list--{final_accountlist}")            

            for i in range(0,9):
               print(f"invoking update for {final_accountlist['ProvisionedProductList'][i]}")
               updateaccount.invoke_update_provision_product(final_accountlist['ProvisionedProductList'][i])
               final_accountlist['ProvisionedProductList'][i].update({"IsUpdateGoing": True})
            return {"FileName": updateaccount.Upload_in_S3bucket(final_accountlist), "IsUpdateComplete": False, "Errored_FileName": errored_file_name}  
    except Exception as exception:
        print(exception)
        return exception