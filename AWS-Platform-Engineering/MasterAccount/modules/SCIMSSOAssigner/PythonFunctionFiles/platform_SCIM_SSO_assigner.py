import json
import time
import os
import boto3
import datetime
import botocore
from boto3.dynamodb.conditions import Attr
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import logging

#Cloudwatch variables
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
LOGGER.addHandler(CH)

SIMAAS_SLA = 5
identitystore_id = "SSO_IDENTITYSTORE_ID"
instance_arn = "SSO_INSTANCE_ARN"

dynamo_client = boto3.client('dynamodb')
SESSION = boto3.session.Session()
SSM_CLIENT = SESSION.client('ssm')
ses_client = SESSION.client('ses')
dynamodb_resource = boto3.resource('dynamodb')


def get_ssm_param(parametre_name):
    """
    param: parametre_name
    return: parameter value for the given param name
    """
    try:
        ssm_client = boto3.client("ssm")
        parameter = ssm_client.get_parameter(
        Name=parametre_name,
            WithDecryption=True
        )
        if parameter:
            return parameter['Parameter']['Value']
    except Exception as ex:
        LOGGER.error("Encountered error while getting parameters".format(ex))

DYNAMOTABLE = get_ssm_param("IPAWS-SCIM-DYNAMO-TABLE")
dynamo_table = dynamodb_resource.Table(DYNAMOTABLE)

SSM_Busniess_Contributor_Public = "BusinessContributor-Public"
SSM_Busniess_Contributor_Private = "BusinessContributor-Private"
SSM_Busniess_LimitedOperator_Private = "LimitedOperatorArn-Private"
SSM_Busniess_LimitedOperator_Public = "LimitedOperatorArn-Public"
SSM_Busniess_ReadOnly_Private = "ReadOnly-Private"
SSM_Busniess_ReadOnly_Public ="ReadOnly-Public"
SSM_Busniess_BusinessOperators_Public = "BusinessOperator-Public"
SSM_Busniess_BusinessOperators_Private ="BusinessOperator-Private"
SSM_Business_BusinessCustom = "BusinessCustom_permission_set"

def notify_operations(list_of_breached_groups):
    try:
        ses_client = boto3.client('ses')
        failure_operation_dl_str = get_ssm_param("failure_operation_dl")
        simaas_operation_dl_str = get_ssm_param("simaas_operation_dl")
        sender_id = get_ssm_param("sender_id")

        body = "<html> <head> <style> table { font-family: Calibri, sans-serif; border-collapse: collapse; width: 100%; text-align: left; } td { border:1px solid #1f1f1f; text-align: left; padding: 10px; } th { border: 1px solid #1f1f1f; border-collapse: collapse; text-align: left; padding: 10px; background-color: #FFFF33; } tr:nth-child(even) { background-color: #aaaa; } pre {font-family: Calibri, sans-serif; size=1px} </style></head><pre>Hi SIMAAS Team, </pre> <br> <pre>Below Active Directory Groups are not synced by the SCIM to the AWS SSO.</pre><br><pre>Please Check and do the needful</pre> <br>"
        footer = " <br/><br/> **This is an auto generated mail by the AWS Platform Engineering Team. <br/><br/>"
        strTable = "<table><tr><th style="'text-align:center'">Group Name</th><th style="'text-align:center'">Account Number</th>"
        strTable = body+strTable
        body_text = """Hello SIMAAS Team\n The following groups were found assigned after the standard 5 hours SLA of SIMAAS. Groups are not yet synced""" \
            + """.\n Please check and do the needful """ + " "\
                    + """\nBest Regards,\n AWS Platform Engineering team"""


        #generate the table dynamically for html file
        for item in list_of_breached_groups:
            temp_list = []
            temp_list.append(item['ADBusinessLimitedOperatorsName'])
            temp_list.append(item['ADBusinessContributorsName'])
            temp_list.append(item['ADBusinessReadOnlyName'])
            temp_list.append(item['ADBusinessOperatorsName'])
            if 'ADBusinessCustomName' in item:
                temp_list.append(item['ADBusinessCustomName'])
            for temp_group in temp_list:
                account_number = str(item["AccountNumber"])
                group_name = str(temp_group)
                strRW = "<tr><td>"+ group_name+ "</td><td>"+account_number+ "</td>" + "</tr>"
                strTable = strTable+strRW 
        strTable = strTable+"</table><br><br><pre>Thanks,</pre><br><pre>AWS Platform Engineering team.</pre><br><br><br><footer>**This is an auto generated mail by the AWS Platform Engineering Team.</footer></html>"

        send_mail_response = ses_client.send_email(
            Source= sender_id,
            Destination={
                'ToAddresses': [simaas_operation_dl_str],
                'CcAddresses': [failure_operation_dl_str,'kraj@simeio.com']
            },
            Message={
                'Subject': {
                    'Data':' SLA Breach: iPAWS Group Replication Failed'
                },
                'Body': {
                    'Text': {
                        'Data': body_text
                    },
                    'Html': {
                        'Data': strTable
                    }
                }
            }
        )
        return send_mail_response
    except Exception as e:
        LOGGER.error(str(e))
        return str(e)

