"""
This module is used to update the DL table when any DL used for account creation
"""
import logging
import datetime
import boto3
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


class UpdateDLTable(object):
    """
    # Class: UpdateAccountTable
    # Description: Includes all the properties and method to update the relevant
    # details to the AccountDetailsTable after the Child account is created.
    """

    def __init__(self, event, context):
        self.event = event
        self.context = context
        self.res_dict = {}
        logger.info("Event: %s" % self.event)
        logger.info("Context: %s" % self.context)
        try:
            session_client = boto3.session.Session()
            self.ssm_client = session_client.client('ssm')
            self.dl_table_name = event['SSMParametres']['dlTableName']
            # get relevant input params from event
            resource_properties = event['ResourceProperties']
            print(resource_properties)
            self.reason_data = ""
            self.request_type = event['RequestType']
            if resource_properties['Migration'] == "Yes":
                self.dl_for_new_account = resource_properties['dlForNewAccount']
            else:
                self.dl_for_new_account = event['dlForNewAccount']
            self.account_number = event['accountNumber']
            self.account_name = resource_properties['AccountName']
            self.completed_time_stamp = event['completedTimeStamp']
            self.workload_type = resource_properties['WorkloadType']
            session_client = boto3.Session()
            self.dd_client = session_client.client('dynamodb', region_name="us-east-1")
        except Exception as exception:
            self.reason_data = "Missing required property %s" % exception
            logger.error(self.reason_data)
            raise Exception(str(exception))

    def update_request_details(self):
        """
        The following method upddates the Account details table after account
        creation.
        """
        try:
            print("inside updateDLDetails")
            # Code to write new account details into dynamoDB
            item_list = {
                'AccountNumber': {"S": self.account_number},
                'AccountName': {"S": self.account_name},
                'DLEmailId': {"S": self.dl_for_new_account},
                'CreationDate': {"S": self.completed_time_stamp},
                'IsUsed': {"BOOL": True},
                'InProgress': {"BOOL": False}
            }
            if self.request_type == 'Update':
                print("Inside update dl flag")
                item_list.update(
                    {'UpdationDate': {"S": str(datetime.datetime.now().strftime('%d-%m-%Y'))}})
                print("UPDATE ITEM>>", item_list)

            elif self.request_type == 'Delete':
                print("Inside Delete dl flag")
                item_list.update(
                    {'DeletionDate': {"S": str(datetime.datetime.now().strftime('%d-%m-%Y'))}})
                print("Delete ITEM>>", item_list)

            else:
                print("It is a Create dl flag")
                print("Create ITEM>>", item_list)
            insert_response = self.dd_client.put_item(
                TableName=self.dl_table_name,
                Item=item_list
            )
            self.res_dict['update_request_details'] = 'PASSED'
            return self.res_dict
        except Exception as exception:
            self.reason_data = "DynamoDB DL update failed %s" % exception
            logger.error(self.reason_data)
            self.res_dict['return_val'] = False
            self.res_dict['update_request_details'] = 'FAILED'
            return self.res_dict


    def tag_newly_vended_account(self):
        """ Tag AWS@Shell Account based on workload Type (BC,Non BC) """
        try:
            print('Tagging new Account')
            if self.request_type == 'Create' or self.request_type == 'Update':
                print('tagging newly vended account', self.account_number)
                client = boto3.client('organizations')
                response = client.tag_resource(
                    ResourceId=self.account_number,
                    Tags=[
                        {
                            'Key': 'platform_workload',
                            'Value': self.workload_type
                        }
                    ]
                )

        except Exception as exception:
            logger.error('Error while adding tag to vended account', exception)


def lambda_handler(event, context):
    """
    This is the entry point of the module
    :param event:
    :param context:
    :return:
    """
    result_value = {}
    try:
        result_value.update(event)
        print("Received a {} Request".format(event['RequestType']))
        update_object = UpdateDLTable(event, context)
        output_value = update_object.update_request_details()
        print("Output of the function : " + str(output_value))
        print('Nothing to add in the output')
        result_value.update(output_value)
        result_value['UpdateDLTable'] = "PASSED"
        print("final response", json.dumps(result_value))
        update_object.tag_newly_vended_account()
        return result_value
    except Exception as exception:
        result_value['UpdateDLTable'] = "FAILED"
        result_value['Error'] = str(exception)
        print(result_value)
        return result_value