"""
This module is used Send Notifications for Security Hub Findings and
non complaint activities
"""

import logging
import boto3

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
LOGGER.addHandler(CH)


class SendNotification:
    """
    # Class: Get Findings from Security Hub and Invoke
    # Description: Includes method to Get Findings from Security Hub and invoke
      the respective Child Lambda
    """

    def __init__(self, event, context):
        self.event = event
        self.context = context
        LOGGER.info("Event: %s" % self.event)
        LOGGER.info("Context: %s" % self.context)
        try:
            # get relevant input params from event

            self.reason_data = ""
            session_client = boto3.Session()

            self.res_dict = {}
            self.event_data = event
            self.account_id = self.event_data['account']
            self.region = self.event_data['region']
            self.resources = self.event_data['resources'][0]
            self.finding_resources = self.event_data['detail']['findings'][0]['Resources']
            self.sns_topic_arn = 'arn:aws:sns:'+self.region+':' + self.account_id + \
                                 ':platform_Compliance_Security_Notification'
            self.sns_client = session_client.client('sns', region_name=self.region)
            print(self.sns_topic_arn)
            print(self.event_data)
            print(self.resources)

        except Exception as exception:
            self.reason_data = "Missing required property %s" % exception
            LOGGER.error(self.reason_data)

    def send_notification(self):
        """
        Send Notification Lambda.
        """
        try:
            if 'cis-aws-foundations-benchmark/v/1.2.0/1.2/' in self.resources and \
                    self.finding_resources[0]['Type'] != 'AwsAccount':
                user_arn = self.finding_resources[0]['Id']
                sns_subject = 'Security Threat - IAM User without MFA'
                sns_message = 'Hello User, \n' \
                              'You have configured an IAM User with the arn - "' + user_arn + '" in the region - ' \
                              + self.region + ', without enabling MFA in the account - ' + self.account_id + ' . \n' \
                              'As per Shell IRM Compliance, ' \
                              'IAM User that have a password should be configured with MFA. \n' \
                              'If you have any queries, Please raise a ServiceNow case to the queue ' \
                              '- Cloud Hosting Services. \n'
                print(sns_message)
                send_response = self.sns_client.publish(TopicArn=self.sns_topic_arn,
                                                        Message=sns_message,
                                                        Subject=sns_subject)
                self.res_dict['Message_Id'] = send_response['MessageId']
            elif 'cis-aws-foundations-benchmark/v/1.2.0/1.4/' in self.resources and \
                    self.finding_resources[0]['Type'] != 'AwsAccount':
                user_arn = self.finding_resources[0]['Id']
                sns_subject = 'Security Threat - Access keys are not rotated'
                sns_message = 'Hello User, \n' \
                              'You have configured Access Keys for user with arn - "' + user_arn + '" in the region'\
                              + self.region + ' and the keys are not rotated for 90 days or more in the account - ' \
                              + self.account_id + ' . \nAs per Shell IRM Compliance, ' \
                              'Access Key should be rotated every 90 days . \n' \
                              'Please raise a ServiceNow case to the queue - Cloud Hosting Services to ' \
                              'rotate the keys for the IAM user. \n'
                print(sns_message)
                send_response = self.sns_client.publish(TopicArn=self.sns_topic_arn,
                                                        Message=sns_message,
                                                        Subject=sns_subject)
                self.res_dict['Message_Id'] = send_response['MessageId']
            elif 'cis-aws-foundations-benchmark/v/1.2.0/1.22/' in self.resources and \
                    self.finding_resources[0]['Type'] != 'AwsAccount':
                policy_arn = self.finding_resources[0]['Id']
                sns_subject = 'Security Threat - IAM Policies created with full "*:*" administrative privileges'
                sns_message = 'Hello User, \n' \
                              'You have configured IAM Policies in the region - ' + self.region + ' with full "*:*" '\
                              'administrative privileges and this is the policy arn - "' + policy_arn + '" in the ' \
                              'account - ' + self.account_id + ' . \nAs per Shell IRM Compliance, ' \
                              'IAM Policies should not be created with full "*:*" administrative privileges. \n' \
                              'Please refer the "QRG_Best Practices for Whitelisted Services" ' \
                              'to follow best practices for IAM Policies. \n' \
                              'If you have any queries, Please raise a ServiceNow case to the queue - ' \
                              'Cloud Hosting Services. \n'
                print(sns_message)
                send_response = self.sns_client.publish(TopicArn=self.sns_topic_arn,
                                                        Message=sns_message,
                                                        Subject=sns_subject)
                self.res_dict['Message_Id'] = send_response['MessageId']
            elif 'cis-aws-foundations-benchmark/v/1.2.0/2.8/' in self.resources and \
                    self.finding_resources[0]['Type'] != 'AwsAccount':
                key_arn = self.finding_resources[0]['Id']
                sns_subject = 'Security Threat - CMK Rotation is not Enabled'
                sns_message = 'Hello User, \n' \
                              'You have configured Customer Managed Keys in the region - ' + self.region + ' without '\
                              'enabling auto rotation feature and this is the arn of the key - "' + key_arn + '" in' \
                              ' the account - ' + self.account_id + ' . \nAs per Shell IRM Compliance, ' \
                              'Customer Managed Keys should be created with auto rotate feature enabled. \n' \
                              'Please refer the "QRG_Best Practices for Whitelisted Services" ' \
                              'to follow best practices for Managing Custom Keys. \n' \
                              'If you have any queries, Please raise a ServiceNow case to the queue - ' \
                              'Cloud Hosting Services. \n'
                print(sns_message)
                send_response = self.sns_client.publish(TopicArn=self.sns_topic_arn,
                                                        Message=sns_message,
                                                        Subject=sns_subject)
                self.res_dict['Message_Id'] = send_response['MessageId']
            elif 'cis-aws-foundations-benchmark/v/1.2.0/4.3/' in self.resources and \
                    self.finding_resources[0]['Type'] != 'AwsAccount':
                sg_id = self.finding_resources[0]['Details']['AwsEc2SecurityGroup']['GroupId']
                sns_subject = 'Security Threat - Default Security Group is not restricting all traffic'
                sns_message = 'Hello User, \n' \
                              'You have a default security group not restricting all traffic' \
                              ' and this is the security group id - "' + sg_id + '" in ' + self.region + ' region' \
                              ' in the account - ' + self.account_id + ' . \nAs per Shell IRM Compliance, ' \
                              'Default Security Groups should restrict all the traffic. \n' \
                              'Please refer the "QRG_Best Practices for Whitelisted Services" ' \
                              'to follow best practices for Security Group. \n' \
                              'If you have any queries, Please raise a ServiceNow case to the queue - ' \
                              'Cloud Hosting Services. \n'
                print(sns_message)
                send_response = self.sns_client.publish(TopicArn=self.sns_topic_arn,
                                                        Message=sns_message,
                                                        Subject=sns_subject)
                self.res_dict['MessageId'] = send_response['MessageId']
            self.res_dict['Send Notification'] = 'PASSED'
        except Exception as exception:
            print("ERROR Send Notification", exception)
            self.reason_data = "Send Notification Lambda - %s" % exception
            self.res_dict['Send Notification'] = 'FAILED'
            LOGGER.error(self.reason_data)
            return self.res_dict
        return self.res_dict


def lambda_handler(event, context):
    """
    Lambda handler that calls the function to send notification
    """
    result_value = {}
    try:
        sec_hub_obj = SendNotification(event, context)
        output_value = sec_hub_obj.send_notification()
        print("Output of the function : " + str(output_value))
        result_value.update(output_value)
        return result_value

    except Exception as exception:
        print("Error in Lambda Handler", exception)
        result_value['Handler Exception'] = str(exception)
        return exception
