import json
import logging
import json
import boto3
from datetime import datetime
from botocore.exceptions import ClientError
import base64
import gzip

logger = logging.getLogger()
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

class SubscriptionFilter(object):
    """
    # Class: Alarm Notification
    # Description: Accepts cloudwatch log streams based on filter patterns and sends email notification.
    """
    def __init__(self, event, context):
        self.event = event
        self.context = context
        logger.info("Event: %s" % self.event)
        logger.info("Context: %s" % self.context)
    
    def get_event_attributes(self):
        try:
            logger.info("Getting required event details to send the alarm notification")
            data = gzip.decompress(base64.b64decode(self.event['awslogs']['data']))
            self.data = json.loads(data)
            self.loggroup = self.data["logGroup"]
            self.logstream = self.data["logStream"]
            self.logeventid = self.data["logEvents"][0]["id"]
            self.message = json.loads(self.data["logEvents"][0]["message"])
            logger.info("LogEvent -> {}".format(self.message))
            self.account_id = self.message["recipientAccountId"]
            self.region = self.message["awsRegion"]
            self.eventtime = self.message["eventTime"]
            self.eventname = self.message["eventName"]
            self.eventsource = self.message["eventSource"]
            self.eventtype = self.message["eventType"]
            #Getting Account Type
            self.account_table_name = self.get_operations_dl('accountDetailTableName') 
            self.dynamodb_client = boto3.client("dynamodb")
            table = self.dynamodb_client.scan(TableName=self.account_table_name)
            self.account_type = ''
            for item in table['Items']:
                if self.account_id == item['AccountNumber']['S']:
                    self.account_type = item['Organization']['S']
            self.alert_operations()
        except Exception as ex:
           logger.error("Encountered error while getting event details".format(ex))

    def get_operations_dl(self,parameter_name):
        try:
            logger.info("Getting operations team dl")
            self.ssm_client = boto3.client("ssm")
            parameter = self.ssm_client.get_parameter(Name=parameter_name,WithDecryption=True)
            if parameter:
                return parameter['Parameter']['Value']        
        except Exception as ex:
            logger.error("Encountered error while getting operations team dl".format(ex))

    def alert_operations(self):
        try:
            self.ses_client = boto3.client('ses')
            failure_operation_dl_str = self.get_operations_dl("failure_operation_dl")
            sender_id = self.get_operations_dl("sender_id")
            # The email body for recipients with non-HTML email clients.
            body_text = """
                Hello There!,
                
                You are receiving this email because Amazon CloudWatch Logs found an activity that may be the cause of concern.          
                    * Account Number : """ + self.account_id + """
                    * Region : """ + self.region + """
                    * Account Type : """ + self.account_type + """
                    * EventTime : """ + self.eventtime + """
                    * EventName : """ + self.eventname + """
                    * EventSource : """ + self.eventsource + """
                    * EventType : """ + self.eventtype + """
                    * LogGroup : """ + self.loggroup + """
                    * LogStream : """ + self.logstream + """
                    * LogEventId : """ + self.logeventid + """
                To know more about event details check CloudWatch Logs.
                
                Best Regards,
                AWS Platform Engineering Team.
                """

            # The HTML body of the email.
            body_html = """<html>
                <head>
                <style>
                    table, td {
                    border: 1px solid black;
                    border-collapse: collapse;
                    }
                    
                    
                    th {
                    border: 1px solid black;
                    border-collapse: collapse;
                    font-weight: bold
                    }
                    
                    
                    td, th {
                    padding-left: 15px;
                    text-align: left;
                    }
                </style>
                </head>
                <body>
                <p style="font-family:'Futura Medium'">Hello There!,</p>
                <p style="font-family:'Futura Medium'">You are receiving this email because Amazon CloudWatch Logs found an activity that may be the cause of concern.</p>
                
                <table style="width:100%">
                    <col style="width:50%">
                    <col style="width:50%">
                  <tr bgcolor="yellow">
                    <td width="50%">Event Property Names</td>
                    <td width="50%">Values</td>
                  </tr>
                  <tr>
                    <td width="50%">Account Number</td>
                    <td width="50%">""" + self.account_id + """</td>
                  </tr>
                  <tr>
                    <td width="50%">Region</td>
                    <td width="50%">""" + self.region + """</td>
                  </tr>
                  <tr>
                    <td width="50%">Account Type</td>
                    <td width="50%">""" + self.account_type + """</td>
                  </tr>                  
                  <tr>
                    <td width="50%">EventTime </td>
                    <td width="50%">""" + self.eventtime  + """</td>
                  </tr>
                  <tr>
                    <td width="50%">EventName </td>
                    <td width="50%">""" + self.eventname  + """</td>
                  </tr>
                  <tr>
                    <td width="50%">EventSource </td>
                    <td width="50%">""" + self.eventsource  + """</td>
                  </tr>
                  <tr>
                    <td width="50%">EventType </td>
                    <td width="50%">""" + self.eventtype  + """</td>
                  </tr>
                  <tr>
                    <td width="50%">LogGroup</td>
                    <td width="50%">""" + self.loggroup + """</td>
                  </tr>
                  <tr>
                    <td width="50%">LogStream</td>
                    <td width="50%">""" + self.logstream + """</td>
                  </tr>
                  <tr>
                    <td width="50%">LogEventId</td>
                    <td width="50%">""" + self.logeventid + """</td>
                  </tr>
                 </table>

                <p style="font-family:'Futura Medium'">For more information check the Cloud Watch Logs details are given above.</p>
                <p style="font-family:'Futura Medium'">Check the resources related to this event in the respective child accounts.</p>                
                <p style="font-family:'Futura Medium'">Best Regards,</p>
                <p style="font-family:'Futura Medium'">AWS Platform Engineering Team.</p>
                </body>
                </html>
                """
            # Provide the contents of the email.
            send_mail_response = self.ses_client.send_email(
                Source= sender_id,
                Destination={
                    'ToAddresses': [failure_operation_dl_str]
                },
                Message={
                    'Subject': {
                        'Data': 'ALARM: Platform API Activity Notification In '+self.region+' ,'+self.account_id
                    },
                    'Body': {
                        'Text': {
                            'Data': body_text
                        },
                        'Html': {
                            'Data': body_html
                        }
                    }
                }
            )
            logger.info(send_mail_response)
            return send_mail_response
        except Exception as e:
            logger.error(str(e))
            return str(e)
             
def lambda_handler(event, context):
    """
    Lambda handler calls the SubscriptionFilter class to send Alarm notifications
    """
    print('event ' + str(event))
    try:
        Subscription_Filter = SubscriptionFilter(event, context)
        output = Subscription_Filter.get_event_attributes()
        return output
    except Exception as exception:
        logger.error(str(exception))
        return str(exception)
