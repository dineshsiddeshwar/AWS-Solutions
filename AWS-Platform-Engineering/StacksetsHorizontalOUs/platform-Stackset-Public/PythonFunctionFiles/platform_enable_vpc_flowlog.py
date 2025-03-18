import boto3
import os
import logging
import time

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
LOGGER.addHandler(CH)


class EnableVPCFlowLogs:
    """
    # Class: Enable VPC Flow logs
    # Description: Includes method to enable VPC flow logs in Public if not enabled
    """

    def __init__(self, event, context):
        self.event = event
        self.context = context
        LOGGER.info("Event: %s" % self.event)
        LOGGER.info("Context: %s" % self.context)
        try:
            # get relevant input params from event
            session_client = boto3.Session()
            self.event = event['detail']
            self.response = self.event['responseElements']
            self.vpc_id = self.response['vpc']['vpcId']
            self.account_id = self.event['userIdentity']['accountId']
            self.region = self.event['awsRegion']
            self.vpc_flowlog_bucket = 'arn:aws:s3:::platform-da2-central-vpcflowlogs-' + os.environ['env']
            self.sns_topic_arn = 'arn:aws:sns:' + self.region + ':' + self.account_id + \
                                 ':platform_Compliance_Security_Notification'
            self.ec2_client = session_client.client('ec2')
            self.sns_client = session_client.client('sns')

        except Exception as exception:
            print(str(exception))
            LOGGER.error(str(exception))
            raise Exception(str(exception))

    def send_failure_email(self):
        try:
            sns_subject = 'ALERT: VPC Flow log failed to enable in Account ' + self.account_id
            sns_message = 'Hello Team,\n\n' \
                          'As per IRM guidelines, all VPCs should have flowlogs feature enabled and '\
                          'stream to AWS@Shell logging bucket.\n' \
                          'VPC Flow logs for VPC ' + self.vpc_id + ' failed to enable in region ' + self.region
            self.sns_client.publish(TopicArn=self.sns_topic_arn, Message=sns_message, Subject=sns_subject)
            print("VPC Flow log failed message sent successfully")
        except Exception as exception:
            print("Error occurred in send_failure_email", str(exception))

    def is_flowlog_enabled(self):
        try:
            vpc_fl_response = self.ec2_client.describe_flow_logs(
                Filter=[
                    {
                        'Name': 'resource-id',
                        'Values': [
                            self.vpc_id,
                        ]
                    },
                ],
            )
            print(vpc_fl_response)
            if len(vpc_fl_response['FlowLogs']) != 0:
                log_destination = vpc_fl_response['FlowLogs'][0]['LogDestinationType']
                print("Log destination Type: ", log_destination)
                if log_destination == 's3':
                    log_destination_bucket = vpc_fl_response['FlowLogs'][0]['LogDestination']
                    if log_destination_bucket == self.vpc_flowlog_bucket:
                        print(self.vpc_id + "has flowlog created")
                        return True
                    else:
                        print(self.vpc_id + " has flowlog enabled but not published to platform bucket")
                        return False
                else:
                    print(self.vpc_id + " has flowlog enabled but published to cloudwatch logs")
                    return False
            else:
                print(self.vpc_id + " doesn't have flowlog enabled")
                return False
        except Exception as exception:
            print("Error occurred while is_flowlog_enabled: {}".format(exception))

    def enable_vpc_flowlog(self):
        try:
            # Wait condition for vpc to come to available state
            time.sleep(10)
            self.ec2_client.create_flow_logs(
                ResourceIds=[self.vpc_id],
                ResourceType='VPC',
                TrafficType='ALL',
                LogDestinationType='s3',
                LogDestination=self.vpc_flowlog_bucket,
                TagSpecifications=[
                    {
                        'ResourceType': 'vpc-flow-log',
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': 'platform-Flowlogs'
                            },
                            {
                                'Key': 'platform_donotdelete',
                                'Value': 'yes'
                            }
                        ]
                    },
                ]
            )
            if self.is_flowlog_enabled():
                print("VPC Flow Logs created successfully")
            else:
                print("VPC Flow Logs creation failed")
                self.send_failure_email()
        except Exception as exception:
            print(str(exception))
            LOGGER.error(str(exception))


def lambda_handler(event, context):
    try:
        enable_flow_log = EnableVPCFlowLogs(event, context)
        enable_flow_log.enable_vpc_flowlog()
    except Exception as exception:
        print("Error in fwlog lambda_handler: ", exception)
