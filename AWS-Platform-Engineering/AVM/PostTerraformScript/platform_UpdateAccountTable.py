"""
This module is used to update the Accounts_Details table whenever any action is performed on
member accounts
"""
import datetime
import json
import sys
import boto3
from datetime import datetime

class UpdateAccountTable(object):

    def __init__(self, event):
        self.event = event
        try:
            session_client = boto3.session.Session()
            self.acnts_table_name = event['SSMParameters']['accountDetailTableName']
            self.request_type = self.event['RequestType']
            self.account_number = self.event['ProvisionedProduct']['AccountNumber']
            self.account_name = self.event['ProvisionedProduct']['Name']
            self.ppid = self.event['ProvisionedProduct']['Id']
            self.time_stamp = datetime.now().strftime("%Y:%m:%d:%I:%M:%S")
            resource_properties = self.event['RequestEventData']
            self.budget_value = resource_properties['Budget']
            self.line_of_business = resource_properties['LOB']
            self.is_IOT_Account = resource_properties['IsIOTAccount']
            self.is_RESPC_Account = resource_properties['IsRESPCAccount']
            self.non_rou_subnets = resource_properties['IsNonroutableSubnets']
            self.sold_to_code = resource_properties['SoldToCode']
            self.support_dl = resource_properties['SupportDL']
            self.dl_for_new_account = self.event['ProvisionedProduct']['AccountDL']
            self.requester_id = resource_properties['RequestorEmail']
            self.request_id = []
            self.request_id.append({'S': resource_properties['RequestNo']})
            self.custodian_user = resource_properties['CustodianUser']
            self.apex_id = resource_properties['ApexID']
            self.SOXrelevant = resource_properties['SOXrelevant']
            self.ActiveBIAid = resource_properties['ActiveBIAid']
            self.DataClassification = resource_properties['DataClassification']
            self.AccountTenancy = resource_properties['AccountTenancy']
            session_client = boto3.Session()
            self.dd_client = session_client.client('dynamodb', region_name="us-east-1")

            self.RegionIpDictionary_EU = self.event['RegionIpDictionary_EU']
            self.RegionIpDictionary_US = self.event['RegionIpDictionary_US']
            self.RegionIpDictionary_SG = self.event['RegionIpDictionary_SG']

            self.account_ou = self.event['ProvisionedProduct']['OU']

            self.regions_str = event['SSMParameters']['whitelisted_regions_private'] if "Private" in event['ProvisionedProduct']['OU'] or "Hybrid" in event['ProvisionedProduct']['OU'] else event['SSMParameters']['whitelisted_regions_public']
            print("Regions allowed", self.regions_str)
            if resource_properties['Migration'] == "Yes":
                self.dl_for_new_account = event['ProvisionedProduct']['AccountDL']
        except Exception as exception:
            print("Missing required property:", exception)

    def update_account_details(self):
        try:
            get_response = self.dd_client.get_item(
                TableName=self.acnts_table_name,
                Key={
                    'AccountNumber': {"S": self.account_number}
                }
            )
            get_response_keys = get_response.keys()
            print("Inside account update method")

            table_item = {
                'AccountNumber': {"S": self.account_number},
                'AccountName': {"S": self.account_name},
                'CreationDate': {"S": self.time_stamp},
                'RequestNo': {'L': self.request_id},
                'RequestorEmail': {"S": self.requester_id},
                'DLUsed': {"S": self.dl_for_new_account},
                'Budget': {"S": self.budget_value},
                'LoB': {"S": self.line_of_business},
                'IsIOTAccount': {"S": self.is_IOT_Account},
                'IsRESPCAccount': {"S": self.is_RESPC_Account},
                'IsNonroutableSubnets': {"S": self.non_rou_subnets},
                'SoldToCode': {"S": self.sold_to_code},
                'SupportDL': {"S": self.support_dl},
                'CustodianUser': {"S": self.custodian_user},
                'ApexID': {"S": self.apex_id},
                'SOXrelevant': {"S": self.SOXrelevant},
                'ActiveBIAid': {"S": self.ActiveBIAid},
                'DataClassification': {"S": self.DataClassification},
                'AccountTenancy': {"S": self.AccountTenancy},
                'Ppid': {"S": self.ppid},
                'EnabledRegion': {"S": self.regions_str},
                'Organization': {"S": self.account_ou},
                'RegionIpDictionary_EU' : {"S": str(self.RegionIpDictionary_EU)},
                'RegionIpDictionary_US' : {"S": str(self.RegionIpDictionary_US)},
                'RegionIpDictionary_SG' : {"S": str(self.RegionIpDictionary_SG)},
                'IsNewAVM' : {"S": "TRUE"}
            }

            if 'Item' in get_response_keys:
                self.request_id.extend(get_response['Item']['RequestNo']['L'])
                table_item['RequestNo']['L'] = self.request_id
                if self.request_type == 'Create':
                    print("Create Condition")
                    table_item['State'] = {"S": "Active"}
                    table_item['CreationDate'] = {"S": str(self.time_stamp)}
                elif self.request_type == 'Update':
                    print("Update Condition")
                    table_item['State'] = {"S": "Active"}
                    table_item['UpdationDate'] = {"S": str(self.time_stamp)}
                else:
                    print("Delete Condition")
                    table_item['State'] = {"S": "Decomissioned"}
                    table_item['DeletionDate'] = {"S": str(self.time_stamp)}
                print("Inside Update/Delete block")
                self.dd_client.put_item(
                    TableName=self.acnts_table_name,
                    Item=table_item
                )
            else:
                table_item['State'] = {"S": "Active"}
                self.dd_client.put_item(
                    TableName=self.acnts_table_name,
                    Item=table_item
                )
            return True
        except Exception as exception:
            print("dynamoDB Account details update failed:", exception)
            return False

try:
    local_file_path = str(sys.argv[1])+"parameters.json"
    print("Parameters local file path: ", local_file_path)
    with open(local_file_path) as json_data:
        parameters_data = json.load(json_data)
    print(parameters_data)
    if parameters_data : 
        print("parameters are loaded in json format, invokes update_request_details function..")
        updateAccountTableobject = UpdateAccountTable(parameters_data)
        if updateAccountTableobject.update_account_details():
            print("Update Account Details Table is success..!!")
        else:
            print("EUpdate Account Details Table is fialed..!!")
except Exception as ex:
    print("There is an error %s", str(ex))
