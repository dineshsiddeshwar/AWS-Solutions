import boto3
import random

SESSION = boto3.session.Session()
STS_CLIENT = SESSION.client('sts')
BACKUP_VAULT_NAME = "platform_backupvault"
SNS_TOPIC_NAME = "platform_back_up_topic"

"""
This lambda Function is used to setup the back up vault in the business account
"""


class BackUpSetUp:
    def __init__(self, event, context):
        try:
            self.event = event
            self.context = context
            """
            Assume role into the child account
            """
            self.child_accountnumber = self.event['accountNumber']
            self.child_account_sessionname = "ChildAccountSession-" + str(random.randint(
                1, 100000))
            self.child_account_arn = "arn:aws:iam::{}:role/platform_service_inflation".format(
                self.child_accountnumber)
            child_account_role_creds = STS_CLIENT.assume_role(
                RoleArn=self.child_account_arn,
                RoleSessionName=self.child_account_sessionname)
            child_credentials = child_account_role_creds.get('Credentials')
            child_access_keyid = child_credentials.get('AccessKeyId')
            child_secret_access_key = child_credentials.get('SecretAccessKey')
            child_session_token = child_credentials.get('SessionToken')
            self.child_assume_role_session = boto3.Session(child_access_keyid,
                                                           child_secret_access_key,
                                                           child_session_token)
            ssm = boto3.client('ssm')
            if self.event['ResourceProperties']['AccountType'] == "public":
                region_list = event['SSMParametres']['whitelisted_regions_public'].split(",")
                print("regions list ",region_list)

            if self.event['ResourceProperties']['AccountType'] == "Data-Management":
                region_list = event['SSMParametres']['whitelisted_regions_public'].split(",")
                print("regions list ",region_list) 

            if self.event['ResourceProperties']['AccountType'] == "Migration":
                region_list = event['SSMParametres']['whitelisted_regions_public'].split(",")
                print("regions list ",region_list)
            
            if self.event['ResourceProperties']['AccountType'] == "private":
                region_list = event['SSMParametres']['whitelisted_regions_private'].split(",")
                print("regions list ",region_list)

            if self.event['ResourceProperties']['AccountType'] == "hybrid":
                region_list = event['SSMParametres']['whitelisted_regions_private'].split(",")
                print("regions list ",region_list)

            self.regions = region_list
        except Exception as e:
            raise Exception(str(e))

    """
    Create the back up vault
    """

    def create_back_up_vault(self):
        try:
            for region in self.regions:
                print(region)
                """Check if back up vault exists"""
                self.backup_client = self.child_assume_role_session.client('backup', region_name=region)

                back_up_vault_list = []
                while True:
                    response = self.backup_client.list_backup_vaults(MaxResults=100)
                    for item in response['BackupVaultList']:
                        back_up_vault_list.append(item['BackupVaultName'])
                    if 'NextToken' not in response:
                        break
                print(back_up_vault_list)
                """Create back up vault in each region"""
                if BACKUP_VAULT_NAME not in back_up_vault_list:
                    self.backup_client.create_backup_vault(
                        BackupVaultName=BACKUP_VAULT_NAME,
                        BackupVaultTags={
                            'platform_donotdelete': 'yes'
                        }
                    )
                topic_arn = self.create_sns_notification(region)
                self.setupsnsnotification(self.backup_client, topic_arn)
            return True
        except Exception as e:
            raise Exception(str(e))

    """Create a SNS topic add policy to this SNS topic to trust AWS Back up service"""

    def create_sns_notification(self, region):
        try:
            self.sns_client = self.child_assume_role_session.client('sns', region_name=region)
            sns_topic_arn_list = []
            while True:
                response = self.sns_client.list_topics()
                print("response", response)
                for item in response['Topics']:
                    sns_topic_arn_list.append(item['TopicArn'])
                if 'NextToken' not in response:
                    break
            print(sns_topic_arn_list)
            SNS_TOPIC_ARN = 'arn:aws:sns:' + region + ':' + self.child_accountnumber + ':' + SNS_TOPIC_NAME
            if SNS_TOPIC_ARN not in sns_topic_arn_list:
                """Create Topic and its Policy"""
                policy = """
                {
                      \"Version\": \"2008-10-17\",
                      \"Id\": \"__default_policy_ID\",
                      \"Statement\": [
                        {
                          \"Sid\": \"__default_statement_ID\",
                          \"Effect\": \"Allow\",
                          \"Principal\": {
                            \"AWS\": \"*\"
                          },
                          \"Action\": [
                            \"SNS:GetTopicAttributes\",
                            \"SNS:SetTopicAttributes\",
                            \"SNS:AddPermission\",
                            \"SNS:RemovePermission\",
                            \"SNS:DeleteTopic\",
                            \"SNS:Subscribe\",
                            \"SNS:ListSubscriptionsByTopic\",
                            \"SNS:Publish\",
                            \"SNS:Receive\"
                          ],
                          \"Resource\": \"arn:aws:sns:""" + region + """:""" + self.child_accountnumber + """:platform_back_up_topic\",
                          \"Condition\": {
                            \"StringEquals\": {
                              \"AWS:SourceOwner\": \"""" + self.child_accountnumber + """\"
                            }
                          }
                        },
                        {
                          \"Sid\": \"__console_pub_0\",
                          \"Effect\": \"Allow\",
                          \"Principal\": {
                            \"Service\": \"backup.amazonaws.com\"
                          },
                          \"Action\": \"SNS:Publish\",
                          \"Resource\": \"arn:aws:sns:""" + region + """:""" + self.child_accountnumber + """:platform_back_up_topic\"
                        }
                      ]
                    }
                """
                print(policy)
                response = self.sns_client.create_topic(
                    Name=SNS_TOPIC_NAME,
                    Tags=[
                        {
                            'Key': 'platform_donotdelete',
                            'Value': 'yes'
                        }
                    ],
                    Attributes={
                        "Policy": str(policy),
                        'KmsMasterKeyId': 'alias/aws/sns'
                    }
                )
                print(response)
                topic_arn = response['TopicArn']
            else:
                topic_arn = SNS_TOPIC_ARN
                response=self.sns_client.get_topic_attributes(TopicArn=topic_arn)
                res_dic=response['Attributes']
                kms_id='KmsMasterKeyId'
                if kms_id not in res_dic:
                    self.sns_client.set_topic_attributes(TopicArn=topic_arn,
                    AttributeName=kms_id,
                    AttributeValue='alias/aws/sns')
                    print('---Encrypted----')
            self.checksnssubscription(topic_arn)
            return topic_arn
        except Exception as exception:
            raise Exception(str(exception))

    def checksnssubscription(self, topic_arn):
        try:
            subscription_response = self.sns_client.list_subscriptions_by_topic(TopicArn=topic_arn)
            if subscription_response['Subscriptions']:
                print("Backup SNS Subscription already exist..!!", subscription_response['Subscriptions'])
            else:
                print("Empty subscription", subscription_response['Subscriptions'])
                self.createsnssubscription(topic_arn)
        except Exception as exception:
            raise Exception(str(exception))

    def createsnssubscription(self, topic_arn):
        try:
            create_response = self.sns_client.subscribe(
                TopicArn=topic_arn,
                Protocol='email',
                Endpoint=self.event['dlForNewAccount'],
                ReturnSubscriptionArn=True
            )
            print("Subscription created ", create_response)
        except Exception as exception:
            raise Exception(str(exception))

    """Set Up Back up valut Notification"""
    def setupsnsnotification(self, back_up_client, topic_arn):
        try:
            print(topic_arn)
            back_up_client.put_backup_vault_notifications(
                BackupVaultName=BACKUP_VAULT_NAME,
                SNSTopicArn=topic_arn,
                BackupVaultEvents=[ "BACKUP_JOB_FAILED" ])
            response = back_up_client.get_backup_vault_notifications(
                BackupVaultName=BACKUP_VAULT_NAME
            )
            print(response)
            return True
        except Exception as exception:
            raise Exception(str(exception))


def lambda_handler(event, context):
    try:
        print(event)
        back_up_object = BackUpSetUp(event, context)
        back_up_object.create_back_up_vault()
        event['back_up_status'] = True
        return event
    except Exception as e:
        print(str(e))
        event['back_up_status'] = False
        return event
