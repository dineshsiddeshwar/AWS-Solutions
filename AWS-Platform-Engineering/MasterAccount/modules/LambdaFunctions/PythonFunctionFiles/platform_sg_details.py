import os
import logging
import json
import random
import boto3
import csv
import datetime
import calendar
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from boto3.dynamodb.conditions import Key, Attr

SESSION = boto3.session.Session()
SSM_CLIENT = SESSION.client('ssm')
ses_client = SESSION.client('ses')
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
LOGGER.addHandler(CH)
failed_accounts_global = []
SUPPORT_TEAM_ID = "GXSOMWIPROAWSDASupport@shell.com"


def read_aacount():
    """
    Reads the list of accounts in dynamo_db table
    returns: list of active accounts
    """

    try:
        account_list = []
        dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
        dynamo_table = dynamodb.Table('Account_Details')
        response = dynamo_table.scan(ProjectionExpression='AccountNumber,#State_ref,AccountName',
                                     ExpressionAttributeNames={'#State_ref': 'State'})
        result = response['Items']

        while 'LastEvaluatedKey' in response:
            response = dynamo_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])

            result.extend = response['Items']
        if (result):
            for item in result:
                ac_details = {}
                if item['State'] == 'Active':
                    ac_details['AccountName'] = item['AccountName']
                    ac_details['AccountNumber'] = item['AccountNumber']
                    account_list.append(ac_details)

        LOGGER.info("Account Numbers are %s", str(account_list))
        return account_list

    except Exception as ex:
        print("There is an error %s", str(ex))


def get_platform_type(account_list):
    """
    Function checks for compliant ec2 instance in the accounts given by the param.
    Param : list of accounts
    return: SUCCESS or FAILURE
    """
    try:
        global_list = []
        failed_account = []
        succeeded_accounts = []
        session_client = boto3.Session()
        sts_client = session_client.client('sts')
        ec2_client = session_client.client('ec2')
        for item in account_list:
            account = item['AccountNumber']
            account_name = item['AccountName']
            response = child_account_instances_details(account, session_client, sts_client, ec2_client, global_list, account_name)
            if response != str:
                succeeded_accounts.append(account)
        final_list = []
        for item in global_list:
            temp_inbound = item['Inbound']
            if temp_inbound:
                for item_ibound in temp_inbound:
                    temp_dict = {}
                    temp_dict['AccountNumber'] = item['AccountNumber']
                    temp_dict['AccountName'] = item['AccountName']
                    temp_dict['Region'] = item['Region']
                    temp_dict['GroupName'] = item['GroupName']
                    temp_dict['GroupId'] = item['GroupId']
                    temp_dict['Description'] = item['Description']
                    temp_dict['In/Out'] = 'In'
                    temp_dict['IpProtocol'] = item_ibound['IpProtocol']
                    temp_dict['FromPort'] = item_ibound['FromPort']
                    temp_dict['ToPort'] = item_ibound['ToPort']
                    temp_dict['CIDR Range'] = item_ibound['CIDR Range']
                    final_list.append(temp_dict)
            else:
                    temp_dict['AccountNumber'] = item['AccountNumber']
                    temp_dict['AccountName'] = item['AccountName']
                    temp_dict['Region'] = item['Region']
                    temp_dict['GroupName'] = item['GroupName']
                    temp_dict['GroupId'] = item['GroupId']
                    temp_dict['Description'] = item['Description']
                    temp_dict['In/Out'] = 'In'
                    temp_dict['IpProtocol'] = temp_dict['FromPort'] = temp_dict['ToPort'] = 'Empty'
                    temp_dict['CIDR Range'] = ['Not available']
                    final_list.append(temp_dict)
            temp_outbound = item['Outbound']
            if temp_outbound:
                for item_obound in temp_outbound:
                    temp_dict = {}
                    temp_dict['AccountNumber'] = item['AccountNumber']
                    temp_dict['AccountName'] = item['AccountName']
                    temp_dict['Region'] = item['Region']
                    temp_dict['GroupName'] = item['GroupName']
                    temp_dict['GroupId'] = item['GroupId']
                    temp_dict['Description'] = item['Description']
                    temp_dict['In/Out'] = 'Out'
                    temp_dict['IpProtocol'] = item_ibound['IpProtocol']
                    temp_dict['FromPort'] = item_ibound['FromPort']
                    temp_dict['ToPort'] = item_ibound['ToPort']
                    temp_dict['CIDR Range'] = item_ibound['CIDR Range']
                    final_list.append(temp_dict)
            else:
                    temp_dict['AccountNumber'] = item['AccountNumber']
                    temp_dict['AccountName'] = item['AccountName']
                    temp_dict['Region'] = item['Region']
                    temp_dict['GroupName'] = item['GroupName']
                    temp_dict['GroupId'] = item['GroupId']
                    temp_dict['Description'] = item['Description']
                    temp_dict['In/Out'] = 'Out'
                    temp_dict['IpProtocol'] = temp_dict['FromPort'] = temp_dict['ToPort'] = 'Empty'
                    temp_dict['CIDR Range'] = ['Not available']
                    final_list.append(temp_dict)
                    
        make_excel_response = make_excel(final_list)
        LOGGER.info("List of failed accounts to assume Role %s", failed_account)
        LOGGER.info("Succeeded Accounts %s", str(succeeded_accounts))

    except Exception as ex:
        LOGGER.info("Falied in compliance check %s", str(ex))
        return "FAILED"


