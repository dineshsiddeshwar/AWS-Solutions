"""
This module is as part of account decommission to move the member account to the decommissioned
OU of the Master Account
"""
import random
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(FORMATTER)
logger.addHandler(ch)
RESULT_DICT = {}

class MoveDecomOU(object):
    """
       This class is used to move the member account to decommission OU
    """
    def __init__(self, event, context):
        self.event = event
        self.context = context
        logger.info("Event: %s" % self.event)
        logger.info("Context: %s" % self.context)
        try:
            # get relevant input params from event
            resource_properties = event['ResourceProperties']
            logger.debug(resource_properties)
            self.reason_data = ""
            self.account_number = event['accountNumber']
            print(f'The account to be moved under Decommisioned OU is {self.account_number}')
            session_client = boto3.Session()
            self.ssm_client = session_client.client('ssm')

            parameter_list = []
            params_dict = {}
            parameter_name = "platform_ou_decommission"
            param_value = ""
            response = self.ssm_client.get_parameter(Name=parameter_name)
            param_value = response['Parameter']['Value']
            master_account_response=self.ssm_client.get_parameter(Name="master_account")
            self.master_account=master_account_response['Parameter']['Value']
            self.ou_destination_parentid = param_value
            print(f'The destination OU ID is {self.ou_destination_parentid}')
            self.org_client = session_client.client('organizations')
            parent_ou_response = self.org_client.list_parents(ChildId=self.account_number)
            self.parent_ou_id = parent_ou_response['Parents'][0]['Id']
            print(f'The source OU ID is {self.parent_ou_id}')
        except Exception as exception:
            self.reason_data = "Missing required property %s" % exception
            logger.error(self.reason_data)

    def list_account_for_parent(self):
        """
        # Function: listAccountsForParent
        # Description: get the decommissioned accounts list from  decommissioned OU
        :return:
        """
        try:
            account_array = []
            next_token = 'null'
            member_account_response = self.org_client.list_accounts_for_parent(
                ParentId=self.ou_destination_parentid)
            accounts = member_account_response['Accounts']
            for account in accounts:
                account_array.append(account['Id'])
            if 'NextToken' in member_account_response.keys():
                next_token = member_account_response['NextToken']
            while 'NextToken' in member_account_response:
                member_account_response = self.org_client.list_accounts_for_parent(
                    ParentId=self.ou_destination_parentid, NextToken=next_token)
                accounts = member_account_response['Accounts']
                for account in accounts:
                    account_array.append(account['Id'])
                if 'NextToken' in member_account_response.keys():
                    next_token = member_account_response['NextToken']
            print("Decommissioned OU final list" + str(account_array))
            RESULT_DICT['list_account_for_parent'] = "PASSED"
            return account_array
        except Exception as exception:
            print(str(exception))
            print("Error occurred while listing decommissioned OU list")
            return ""

    def decommision_ou(self):
        """
        # Function: decommision_ou
        # Description: Includes all the properties and method to move member
        account to decommission OU
        :return:
        """
        try:
            decommissioned_ou_accounts_arr = self.list_account_for_parent()
            if not decommissioned_ou_accounts_arr:
                print("Decommissioned OU list is empty, Hence move {} "
                      "account in OU".format(self.account_number))
                move_account_response = self.org_client.move_account(
                    AccountId=self.account_number, SourceParentId=self.parent_ou_id,
                    DestinationParentId=self.ou_destination_parentid)
                print("OU movement Response", move_account_response)
            else:
                print("Decommissioned OU list is not empty, Hence check {} "
                      "account in OU".format(self.account_number))
                if self.account_number in decommissioned_ou_accounts_arr:
                    print("Decommissioned account {} has been moved "
                          "to decommissioned OU already".format(self.account_number))
                else:
                    print("{} account is not available in OU, "
                          "Hence move it".format(self.account_number))
                    move_account_response = self.org_client.move_account(
                        AccountId=self.account_number, SourceParentId=self.parent_ou_id,
                        DestinationParentId=self.ou_destination_parentid)
                    print("OU movement Response", move_account_response)
            RESULT_DICT['decommision_ou'] = "PASSED"
            return True
        except Exception as exception:
            logger.error(str(exception))
            print("Error occurred while {} account moving to "
                  "decommissioned OU".format(self.account_number))
            return False


def lambda_handler(event, context):
    """
            This is the entry point of the module
            :param event:
            :param context:
            :return:
    """

    try:
        print('event ' + str(event))
        result_values = {}
        result_values.update(event)
        decom_ou_object = MoveDecomOU(event, context)
        output_status = decom_ou_object.decommision_ou()
        if not output_status:
            event['emailParameter'].append('decomFailure')

        else:
            event['emailParameter'].append('decomSuccess')
            event['emailParameter'].append('AccountDecomCleanupMail')

        print(str(result_values))
        return result_values
    except Exception as exception:
        print(exception)
        return exception
