"""
This module is used to Setup SNS Topic in the child account.
"""
import random
import logging
import boto3
import time

LOGGER = logging.getLogger('logging')
LOGGER.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
LOGGER.addHandler(CH)


class SetupSNSTopic:
    """
    # Class: Setup SNS Topic
    # Description: Includes method to Setup SNS Topic in the child account
    """

    def __init__(self, event, context):
        self.event = event
        self.context = context
        LOGGER.info("Event: %s" % self.event)
        LOGGER.info("Context: %s" % self.context)
        try:
            # get relevant input params from event
            session_client = boto3.Session()
            self.reason_data = ""
            self.sts_client = session_client.client('sts')
            self.db_client = session_client.client('dynamodb')
            ssm_client = session_client.client('ssm')
            self.table_name = event['SSMParametres']['accountDetailTableName']
            self.account_number = event['accountNumber']
            self.region = event['whitelisted_regions']
            get_response = self.db_client.get_item(
                TableName=self.table_name,
                Key={'AccountNumber': {'S': self.account_number}},
                ConsistentRead=True
            )
            self.res_dict = {'Enable Analyzer Child': event['Enable Analyzer Child'],
                             'Enable EMR Block Public': event['Enable EMR Block Public'],
                             'Public Access Block Configuration': event['Public Access Block Configuration'],
                             'Enable EBS Encryption': event['Enable EBS Encryption']
                             }
            self.email_list = []
            self.account_delivery_ls = get_response['Item']['DLUsed']['S']
            self.platform_delivery_ls = 'GXSOMWIPROCLOUDAWSDA2-Operations@shell.com'

            self.email_list.append(self.platform_delivery_ls)
            self.email_list.append(self.account_delivery_ls)
            self.child_account_role_arn = "arn:aws:iam::{}:role/platform_service_inflation". \
                format(self.account_number)
            self.child_account_session_name = "childAccountSession-" + \
                                              str(random.randint(1, 100000))
            self.child_account_role = self.sts_client.assume_role(
                RoleArn=self.child_account_role_arn,
                RoleSessionName=self.child_account_session_name)
            self.child_credentials = self.child_account_role.get('Credentials')
            self.child_access_key = self.child_credentials.get('AccessKeyId')
            self.child_secret_access_key = self.child_credentials.get('SecretAccessKey')
            self.child_session_token = self.child_credentials.get('SessionToken')
            self.child_assume_role_session = boto3.Session(
                self.child_access_key,
                self.child_secret_access_key,
                self.child_session_token)

        except Exception as exception:
            self.reason_data = "Missing required property %s" % exception
            LOGGER.error(self.reason_data)

    def get_sns_topic(self):
        """
        Create SNS Topic in the child account.
        """
        # Adding Sleep time for Stackset to create topic
        time.sleep(180)
        for region in self.region:
            print('Inside Region - {}'.format(region))
            topic_arn = 'arn:aws:sns:' + region + ':' + self.account_number + \
                        ':platform_Compliance_Security_Notification'
            sns_client = self.child_assume_role_session.client('sns', region_name=region)
            try:
                print('Get SNS Topic')
                sns_client.get_topic_attributes(TopicArn=topic_arn)
                self.update_sns_topic(topic_arn, sns_client)

            except Exception as error:
                try:
                    print('Invoke Update Topic Function - {}'.format(str(error)))
                    self.update_sns_topic(topic_arn, sns_client)
                except Exception as exception:
                    print("ERROR Checking SNS Topic", exception)
                    self.reason_data = "SNS Topic Status %s" % exception
                    LOGGER.error(self.reason_data)
                    self.res_dict['Update SNS Topic'] = 'FAILED'
                    return self.res_dict
        return self.res_dict

    def update_sns_topic(self, topic_arn, sns_client):
        """
        Update SNS Topic in the child account.
        """
        print('Update SNS Topic function')
        response = sns_client.list_subscriptions_by_topic(TopicArn=topic_arn)
        print('Subscription List - {}'.format(response))
        email_list = self.email_list.copy()
        if response['Subscriptions'] != 0:
            for subscription in response['Subscriptions']:
                if len(self.email_list) != 0 and subscription['Endpoint'] in email_list:
                    email_list.remove(subscription['Endpoint'])
                elif len(self.email_list) != 0 and subscription['Endpoint'] not in email_list:
                    sns_client.unsubscribe(
                        SubscriptionArn=subscription['SubscriptionArn']
                    )
        if len(email_list) != 0:
            for email_id in email_list:
                subscribe_response = sns_client.subscribe(
                    TopicArn=topic_arn,
                    Protocol='email',
                    Endpoint=email_id,
                    ReturnSubscriptionArn=True
                )
                print('Subscription_Arn is - {}'.format(subscribe_response['SubscriptionArn']))
        self.res_dict['Update SNS Topic'] = 'PASSED'


def lambda_handler(event, context):
    """"
    Lambda handler that calls the function to Setup SNS Topic
    """
    result_value = {}
    try:
        setup_sns_topic_obj = SetupSNSTopic(event, context)
        output_value = setup_sns_topic_obj.get_sns_topic()
        print("Output of the function : " + str(output_value))
        result_value.update(output_value)
        return result_value

    except Exception as exception:
        print("Error in Lambda Handler", exception)
        result_value['Handler Exception'] = str(exception)
        return result_value