def get_permission_set_arn(parameter_name):
    """
    method: retrieve the Permission set ARN
    param: permission set name stored in parameter store
    return: arn of the parametr store
    """
    try:
        LOGGER.info("Retrieving the arn for: '{0}'".format(parameter_name))
        ssm_param_client = boto3.client('ssm')
        retries = 0
        get_param_status = 'False'
        while retries < 4 and get_param_status == 'False':
            response = ssm_param_client.get_parameter(
                Name=parameter_name,WithDecryption=True)
            temp_res_code = response['ResponseMetadata']['HTTPStatusCode']
            if temp_res_code == 200:
                get_param_status = 'True'
                response_parametre = response['Parameter']
                arn = response_parametre['Value']
                return arn
            else: 
                time_to_sleep = 2 ** retries
                retries += 1
                time.sleep(time_to_sleep)
    except Exception as ex:
        LOGGER.error("ARN retrival from the parameter store failed.")



def marshal_permission_sets_arn():
    """
    method: Retrieve ARNs of the permissions sets and dress in a dictionary
    paran: none
    returns: a dict of permission sets and thei ARNs
    """
    try:
        return_dict = {}
        LOGGER.info("Inside the marshal_permission_sets_arn")
        return_dict["platform_ContributorExternal"] = str(get_permission_set_arn(SSM_Busniess_Contributor_Public))
        return_dict["business_ContributorPrivate"] = str(get_permission_set_arn(SSM_Busniess_Contributor_Private))
        return_dict["business_LimitedOperatorPrivate"] = str(get_permission_set_arn(SSM_Busniess_LimitedOperator_Private))
        return_dict["business_LimitedOperatorExternal"] = str(get_permission_set_arn(SSM_Busniess_LimitedOperator_Public))
        return_dict["business_ReadOnlyPrivate"] = str(get_permission_set_arn(SSM_Busniess_ReadOnly_Private))
        return_dict["business_ReadOnlyExternal"] = str(get_permission_set_arn(SSM_Busniess_ReadOnly_Public))
        return_dict["business_OperatorExternal"] = str(get_permission_set_arn(SSM_Busniess_BusinessOperators_Public))
        return_dict["business_OperatorPrivate"] = str(get_permission_set_arn(SSM_Busniess_BusinessOperators_Private))
        return_dict["business_Custom"] = str(get_permission_set_arn(SSM_Business_BusinessCustom))
        return return_dict
    except Exception as ex:
        LOGGER.error("Error while retriving the arn s from the parameter storey: '{0}'".format(ex))
        return "FAILED"


def get_ssm_param(parametre_name):
    """
    param: parametre_name
    return: parameter value for the given param name
    """
    try:
        ssm_client = boto3.client("ssm")
        parameter = ssm_client.get_parameter(
        Name=parametre_name)
        if parameter:
            return parameter['Parameter']['Value']
    except Exception as ex:
        LOGGER.error("Encountered error while getting parameters".format(ex))



