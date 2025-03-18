import random
import boto3
import json
import sys

class SetupSNSTopic(object):

    def __init__(self, event):
        self.event = event
        try:
            session_client = boto3.Session()
            self.sts_client = session_client.client('sts')
            self.table_name = event['SSMParameters']['accountDetailTableName']
            self.account_number = event['ProvisionedProduct']['AccountNumber']
            self.regions_str = event['SSMParameters']['whitelisted_regions_private'] if "Private" in event['ProvisionedProduct']['OU'] or "Hybrid" in event['ProvisionedProduct']['OU'] else event['SSMParameters']['whitelisted_regions_public']
            self.regions = self.regions_str.split(',')
            print("Regions allowed", self.regions)
            self.email_list = []
            self.account_delivery_ls = event['RequestEventData']['SupportDL']
            self.platform_delivery_ls = 'GX-SITI-CPE-Team-Titan@shell.com'
            self.email_list.append(self.platform_delivery_ls)
            self.email_list.append(self.account_delivery_ls)
            self.child_account_role_arn = "arn:aws:iam::{}:role/AWSControlTowerExecution".format(self.account_number)
            self.child_account_session_name = "childAccountSession-"+str(random.randint(1, 100000))
            self.child_account_role = self.sts_client.assume_role(RoleArn=self.child_account_role_arn, RoleSessionName=self.child_account_session_name)
            self.child_credentials = self.child_account_role.get('Credentials')
            self.child_access_key = self.child_credentials.get('AccessKeyId')
            self.child_secret_access_key = self.child_credentials.get('SecretAccessKey')
            self.child_session_token = self.child_credentials.get('SessionToken')
            self.child_assume_role_session = boto3.Session(self.child_access_key, self.child_secret_access_key, self.child_session_token)
        except Exception as exception:
            print("Missing required property %s" % exception)

    def get_sns_topic(self):
        """
        Create SNS Topic in the child account.
        """
        for region in self.regions:
            print('Inside Region - {}'.format(region))
            topic_arn = 'arn:aws:sns:' + region + ':' + self.account_number + ':platform_Compliance_Security_Notification'
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
                    return False
        return True

    def update_sns_topic(self, topic_arn, sns_client):
        """
        Update SNS Topic in the child account.
        """
        print('Update SNS Topic function')
        response = sns_client.list_subscriptions_by_topic(TopicArn=topic_arn)
        print('Subscription List - {}'.format(response))
        email_list = list(set(self.email_list.copy()))
        if response['Subscriptions'] != 0:
            for subscription in response['Subscriptions']:
                if len(self.email_list) != 0 and subscription['Endpoint'] in email_list:
                    email_list.remove(subscription['Endpoint'])
                elif len(self.email_list) != 0 and subscription['Endpoint'] not in email_list:
                    sns_client.unsubscribe( SubscriptionArn=subscription['SubscriptionArn'])
        if len(email_list) != 0:
            for email_id in email_list:
                subscribe_response = sns_client.subscribe(
                    TopicArn=topic_arn,
                    Protocol='email',
                    Endpoint=email_id,
                    ReturnSubscriptionArn=True
                )
                print('Subscription_Arn is - {}'.format(subscribe_response['SubscriptionArn']))

try:
    local_file_path = str(sys.argv[1])+"parameters.json"
    print("Parameters local file path: ", local_file_path)
    with open(local_file_path) as json_data:
        parameters_data = json.load(json_data)
    print(parameters_data)
    if parameters_data : 
        print("parameters are loaded in json format, invokes tag_eks_ami_account function..")
        SNSObject = SetupSNSTopic(parameters_data)
        if SNSObject.get_sns_topic():
            print("Invoke subscribe to SNS topic is success..!!")
        else:
            print("Invoke subscribe to SNS topic is fialed..!!")
except Exception as ex:
    print("There is an error %s", str(ex))