def child_account_instances_details(account_number, session_client, sts_client, ec2_client_session, global_list, account_name
                                      ):
    try:
        # get whitelisted regions from SSM Parameter Store
        ssm_prmtr_client = boto3.client('ssm')
        regions_response = ssm_prmtr_client.get_parameter(Name='whitelisted_regions')
        temp_p = regions_response['Parameter']['Value']
        regions = temp_p.split(',')
        secondaryRoleArn = "arn:aws:iam::{}:role/AWSControlTowerExecution".format(account_number)
        secondarySessionName = "SecondarySession-" + str(random.randint(1, 100000))
        # Logging to child account.
        # LOGGER.info("Logging to Child Account")
        secondaryRoleCreds = sts_client.assume_role(RoleArn=secondaryRoleArn,
                                                    RoleSessionName=secondarySessionName)
        credentials = secondaryRoleCreds.get('Credentials')
        accessKeyID = credentials.get('AccessKeyId')
        secretAccessKey = credentials.get('SecretAccessKey')
        sessionToken = credentials.get('SessionToken')
        assumeRoleSession = boto3.session.Session(accessKeyID, secretAccessKey, sessionToken)
        ssm_service_role_arn = "arn:aws:iam::{}:role/platform_service_inflation".format(
            account_number)
        ec2_child_client = boto3.client('ec2')
        security_groups_global = []
        for region in regions:
            ec2_child_client = assumeRoleSession.client('ec2', region_name=region)
            sg_response = ec2_child_client.describe_security_groups(MaxResults=999)
            if (sg_response['SecurityGroups']):
                sg_list = sg_response['SecurityGroups']
                for item in sg_list:
                    inbound = item ['IpPermissions']
                    outbound = item['IpPermissionsEgress']
                    inbound_global = []
                    outbound_global = []
                    for rule in inbound:
                        inbound = {}
                        if rule['IpProtocol'] == "-1":
                            traffic_type="All Trafic"
                            ip_protpcol="All"
                            to_port="All"
                            from_port = "All"
                        else:
                            ip_protpcol = rule['IpProtocol']
                            from_port=rule['FromPort']
                            to_port=rule['ToPort']
                            #If ICMP, report "N/A" for port #
                            if to_port == -1:
                                to_port = "N/A"
                        inbound['IpProtocol'] = ip_protpcol
                        inbound['FromPort'] = from_port
                        inbound['ToPort'] = to_port
                        address = " "
                        if len(rule['IpRanges']) > 0:
                            for ip_range in rule['IpRanges']:
                                cidr_block = str(ip_range['CidrIp'])
                                address = address + ","+ cidr_block
                        inbound["CIDR Range"] = address
                        inbound_global.append(inbound)
                    for rule in outbound:
                        outbound = {}
                        if rule['IpProtocol'] == "-1":
                            traffic_type="All Trafic"
                            ip_protpcol="All"
                            to_port="All"
                            from_port = "All"
                        else:
                            ip_protpcol = rule['IpProtocol']
                            from_port=rule['FromPort']
                            to_port=rule['ToPort']
                            #If ICMP, report "N/A" for port #
                            if to_port == -1:
                                to_port = "N/A"
                        outbound['IpProtocol'] = ip_protpcol
                        outbound['FromPort'] = from_port
                        outbound['ToPort'] = to_port
                        address = " "
                        str(address)
                        if len(rule['IpRanges']) > 0:
                            for ip_range in rule['IpRanges']:
                                cidr_block = "," + str(ip_range['CidrIp'])
                                address = address + "," + cidr_block      
                        outbound["CIDR Range"] = address                     
                        outbound_global.append(outbound)
                    security_groups = {}
                    security_groups['AccountNumber'] = account_number
                    security_groups['AccountName'] = account_name
                    security_groups['Region'] = region 
                    security_groups['GroupName'] = item['GroupName']
                    security_groups['GroupId'] = item['GroupId']
                    security_groups['Description'] = item['Description']
                    security_groups['Inbound'] = inbound_global
                    security_groups['Outbound'] = outbound_global
                    global_list.append(security_groups)

        return global_list


    except Exception as ex:
        # LOGGER.info("Unable to assume role in the account %s",account_number)
        LOGGER.error(ex)
        return account_number