def assign_account(permission_sets_arn,account_number):
    """
    method: assign permission to a account with groups
    params: group names
    return: success or failure
    """
    try:
        LOGGER.info("Inside the groups assigner for the acount '{0}':".format(account_number))
        identity_client = boto3.client('identitystore')
        sso_admin_client = boto3.client('sso-admin')
        failed_groups = []
        success_groups = []
        verify_list = []
        sso_identitystore_id = get_ssm_param('identitystore_id')
        sso_instance_arn = get_ssm_param('instance_arn')
        LOGGER.info("Initiating SSO Operations for the Identity store:'{0}' and SSO instance: '{1}'".format(identitystore_id,instance_arn))
        if permission_sets_arn:
            dynamo_update_response = dynamo_client.update_item(
                        TableName=DYNAMOTABLE,
                        Key={
                            'AccountNumber': {"S": account_number}
                            },
                            ReturnValues='ALL_NEW',
                            UpdateExpression="SET IsChecked=:u",
                            ExpressionAttributeValues={
                                ":u": {"S": "True"}})
            for item in permission_sets_arn:
                association_status = "True"
                arn = item['arn']
                verify_list.append(arn)
                group = item['group']
                identitystore_response = identity_client.list_groups(
                    IdentityStoreId= sso_identitystore_id,
                    MaxResults=99,
                    Filters=[
                        {
                            'AttributePath': 'DisplayName',
                            'AttributeValue': group
                            },
                            ])
                if identitystore_response["Groups"]:
                    temp_data = identitystore_response["Groups"][0]
                    group_princial = temp_data['GroupId']
                    response = sso_admin_client.create_account_assignment(
                        InstanceArn=sso_instance_arn,
                        TargetId= account_number,
                        TargetType='AWS_ACCOUNT',
                        PermissionSetArn=arn,
                        PrincipalType='GROUP',
                        PrincipalId=group_princial)
                    LOGGER.info("Done for the group '{0}', updating the dynamodb table".format(group))
                    success_groups.append(item['group'])                 
                else:
                    LOGGER.error("'{0}' : no such group created in SSO. please check with the SIMAAS team'".format(group))
                    failed_groups.append(item['group'])
            if failed_groups:
                association_status = "False" 
            dynamo_update_response = dynamo_client.update_item(
                TableName=DYNAMOTABLE,
                Key={
                    'AccountNumber': {"S": account_number}
                    },
                    ReturnValues='ALL_NEW',
                    UpdateExpression="SET AssociationStatus=:u",
                    ExpressionAttributeValues={
                        ":u": {"S": association_status}})
            LOGGER.info("List of successfully assigned groups{0}".format(success_groups))
            LOGGER.info("List of failed groups{0}".format(failed_groups))
            return "SUCCESS"
    except Exception as ex:
        LOGGER.error("Failed to assign the permission due to:'{0}'".format(ex))
        return "FAILED"


