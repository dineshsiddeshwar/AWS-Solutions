import boto3
import logging
import json
import time

LOGGER = logging.getLogger('logging')
LOGGER.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
LOGGER.addHandler(CH)


SUCCESS = "SUCCESS"
FAILED = "FAILED"

SESSION = boto3.Session()
STS_CLIENT = SESSION.client('sts')
servicecatalogclient = SESSION.client('servicecatalog')
cloudformationclient = SESSION.client('cloudformation')



def get_available_product():
    """
    This module will get the list of available product
    """
    try:
        account_list = []
        sc_response = servicecatalogclient.search_provisioned_products(Filters={"SearchQuery":["productName:platform_avm_product"]})
        result = sc_response['ProvisionedProducts']
        while 'NextPageToken' in sc_response:
            sc_response = servicecatalogclient.search_provisioned_products(Filters={"SearchQuery":["productName:platform_avm_product"]}, PageToken=sc_response['NextPageToken'])
            result.extend(sc_response['ProvisionedProducts'])
        if (result):
            for item in result:
                if item['Status'] in ['AVAILABLE', 'TAINTED']:
                    account_list.append(item)
        LOGGER.info("Account present in tainted and available state {0}".format(account_list))
        return account_list
    except Exception as exception:
        print("There is an error in get available product %s", str(exception))
        return exception
 
 
def get_provision_id(stackid):
    """
    This module is for t get provision product for the account
    """
    try:
        
        parameters_list = []
        LOGGER.info("Inside Get Provision Product ID")
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
        LOGGER.info("Parameter List obtained is {0}".format(parameters_list))
        return parameters_list
    except Exception as ex:
        print("There is an error in getting provision id %s", str(ex))
        return parameters_list
 
def invoke_update_provision_product(account,Environment):
    """
    This module is responsible for invoking update 
    """
    try:
        LOGGER.info("Account we got is :- ".format(account))
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
        print("provision artifcat detailsssssssssssssssssssssssssssssssssssssss")
        print(pa_res)
        for pa in pa_res['ProvisioningArtifactDetails']:
            if pa['Active']:
                provision_artifact = pa['Id']
                print("Provisioning Artifact ID:", pa['Id'])
        response = " "
        print("--------------------------------------")
        print(provision_artifact)
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
                        "Key": "Singapore",
                        "Value": account['ParametersList'][0]['Singapore']
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
                        "Value": Environment
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
                    }     
                ]  
            )
        else:
            print("Provisioning Artifact ID not found for account : {}".format(account['Name']))
        return response['RecordDetail']['Status']
    except Exception as exception:
        print("send(..) failed invoking the provision product:{} ".format(str(exception)))            
        return FAILED

def check_provision_product_status(id):
    try:
        LOGGER.info("Inside check provision product status....")
        sc_response = servicecatalogclient.describe_provisioned_product(Id=id)
        status = sc_response["ProvisionedProductDetail"]["Status"]
        return status
    except Exception as exception:
        print("send(..) failed executing GET account number:{} ".format(str(exception)))        
        return status


def get_provision_id_info(listofpp):
    """
    This module is for getting the status and info of pp
    """
    try:
            product_list = {"ProvisionedProductList":[]}
            for eachproduct in listofpp:
                requireddatadict = {}
                LOGGER.info("Getting info of product {0}".format(eachproduct))
                parameterslist = get_provision_id(eachproduct['PhysicalId'])
                requireddatadict.update({ "Name" : eachproduct['Name'], 
                                        "Id": eachproduct['Id'], 
                                        "ProductId": eachproduct['ProductId'], 
                                        "ProductName": eachproduct['ProductName'],
                                        "ProvisioningArtifactId": eachproduct['ProvisioningArtifactId'],
                                        "ParametersList": parameterslist
                                        })
                product_list['ProvisionedProductList'].append(requireddatadict)
            LOGGER.info("Final Product List :- {0}".format(product_list))
            return product_list
    except Exception as ex:
        print("There is an error %s", str(ex))
        return product_list

def lambda_handler(event, context):
    """_summary_

    Args:
        event (json): This lambda handler will move the account to exception OU
    """
    try:
        LOGGER.info("Recieved event :- {0}".format(event))
        list_status = ['SUCCEEDED','IN_PROGRESS','CREATED']
        modified_event = {}
        modified_event.update(event)
        account_list = get_available_product()
        if account_list:
            update_param_list = get_provision_id_info(account_list)
            if update_param_list != []:
                for account in update_param_list['ProvisionedProductList']:
                    if account['ParametersList'][0]['AccountName'] == event['accountName']:
                        invoking_status = invoke_update_provision_product(account,event['Move_to_OU'])
                        if invoking_status in list_status:
                            LOGGER.info("================================== Time To sleep for 10 sec before exit ===================================================")
                            LOGGER.info("Provisoned Product Invoked just now.")
                            modified_event.update({"Account_movement": SUCCESS})
                            time.sleep(10)
                            LOGGER.info("Checking the status {0}. ".format(account['Id']))
                            check_status = check_provision_product_status(account['Id'])
                            modified_event.update({"provision_product_status": check_status})
                            modified_event.update({"provision_product_id": account['Id']})
                            modified_event.update({"provision_product_name": account['Name']})
                            break
                        else:
                            LOGGER.info("Something went wrong in invoking product.")
                            modified_event.update({"Account_movement": FAILED})
                    else:
                        LOGGER.info("Checked {0}..Account Product not found.Checking next product...".format(account['ParametersList'][0]['AccountName']))
                        modified_event.update({"Account_movement": 'Skipped'})
            else:
                LOGGER.info("Something went wrong in invoking product.")
                modified_event.update({"Account_movement": FAILED})     
        return modified_event
    except Exception as exception:
        print("Error in Lambda Handler", exception)
        event.update({"Account_movement": FAILED})
        return event