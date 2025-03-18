"""
This module is used to update the Accounts_Details table whenever any action is performed on
member accounts
"""
import datetime
import logging
import json

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


class UpdateAccountTable(object):
    """
    # Class: UpdateDLTable
    # Description: Includes all the properties and method to update the relevant
    # details to the DLDetailsTable after the Child account is created.
    """

    def __init__(self, event, context):
        self.event = event
        self.context = context

        try:
            session_client = boto3.session.Session()
            self.acnts_table_name = event['SSMParametres']['accountDetailTableName']
            self.event = self.merge_output(event)
            # logger.info("Merged Event: %s" % self.event)
            # get relevant input params from event
            resource_properties = self.event['ResourceProperties']
            self.reason_data = ""
            self.request_type = self.event['RequestType']
            if resource_properties['Migration'] == "Yes":
                self.dl_for_new_account = resource_properties['dlForNewAccount']
            else:
                self.dl_for_new_account = event['dlForNewAccount']
            self.account_number = self.event['accountNumber']
            self.account_name = resource_properties['AccountName']
            self.completed_time_stamp = self.event['completedTimeStamp']
            self.budget_value = resource_properties['Budget']
            self.line_of_business = resource_properties['LOB']
            self.is_IOT_Account = resource_properties['IsIOTAccount']
            self.is_RESPC_Account = resource_properties['IsRESPCAccount']
            self.non_rou_subnets = resource_properties['IsNonroutableSubnets']
            self.sold_to_code = resource_properties['SoldToCode']
            self.support_dl = resource_properties['SupportDL']
            self.requester_id = resource_properties['RequestorEmail']
            self.request_id = []
            self.request_id.append({'S': resource_properties['RequestNo']})
            self.custodian_user = resource_properties['CustodianUser']
            self.apex_id = resource_properties['ApexID']
            self.SOXrelevant = resource_properties['SOXrelevant']
            self.ActiveBIAid = resource_properties['ActiveBIAid']
            self.DataClassification = resource_properties['DataClassification']
            self.AccountTenancy = resource_properties['AccountTenancy']
            self.ppid = self.event['ppid']
            self.data_format = "%d-%m-%Y"

            session_client = boto3.Session()
            self.dd_client = session_client.client('dynamodb', region_name="us-east-1")
            self.support_dl = resource_properties['SupportDL']
            # print ("CIDR",self.event['CIRD'])
            key_list = self.event.keys()
            if "CIDR" in key_list:
                self.CIDR = self.event['CIDR']
            else:
                self.CIDR = None
        except Exception as exception:
            self.reason_data = "Missing required property %s" % exception
            logger.error(self.reason_data)

    def merge_output(self, events):
        event = {}
        if type(events) is list:
            send_budget_email = False
            for e in events:
                event.update(e)

                if 'send_budget_email' in e.keys() and e['send_budget_email'] == True:
                    send_budget_email = True

            if (send_budget_email == True):
                event['emailParameter'].append('budgetMail')

        elif type(events) is dict:
            event = events
        return event

    def update_account_details(self):
        """
        The following method upddates the DL details table after account
        creation.
        # Add oldRequestTypes in the Update table, add the logic for if entry is there
        # do not add the entry but update it
        :return:
        """
        # # Code to update the request status in the DynamoDB table
        try:
            region = ','.join(list(self.event['region_ip_dict'].keys()))
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
                'CreationDate': {"S": self.completed_time_stamp},
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
                'EnabledRegion': {"S": region},
                'Organization': {"S": self.event['ResourceProperties']['Environment']}
            }

            print ("CIDR",self.CIDR)
            if self.CIDR != None:
                cidr_table = []
                if 'Item' in get_response:
                    if 'CIDR' in get_response['Item']:
                        cidr_table = get_response['Item']['CIDR']['L']

                list_cidr = []
                # print (self.CIDR)
                for ip_add in self.CIDR:
                    dic = {}
                    dic['S'] = str(ip_add)
                    list_cidr.append(dic)
                list_cidr.extend(cidr_table)
                print (list_cidr)
                table_item['CIDR'] = {"L": list_cidr}

            # print (table_item)

            if 'Item' in get_response_keys:
                # self.requesterAdminUser.extend(getResponse['Item']['AdminUsers']['L'])
                self.request_id.extend(get_response['Item']['RequestNo']['L'])
                table_item['RequestNo']['L'] = self.request_id
                if self.request_type == 'Create':
                    print("Create Condition")
                    table_item['State'] = {"S": "Active"}
                    table_item['CreationDate'] = {"S": str(
                        datetime.datetime.now().strftime(self.data_format))}
                elif self.request_type == 'Update':
                    print("Update Condition")
                    table_item['State'] = {"S": "Active"}
                    table_item['UpdationDate'] = {"S": str(
                        datetime.datetime.now().strftime(self.data_format))}

                else:
                    print("Delete Condition")
                    table_item['State'] = {"S": "Decomissioned"}
                    table_item['DeletionDate'] = {"S": str(
                        datetime.datetime.now().strftime(self.data_format))}
                print("Inside Update/Delete block")
                insert_response = self.dd_client.put_item(
                    TableName=self.acnts_table_name,
                    Item=table_item
                )
            else:
                table_item['State'] = {"S": "Active"}
                insert_response = self.dd_client.put_item(
                    TableName=self.acnts_table_name,
                    Item=table_item
                )
            self.event['Update_Request'] = "PASSED"
        except Exception as exception:
            self.reason_data = "dynamoDB Account details update failed %s" % exception
            logger.error(self.reason_data)
            self.event['Update_Request'] = "FAILED"

        return self.event

def lambda_handler(event, context):
    """
        This is the entry point of the module
        :param event:
        :param context:
        :return:
    """
    try:
        account_object = UpdateAccountTable(event, context)
        output_values = account_object.update_account_details()
        output_values['update_account_details'] = "PASSED"
        print(json.dumps(output_values))
        return output_values
    except Exception as exception:
        print(exception)
        return event