def call_assigner():
    """
    Method: Assign groups to accounts with permission sets.
    param: none
    returns: Success or Failure
    """
    try:
        sso_admin_client = boto3.client('sso-admin')
        
        LOGGER.info("Inside the call_assigner")
        permission_sets_arn = marshal_permission_sets_arn()

        if type(permission_sets_arn) != dict:
            return "FAILED"
        scan_complete = False
        records = []
        response = dynamo_table.scan(
            FilterExpression=Attr('AssociationStatus').eq('False'))
        while 'LastEvaluatedKey' in response:
            response = dynamo_table.scan(
                    FilterExpression=Attr('AssociationStatus').eq('False'),
                    ExclusiveStartKey=response['LastEvaluatedKey'])
        if response['Count'] == 0:
            LOGGER.info("No unassociated groups for now. Exiting...!")
            return "SUCESS"
        
        dynamo_items = response['Items']
        now = datetime.datetime.now()
        current_hour = now.hour
        sla_breach = []
        for item in dynamo_items:
            if 'CreationTime' in item and abs(int(item['CreationTime'])-current_hour) > SIMAAS_SLA:
                sla_breach.append(item)
        
        if sla_breach:
            for item in sla_breach:
                if item in dynamo_items:
                    dynamo_update_response = dynamo_client.update_item(
                        TableName=DYNAMOTABLE,
                        Key={
                            'AccountNumber': {"S": item['AccountNumber']}
                        },
                        ReturnValues='ALL_NEW',
                        UpdateExpression="SET CreationTime=:u",
                        ExpressionAttributeValues={
                            ":u": {"S": str(current_hour)}})
                    dynamo_items.remove(item)
            notify_operations(sla_breach)

        if len(dynamo_items) == 0:
            LOGGER.error("SLA Breached for{0}".format(sla_breach))
            return "SUCCESS"
    
        for item in dynamo_items:
            private_permission_set = []
            private_permission_set.append(
                {'arn' : permission_sets_arn['business_LimitedOperatorPrivate'], 
                'group': item ['ADBusinessLimitedOperatorsName']
                })
            private_permission_set.append({
                'arn':permission_sets_arn['business_ContributorPrivate'],
                'group': item['ADBusinessContributorsName']
                 })
            private_permission_set.append({
                'arn': permission_sets_arn['business_ReadOnlyPrivate'],
                'group': item ['ADBusinessReadOnlyName']})
            private_permission_set.append({
                'arn' : permission_sets_arn['business_OperatorPrivate'],
                'group':item ['ADBusinessOperatorsName']})
            
            if 'BusinessCustom' in item:
                private_permission_set.append({
                        'arn': permission_sets_arn['business_Custom'],
                        'group': item ['ADBusinessCustomName']})

            public_permission_set = []
            public_permission_set.append(
                {
                'arn': permission_sets_arn['platform_ContributorExternal'],
                'group': item ['ADBusinessContributorsName']
                }
                )
            public_permission_set.append(
                {'arn':permission_sets_arn['business_LimitedOperatorExternal'],
                'group': item ['ADBusinessLimitedOperatorsName']
                })
            public_permission_set.append(
                {
                    'arn': permission_sets_arn['business_ReadOnlyExternal'],
                    'group': item ['ADBusinessReadOnlyName']
                    }
                    )
            public_permission_set.append(
                {
                    'arn': permission_sets_arn['business_OperatorExternal'],
                    'group':item ['ADBusinessOperatorsName']})
            
            if 'BusinessCustom' in item:
                public_permission_set.append(
                {
                    'arn': permission_sets_arn['business_Custom'],
                    'group': item ['ADBusinessCustomName']})
            

            account_type = item['AccountType']
            if item['AccountType'] in ['PVT','HBD']:
                try:
                    LOGGER.info("Assigning permisions to accounts")
                    assign_response = assign_account(private_permission_set,item['AccountNumber'])
                except Exception as Ex:
                    LOGGER.error("Error while assigning permission sets to accounts: '{0}'".format(Ex))
                    return "FAILED"
            else:
                try:
                    LOGGER.info("Assigning permisions to accounts")
                    assign_response = assign_account(public_permission_set,item['AccountNumber'])
                except Exception as Ex:
                    LOGGER.error("Error while assigning permission sets to accounts: '{0}'".format(Ex))
                    return "FAILED"
        return "SUCCESS"
    except Exception as ex:
        LOGGER.error("Lambda failed with the error:'{0}'".format(ex))
        return "FAILED"




def lambda_handler(event, context):
    """
    Author:Shanmukha SP (shanmukhaswamy.p@shell.com)
    Method: Callling lambda function
    param: event passed by AWS Lambda
    param: context passed by the AWS Lambda
    returns: Success or Failure
    """
    try:
        LOGGER.info("Starting the lambda with event '{0}'".format(json.dumps(event)))
        response = call_assigner()
        return response
    except Exception as ex:
        LOGGER.error("Lambda failed with the error:'{0}'".format(ex))
        return "FAILED"