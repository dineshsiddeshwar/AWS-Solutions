"""
This module is as part of account decommission to close the member account permanently
"""
import time
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

class CloseAccount(object):
    """
        This class is used to close the member account permanently
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
            session_client = boto3.Session()
            self.account_number = event['accountNumber']
            self.org_client = session_client.client('organizations')
        except Exception as exception:
            self.reason_data = "Missing required property %s" % exception
            logger.error(self.reason_data)

    def close_account(self):
        """
        # Function: closeAccount
        # Description: Close the member account using CloseAccount API call from Organizations
        :return:
        """
        try:
            print(f'Account to be closed is {self.account_number}')
            response = self.org_client.close_account(AccountId=self.account_number)
            print(response)
            print("Account Closure operation is started...")
            describe_acct_response = self.org_client.describe_account(AccountId=self.account_number)
            acct_status = describe_acct_response['Account']['Status']
            print("Checking the account closure status first time...")
            print(acct_status)
            print(boto3.__version__)
            wait_time = 60
            retries = 0
            while retries < 5 and acct_status != 'SUSPENDED':
                print(acct_status)
                if acct_status == 'ACTIVE':
                    print(f'Account {self.account_number} is still in Active State...')
                elif acct_status == 'PENDING_CLOSURE':
                    print(f'Account {self.account_number} is still pending to be closed...')
                else:
                    break
                time.sleep(wait_time)
                retries += 1
                print("Checking account status...")
                describe_acct_response = self.org_client.describe_account(AccountId=self.account_number)
                acct_status = describe_acct_response['Account']['Status']
                print(acct_status)
            describe_acct_response = self.org_client.describe_account(AccountId=self.account_number)
            acct_status = describe_acct_response['Account']['Status']
            if acct_status == 'SUSPENDED':
                print(f'Account {self.account_number} has been closed successfully with status as {acct_status}') 
                return True
            else:
                print(f'Account closure for account {self.account_number} is failed with status as {acct_status}. Please troubleshoot further')
                return False
        except Exception as exception:
            logger.error(str(exception))
            print(f'Error occurred while closing member AWS account {self.account_number}')
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
        close_account_object = CloseAccount(event, context)
        output_status = close_account_object.close_account()
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