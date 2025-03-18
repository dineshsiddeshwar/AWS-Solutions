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
TRUE = "TRUE"
FALSE = "FALSE"
SUCCESS = "SUCCESS"
FAILED = "FAILED"
PASSED = "PASSED"

class ConfigureVPCTGWRoute(object):
    """
    # Class: ConfigureVPCTGWRoute
    # Description: Configures VPC to TGW Route in the child account
    """

    def __init__(self, event, context):
        self.event = event
        self.context = context
        logger.info("Event: %s" % self.event)
        logger.info("Context: %s" % self.context)
        self.result = {'vpc_tgw_route': {}}
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
            self.result.update({'configure_vpc_tgw_route' : FAILED})

 
    def Configure_VPC_TGW_Route(self):     
        """
        # Takes request body
        # return: resource share status
        """
        try:
            for region in self.regions:
                #Defining/Getting required parameters
                self.region = region
                self.res_dict = {self.region : {}}
                #getting all the subnets
                self.subnets = []
                for key,value in self.tgw_details[self.region]['subnet_id'].items():
                    for temp in value:
                        if key == 'PRIVATE':
                            self.subnets.append(temp)
                        elif key == 'PUBLIC':
                            self.subnets.append(temp)                
                self.configure_vpc_tgw_route()
            return self.result               
        except Exception as exception:
            logger.error(str(exception))
            self.result.update({'configure_vpc_tgw_route' : FAILED})
            return self.result


    def configure_vpc_tgw_route(self):
        try:
            self.tgw_id = self.tgw_details[self.region]['TransitGatewayId']
            self.tgw_attach_id = self.tgw_details[self.region]['tgw_attachment_id']
            self.child_account_ec2_client = self.assumeRoleSession.client('ec2',region_name=self.region)                
            if self.tgw_attach_id:
                #Verifying if transitgateway attachment is accepted?
                tgw_id_response = self.child_account_ec2_client.describe_transit_gateway_attachments()
                tgw_attachment = FALSE
                logger.info(tgw_id_response)
                if len(tgw_id_response['TransitGatewayAttachments']) > 0:
                    for item in tgw_id_response['TransitGatewayAttachments']:
                        if item['TransitGatewayAttachmentId'] == self.tgw_attach_id and item['State'] == 'available':
                            tgw_attachment = TRUE
                            logger.info("Attachment {} is accepted".format(item['TransitGatewayAttachmentId']))
                            self.res_dict[self.region].update({'tgw_attachment_accept' : SUCCESS})
                        elif item['TransitGatewayAttachmentId'] == self.tgw_attach_id and item['State'] == 'failed':
                            logger.info("Attachment {} is failed".format(item['TransitGatewayAttachmentId']))
                            status_message = "TGW Attachment Accept is failed in Global Network Account"
                            self.res_dict[self.region].update({'tgw_attachment_accept' : FAILED})
                            self.alert_operations(self.account_id, self.region,self.event['ResourceProperties']['RequestNo'], status_message)
            
            #Configuring VPC TGW Route          
            if tgw_attachment == TRUE:
                logger.info("proceeding to configure route in {}".format(self.region))
                self.vpc_id = self.tgw_details[self.region]['vpc_id']
                #Getting route table id
                route_table_response = self.child_account_ec2_client.describe_route_tables(
                    Filters=[
                        {
                            'Name': 'association.main',
                            'Values': [
                                'true',
                            ]
                        },
                        {
                            'Name': 'vpc-id',
                            'Values': [
                                self.vpc_id,
                            ]
                        },                            
                    ],
                )
                logger.info(route_table_response)
                if len(route_table_response['RouteTables']) > 0:
                    id = [item['RouteTableId'] for item  in route_table_response['RouteTables']]
                    self.route_table_id = id[0]
                    
                #verifying if the vpc tgw route alraedy exists
                route_configured = FALSE
                if self.tgw_id:
                    for item in route_table_response['RouteTables'][0]['Routes']:
                        for value in list(item.values()):
                            if value == self.tgw_id:
                                route_configured = TRUE
                                logger.info("VPC {} TO TGW {} route is already configured".format(self.vpc_id, self.tgw_id))
                                self.res_dict[self.region].update({'vpc_tgw_route_configure' : PASSED})
                                self.update_result()
                    for item in route_table_response['RouteTables'][0]['Associations']:
                        for abc in self.subnets:
                            if item['Main'] == False and  item['SubnetId'] != abc:
                                subnet_response = self.child_account_ec2_client.associate_route_table(
                                    RouteTableId=self.route_table_id,
                                    SubnetId=abc,
                                ) 
                                logger.info(subnet_response)
                                if subnet_response:
                                    logger.info("Associated new subnet {} to {} route table".format(abc, self.route_table_id))
                                    
                    #creating vpc tgw route
                    if route_configured == FALSE:
                        logger.info("VPC {} TO TGW {} configuration does not exist, proceeding to create".format(self.vpc_id, self.tgw_id))
                        route_response = self.child_account_ec2_client.create_route(
                            DestinationCidrBlock='0.0.0.0/0',
                            TransitGatewayId=self.tgw_id,
                            RouteTableId=self.route_table_id,
                        )
                        logger.info(route_response)
                        for item in self.subnets:
                            subnet_response = self.child_account_ec2_client.associate_route_table(
                                RouteTableId=self.route_table_id,
                                SubnetId=item,
                            )
                            if subnet_response:
                                logger.info("Associated {} to {} route table".format(item, self.route_table_id))
                        if route_response:
                            if route_response['Return'] == True:
                                logger.info("VPC {} TO TGW {} configuration is done".format(self.vpc_id, self.tgw_id))
                                self.res_dict[self.region].update({'vpc_tgw_route_configure' : SUCCESS}) 
                                self.update_result()
                            else:
                                logger.info("VPC {} TO TGW {} configuration is failed".format(self.vpc_id, self.tgw_id))
                                status_message = "VPC to TGW Route configuration failed"
                                self.res_dict[self.region].update({'vpc_tgw_route_configure' : FAILED})
                                self.update_result()
                                self.alert_operations(self.account_id, self.region,self.event['ResourceProperties']['RequestNo'], status_message)
            else: 
                logger.info("TGW Attachment is not in Available state")
            return self.result            
        except Exception as exception:
            logger.error(str(exception))
            self.res_dict[self.region].update({'vpc_tgw_route_configure' : FAILED})
            self.update_result()
            return self.result

            
    def update_result(self):
        try:
            if self.region == 'us-east-1':
                self.result['vpc_tgw_route'].update({'us-east-1': self.res_dict[self.region]})
            elif self.region == 'eu-west-1':
                self.result['vpc_tgw_route'].update({'eu-west-1':self.res_dict[self.region]})
            elif self.region == 'ap-southeast-1':
                self.result['vpc_tgw_route'].update({'ap-southeast-1':self.res_dict[self.region]})
            return self.result
        except Exception as exception:
            self.result.update({'vpc_tgw_route_update_result' : FAILED})
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
            self.result.update({'vpc_tgw_route_get_parameter' : FAILED})
            return self.result 


    def alert_operations(self,account_id, region_name,request_id, message):
        try:
            self.ses_client = boto3.client('ses')
            logger.info("Sending failed email")
            failure_operation_dl_str = self.get_ssm_param("failure_operation_dl")
            sender_id = self.get_ssm_param("sender_id")
            body_text = """Hello Team\n The following error occurred during TGW Association """ \
                + """.\n• Account Id : """ + str(account_id) + " "\
                    + """.\n• Region """ + str(region_name) + " "\
                        + """.\n• Error : """ + str(message) + " "\
                        + """\nBest Regards,\n AWS Platform Engineering team"""

            # The HTML body of the email.
            body_html = body_html = """<html>
                    <body>
                    <p style="font-family:'Arial Nova'">Hello Team,<p>
                    <p></p>
                    <p style="font-family:'Arial Nova'">The following error occurred during TGW Association operation..</p>
                    <ul>
                    <li style="font-family:'Arial Nova'">Account Id: """ + str(account_id) + """</li>
                    </ul>
                    <ul>
                    <li style="font-family:'Arial Nova'">Request Number: """ + str(request_id) + """</li>
                    </ul>
                    <ul>
                    <li style="font-family:'Arial Nova'">Region: """ + str(region_name) + """</li>
                    </ul>
                    <ul>
                    <li style="font-family:'Arial Nova'">Error: """ + str(message) + """</li>
                    </ul>
                    <p style="font-family:'Arial Nova'"></p>
                    <p style="font-family:'Arial Nova'">Thanks,</p>
                    <p style="font-family:'Arial Nova'"> AWS Platform Engineering Team.</p>
                    </body>
                    </html>
                """

            send_mail_response = self.ses_client.send_email(
                Source= sender_id,
                Destination={
                    'ToAddresses': [failure_operation_dl_str]
                },
                Message={
                    'Subject': {
                        'Data':' ALERT: VPC TGW Route Configuration Failed'
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
    Lambda handler calls the function which accepts the TGW resource share in the child account
    """
    result = {}
    print('event ' + str(event))
    result.update(event)
    try:
        tgw_integration = ConfigureVPCTGWRoute(event, context)
        output = tgw_integration.Configure_VPC_TGW_Route()
        result.update(output)
        return result
    except Exception as exception:
        logger.error(str(exception))
        result.update({'configure_vpc_tgw_route' : FAILED})
        return result
