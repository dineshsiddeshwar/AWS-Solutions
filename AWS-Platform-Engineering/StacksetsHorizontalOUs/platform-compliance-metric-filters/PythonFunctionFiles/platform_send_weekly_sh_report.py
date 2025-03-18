import boto3
import os
import logging
from datetime import date

logger = logging.getLogger()
logger.setLevel(logging.INFO)

SINGLE_LINE_LENGTH = 100
DOUBLE_LINE_LENGTH = 100
HEADER_TEXT = 'Weekly Security Hub Report \n'
FOOTER_URL = 'https://console.aws.amazon.com/securityhub/home?region='


class SendWeeklySecurityHubReport(object):

    def __init__(self, event, context):
        try:
            self.event = event
            self.context = context
            logger.info("Event: %s" % self.event)
            logger.info("Context: %s" % self.context)
        except Exception as exception:
            logger.info('Exception during initialisation',exception)

    def add_horizontal_line(self, text_body, line_char, line_length):
        y = 0
        while y <= line_length:
            text_body += line_char
            y += 1
        text_body += '\n'

        return text_body

    def get_insight_results(self):
        snsBody = ''
        snsBody = self.add_horizontal_line(snsBody, '=', DOUBLE_LINE_LENGTH)
        snsBody = snsBody + HEADER_TEXT
        snsBody = self.add_horizontal_line(snsBody, '=', DOUBLE_LINE_LENGTH)
        snsBody += '\n'
        snsBody = self.add_horizontal_line(snsBody, '-', SINGLE_LINE_LENGTH)
        try:
            client = boto3.client('securityhub', region_name='us-east-1')
            response = client.get_insights()
            newBody = ""
            if len(response['Insights']) > 0:
                for insightArn in response['Insights']:
                    response = client.get_insight_results(InsightArn=insightArn['InsightArn'])
                    newBody = newBody + insightArn['Name']
                    newBody = newBody + '\n'
                    newBody = self.add_horizontal_line(newBody, '-', SINGLE_LINE_LENGTH)
                    newBody = newBody + '\n'
                    insightResults = response['InsightResults']['ResultValues']
                    if len(insightResults) == 0:
                        newBody = newBody + 'NO RESULTS \n'
                    else:
                        for result in insightResults:
                            newBody += result['GroupByAttributeValue'] + '-' + str(result['Count']) + '\n'
                    newBody = newBody + '\n'
                    insightLink = FOOTER_URL + 'us-east-1' + '#/insights/' + insightArn['InsightArn']
                    newBody = newBody + insightLink + '\n'
                    newBody = self.add_horizontal_line(newBody, '-', SINGLE_LINE_LENGTH)
                    newBody = newBody + '\n'
            else:
                newBody = newBody + 'No Insights found'
            return snsBody + newBody

        except Exception as exception:
            return exception

    def send_mail_to_custodian(self, region, accountId):
        try:
            sns_client = boto3.client('sns', region_name=region)
            sns_client.publish(
                TopicArn='arn:aws:sns:' + region + ':' + accountId + ':platform_Compliance_Security_Notification',
                Message=self.get_insight_results(),
                Subject="AWS@Shell Security Hub weekly report - " + str(date.today()))
        except Exception as excepton:
            print('Failed to send email to custodian', excepton)


def lambda_handler(event, context):
    """
        This is the entry point of the module
        :param event:
        :param context:
        :return:
    """
    try:
        weekly_report = SendWeeklySecurityHubReport(event,context)
        region = os.environ['AWS_REGION']
        print(region)
        aws_account_id = context.invoked_function_arn.split(":")[4]
        print(aws_account_id)
        #logger.info('Weekly report of the account', aws_account_id)
        weekly_report.send_mail_to_custodian(region, aws_account_id)
    except Exception as exception:
        reason_data = 'Error sending mail to custodian', exception
        logger.error(reason_data)