def make_excel(input_data):
    """
    Function prepares and sends out excel to given DL
    param: data to send
    return: SUCCESS or FAILURE
    """
    try:
        s3_resource = boto3.resource(u's3')
        s3_bucket = "awsatshellssmcompliancereports"
        # s3_key = boto3.resource("s3")

        current_year = str(datetime.datetime.now().year)
        current_month = calendar.month_name[datetime.datetime.now().month]
        lambda_file_name = "/tmp/" + current_year + current_month + "list_of_security_groups" + ".csv"
        column_names = ['AccountNumber', 'AccountName','Region','GroupId', 'GroupName', 'Description','In/Out','IpProtocol','FromPort','ToPort', 'CIDR Range']
        with open(lambda_file_name, 'w') as f:
            wr = csv.DictWriter(f, fieldnames=column_names)
            wr.writeheader()
            wr.writerows(input_data)
        send_mail(lambda_file_name)
    except Exception as ex:
        LOGGER.error(" An error occured %s", str(ex))


def send_mail(file_name):
    try:
        # # This address must be verified with Amazon SES.
        # sender_id = self.sender_id
        current_year = str(datetime.datetime.now().year)
        current_month = calendar.month_name[datetime.datetime.now().month]
        LOGGER.info("Inside Send Mail %s", str(file_name))
        sender_response = SSM_CLIENT.get_parameter(Name='sender_id')
        sender_id = sender_response['Parameter']['Value']
        rec_response = SUPPORT_TEAM_ID
        to_recipient = rec_response
        recipient_list = to_recipient.split(',')
        # The email body for recipients with non-HTML email clients.
        body_text = "Hello\r\nPlease find the attached Security Groups' details " + "Report for AWS@Shell" \
                                                                      "\r\nRegards,\r\n AWS Platform Engineering Team"
        # The HTML body of the email.
        body_html = """<html>
        <head></head>
        <body>
        <p style="font-family:'Futura Medium'">Hello Team,</p>
        <p style="font-family:'Futura Medium'">Please find the attached Security Groups' details Report for AWS@Shell.</p>
        <p style="font-family:'Futura Medium'">Best Regards,</p>
        <p style="font-family:'Futura Medium'">AWS Platform Engineering Team</p>
        </body>
        </html>
        """
        try:
            # Replace recipient@example.com with a "To" address.
            # # The subject line for the email.
            mail_subject = "Platform Security Groups' details Report for " + "-" + current_month + "-" + current_year
            attachment_template = file_name  # "{}".format(file_name)
            message = MIMEMultipart('mixed')
            message['Subject'] = mail_subject
            message['From'] = sender_id
            message['To'] = to_recipient
            message_body = MIMEMultipart('alternative')
            char_set = "utf-8"
            textpart = MIMEText(body_text.encode(char_set), 'plain', char_set)
            htmlpart = MIMEText(body_html.encode(char_set), 'html', char_set)
            message_body.attach(textpart)
            message_body.attach(htmlpart)
            attribute = MIMEApplication(open(attachment_template, 'rb').read())
            attribute.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment_template))
            message.attach(message_body)
            message.attach(attribute)
            mail_response = ses_client.send_raw_email(
                Source=sender_id,
                Destinations=recipient_list,
                RawMessage={
                    'Data': message.as_string()
                })
            LOGGER.info(" Mail has been successfully sent")

        except Exception as exception:
            print(exception)
    except Exception as exception:
        print(exception)


def lambda_handler(event, context):
    '''
    Main lambda handler takes event as dictionary
    and context as an object
    '''
    try:
        accounts_list = read_aacount()
        LOGGER.info("Calling get platform security details check function")
        status = get_platform_type(accounts_list)

    except Exception as exception:
        print("Exception in Lambda Handler", exception)
