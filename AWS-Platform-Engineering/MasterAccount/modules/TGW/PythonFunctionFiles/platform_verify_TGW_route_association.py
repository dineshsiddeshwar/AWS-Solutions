import boto3
import logging
import time
import json
import random

logger = logging.getLogger()
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

child_account_role_session_name = "ChildAccountSession-" + str(random.randint(1, 100000))
SUCCESS = "SUCCESS"
FAILED = "FAILED"
PASSED = "PASSED"
PENDING = "PENDING"
class TGWAttachment(object):
    """
    # Class: VerifyTGWAssociation
    # Description: Verify TGW Association in the child account
    """

    def __init__(self, event, context):
        self.event = event
        self.context = context
        logger.info("Event: %s" % self.event)
        logger.info("Context: %s" % self.context)
        self.result = {'vpc_tgw_association': {}}
        self.res_dict = {}
        try: 
            #Getting input paramteres
            
            logger.info("Getting relevant input params from event")
            self.account_id = self.event['ResourceProperties']['AccountNumber']
            self.regions = list([item for item in self.event['region_ip_dict'].keys()])
            self.payer_account = self.event['ResourceProperties']['AWSAccountId']            
            self.tgw_details = self.event['tgw']
 
            logger.info("Creating Session and AWS Service Clients")
            session = boto3.session.Session()
            sts_client = session.client('sts')
            child_account_role_arn = "arn:aws:iam::" + self.account_id + ":role/AWSControlTowerExecution"
            child_account_role_creds = sts_client.assume_role(RoleArn=child_account_role_arn,
                                                              RoleSessionName=child_account_role_session_name)
            credentials = child_account_role_creds.get('Credentials')
            accessKeyID = credentials.get('AccessKeyId')
            secretAccessKey = credentials.get('SecretAccessKey')
            sessionToken = credentials.get('SessionToken')
            self.assumeRoleSession = boto3.session.Session(accessKeyID, secretAccessKey, sessionToken)

        except Exception as ex:
            logger.error("Encountered error while getting input parameters".format(ex)) 
            self.result.update({'verify_vpc_tgw_association' : FAILED})
            
 
    def Verify_TGW_attahment_Association(self):     
        """
        # Takes request body
        # return: resource share status
        """
        try:
            for region in self.regions:
                #Defining/Getting required parameters
                self.region = region
                self.res_dict = {self.region : {}}
                self.vpc_id = self.tgw_details[region]['vpc_id']
                self.verify_association()
            return self.result
        except Exception as exception:
            logger.error(str(exception))        
            self.result.update({'verify_vpc_tgw_association' : FAILED})
            return self.result

        
    def verify_association(self):
        try:
            self.tgw_id = self.tgw_details[self.region]['TransitGatewayId']
            self.tgw_attach_id = self.tgw_details[self.region]['tgw_attachment_id']
            if self.tgw_id and self.tgw_attach_id:           
                #Verifying if transitgateway attachment is associated?
                self.child_account_ec2_client = self.assumeRoleSession.client('ec2',region_name=self.region)
                tgw_id_response = self.child_account_ec2_client.describe_transit_gateway_attachments()
                logger.info(tgw_id_response)
                if len(tgw_id_response['TransitGatewayAttachments']) > 0:
                    for item in tgw_id_response['TransitGatewayAttachments']:
                        if item['TransitGatewayAttachmentId'] == self.tgw_attach_id:
                            if item['Association']['State'] == 'associated':
                                logger.info("Attachment {} for transitgateway {} is associated".format(item['TransitGatewayAttachmentId'],self.tgw_id))
                                self.res_dict[self.region].update({'status' : SUCCESS})
                                self.update_result()
                            elif item['Association']['State'] == 'associating':
                                logger.info("Attachment {} for transitgateway {} is in pending state".format(item['TransitGatewayAttachmentId'],self.tgw_id))
                                self.res_dict[self.region].update({'status' : PENDING})
                                self.update_result()
                            else:
                                logger.info("Attachment {} for transitgateway {} is in {} state".format(item['TransitGatewayAttachmentId'],self.tgw_id,item['Association']['State']))
                                self.res_dict[self.region].update({'status' : FAILED})
                                self.update_result()
            return self.result
        except Exception as exception:
            logger.error(str(exception)) 
            self.res_dict[self.region].update({'status' : FAILED})
            self.update_result()
            return self.result      


    def update_result(self):
        try:
            if self.region == 'us-east-1':
                self.result['vpc_tgw_association'].update({'us-east-1': self.res_dict[self.region]})
            elif self.region == 'eu-west-1':
                self.result['vpc_tgw_association'].update({'eu-west-1':self.res_dict[self.region]})
            elif self.region == 'ap-southeast-1':
                self.result['vpc_tgw_association'].update({'ap-southeast-1':self.res_dict[self.region]})
            return self.result
        except Exception as exception:
            logger.error(str(exception))
            self.result.update({'vpc_tgw_association_update_result' : FAILED})
            return self.result 


    def get_ssm_param(self,parameter_name):
        """
        param: parametre_name
        return: parameter value for the given param name
        """
        try:
            self.ssm_client = boto3.client("ssm")
            parameter = self.ssm_client.get_parameter(Name=parameter_name,WithDecryption=True)
            if parameter:
                return parameter['Parameter']['Value']
        except Exception as ex:
            logger.error("Encountered error while getting parameters".format(ex)) 
            self.result.update({'vpc_tgw_association_get_parameter' : FAILED})
            return self.result

            
    def alert_operations(self):
        try:
            for region in self.regions:
                for key,value in self.event['tgw_resource_share_request_api'].items():
                    if key == region:
                        self.resource_share = value['status']
                for key,value in self.event['accept_tgw_resource_share'].items():
                    if key == region:
                        self.accept_resource_share = value['status'] 
                for key,value in self.event['tgw'].items():
                    if key == region:
                        self.create_tgw_attachment = value['create_tgw_attachment'] 
                for key,value in self.event['tgw_accept_api'].items():
                    if key == region:
                        self.accept_tgw_attachment = value['status'] 
                for key,value in self.event['vpc_tgw_route'].items():
                    if key == region:
                        self.vpc_tgw_route = value['vpc_tgw_route_configure'] 
                for key,value in self.result['vpc_tgw_association'].items():
                    if key == region:
                        self.vpc_tgw_association = value['status'] 
                
                self.ses_client = boto3.client('ses')
                logger.info("Sending email now in {}".format(region))
                failure_operation_dl_str = self.get_ssm_param("failure_operation_dl")
                sender_id = self.get_ssm_param("sender_id")
                # The email body for recipients with non-HTML email clients.
                body_text = """
                    Hello Team,
                    
                    Transitgateway integration is processed now. Below are the processed details and results.          
                        * Account Number : """ + self.event['ResourceProperties']['AccountNumber'] + """
                        * Account Name : """ + self.event['response_data']['AccountName'] + """
                        * Account Type : """ + self.event['tgw']['account_type'] + """
                        * Environment : """ + self.event['tgw']['environment'] + """
                        * Request Id : """ + self.event['ResourceProperties']['RequestNo'] + """
                        * Region : """ + region + """
                        * VPC Id : """ + self.event['tgw'][region]['vpc_id'] + """
                        * TransitGatewayId : """ + self.event['tgw'][region]['TransitGatewayId'] + """
                        * Resource Share Request : """ + self.resource_share + """
                        * Accept Shared Resource Share : """ + self.accept_resource_share + """
                        * Create Transitgateway attachment : """ + self.create_tgw_attachment + """
                        * Accept Transitgateway attachment : """ + self.accept_tgw_attachment  + """                    
                        * Configure VPC to Transitgateway Route : """ + self.vpc_tgw_route + """                    
                        * Transigateway Association : """ + self.vpc_tgw_association + """ 
    
                    In case of account request processing status like failure or error, please check the Step Function execution and Cloud Watch Logs.
                    
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
                    <p style="font-family:'Futura Medium'">Hello Team,</p>
                    <p style="font-family:'Futura Medium'">Transitgateway integration is processed now. Below are the processed details and results.</p>
                    
                    <table style="width:100%">
                        <col style="width:50%">
                        <col style="width:50%">
                      <tr bgcolor="yellow">
                        <td width="50%">Account Property Names</td>
                        <td width="50%">Values</td>
                      </tr>
                      <tr>
                        <td width="50%">Account Number</td>
                        <td width="50%">""" + self.event['ResourceProperties']['AccountNumber'] + """</td>
                      </tr>
                      <tr>
                        <td width="50%">Account Name</td>
                        <td width="50%">""" + self.event['response_data']['AccountName'] + """</td>
                      </tr>
                      <tr>
                        <td width="50%">Account Type</td>
                        <td width="50%">""" + self.event['tgw']['account_type'] + """</td>
                      </tr>
                      <tr>
                        <td width="50%">Environment</td>
                        <td width="50%">""" + self.event['tgw']['environment'] + """</td>
                      </tr>
                      <tr>
                        <td width="50%">Request Id</td>
                        <td width="50%">""" + self.event['ResourceProperties']['RequestNo'] + """</td>
                      </tr>
                      <tr>
                        <td width="50%">Region</td>
                        <td width="50%">""" + region + """</td>
                      </tr>
                      <tr>
                        <td width="50%">VPC Id</td>
                        <td width="50%">""" + self.event['tgw'][region]['vpc_id'] + """</td>
                      </tr>
                      <tr>
                        <td width="50%">TransitGatewayId</td>
                        <td width="50%">""" + self.event['tgw'][region]['TransitGatewayId'] + """</td>
                      </tr>
                      <tr>
                        <td width="50%">Resource Share Request</td>
                        <td width="50%">""" + self.resource_share + """</td>
                      </tr>
                      <tr>
                        <td width="50%">Accept Shared Resource Share</td>
                        <td width="50%">""" + self.accept_resource_share + """</td>
                      </tr>
                      <tr>
                        <td width="50%">Create Transitgateway attachment</td>
                        <td width="50%">""" + self.create_tgw_attachment + """</td>
                      </tr>
                      <tr>
                        <td width="50%">Accept Transitgateway attachment</td>
                        <td width="50%">""" + self.accept_tgw_attachment + """</td>
                      </tr>
                      <tr>
                        <td width="50%">Configure VPC to Transitgateway Route</td>
                        <td width="50%">""" + self.vpc_tgw_route + """</td>
                      </tr>
                      <tr>
                        <td width="50%">Transigateway Association</td>
                        <td width="50%">""" + self.vpc_tgw_association + """</td>
                      </tr>
                    </table>
    
                    <p style="font-family:'Futura Medium'">In case of account request processing status like failure or error, please check the Step Function execution and Cloud Watch Logs</p>
                    
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
                            'Data': self.event['ResourceProperties']['RequestNo']+': VPC TGW Association Status'
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
            print(str(e))
            return str(e)
    
    
def lambda_handler(event, context):
    """
    Lambda handler calls the function which verifies the TGW Association in the child account
    """
    result = {}
    print('event ' + str(event))
    result.update(event)
    try:
        tgw_integration = TGWAttachment(event, context)
        output = tgw_integration.Verify_TGW_attahment_Association()
        result.update(output)
        send_email = tgw_integration.alert_operations()
        return result
    except Exception as exception:
        logger.error(str(exception))
        result.update({'verify_vpc_tgw_association' : FAILED})
        return result
