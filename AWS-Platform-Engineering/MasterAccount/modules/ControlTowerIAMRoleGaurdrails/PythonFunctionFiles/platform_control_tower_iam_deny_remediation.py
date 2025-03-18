#!/usr/bin/env python3
# Python3 script to remediate IAM identities that do not have the required AWSControlTowerExecution STS Deny
# policy attached.


import boto3
import os
import logging
from datetime import datetime
from botocore.exceptions import ClientError


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
now = datetime.utcnow()
aws_region = os.environ.get('AWS_REGION', 'us-east-1')
iam_policy_arns = os.environ.get('IAM_POLICY_ARNS', [])
if ',' in iam_policy_arns:
    iam_policy_arns = iam_policy_arns.split(',')
if isinstance(iam_policy_arns, str):
    iam_policy_arns = [iam_policy_arns]


def get_logger():
    """
    Setup log handlers for both local interpreters and Lambda
    :return Logging object
    """
    if len(logging.getLogger().handlers) > 0:
        logging.getLogger().setLevel(logging.INFO)
    else:
        logging.basicConfig(level=logging.INFO)
    return logging.getLogger()


def get_attached_policies(role_name=None, user_name=None, iam_client=None):
    """
    Get list of managed policy ARNs attached for a role or user
    :param role_name: string containing AWS config resource name for a role
    :param user_name: string containing AWS config resource name for a user
    :param iam_client: optional boto3 client for AWS IAM
    :return: list of strings containing managed policy ARNs
    """
    attached_policies = []
    response = {}
    resource_name = None
    if iam_client is None:
        iam_client = boto3.client('iam', region_name=aws_region)
    try:
        if role_name is not None:
            resource_name = role_name
            response = iam_client.list_attached_role_policies(
                RoleName=resource_name
            )
        elif user_name is not None:
            resource_name = user_name
            response = iam_client.list_attached_user_policies(
                UserName=resource_name
            )
        code = response['ResponseMetadata']['HTTPStatusCode']
        if code == 200:
            logger.info(f'{resource_name} policies found')
            for p in response.get('AttachedPolicies', []):
                if p.get('PolicyArn', None) is not None:
                    attached_policies.append(p.get('PolicyArn'))
        else:
            logger.warning(response)
    except ClientError as e:
        logger.error('Unexpected error: %s' % e)
    return attached_policies


def attach_managed_iam_policy(policy_arn, role_name=None, user_name=None, iam_client=None):
    """
    Attach a managed policy to a role or user
    :param policy_arn: string containing ARN for IAM managed policy
    :param role_name: string containing AWS config resource name for a role
    :param user_name: string containing AWS config resource name for a user
    :param iam_client: optional boto3 client for AWS IAM
    """
    response = {}
    resource_name = None
    if iam_client is None:
        iam_client = boto3.client('iam', region_name=aws_region)
    try:
        if role_name is not None:
            resource_name = role_name
            response = iam_client.attach_role_policy(
                RoleName=resource_name,
                PolicyArn=policy_arn
            )
        elif user_name is not None:
            resource_name = user_name
            response = iam_client.attach_user_policy(
                UserName=resource_name,
                PolicyArn=policy_arn
            )
        code = response['ResponseMetadata']['HTTPStatusCode']
        if code == 200:
            logger.info(f'Successfully attached {policy_arn} to {resource_name}')
        else:
            logger.warning(response)
    except ClientError as e:
        logger.error('Unexpected error: %s' % e)
    return


def remediate_iam_identity(resource_id, resource_type, resource_name, iam_client=None):
    """
    Performs remediation logic for IAM roles
    :param resource_id: string containing AWS config resource id
    :param resource_type: string containing AWS config resource type
    :param resource_name: string containing underlying AWS resource name
    :param iam_client: optional boto3 client for AWS IAM
    """
    logger.info(f'Remediating IAM identity {resource_id} {resource_type} {resource_name}')
    if iam_client is None:
        iam_client = boto3.client('iam', region_name=aws_region)

    if resource_type == 'AWS::IAM::Role':
        attached_policies = get_attached_policies(role_name=resource_name, iam_client=iam_client)
    elif resource_type == 'AWS::IAM::User':
        attached_policies = get_attached_policies(user_name=resource_name, iam_client=iam_client)
    else:
        attached_policies = []

    for policy in iam_policy_arns:
        logger.info(f'Checking policy {policy}')
        if policy in attached_policies:
            logger.info(f'{policy} already attached to {resource_name}')
        else:
            logger.info(f'{policy} needs attached to {resource_name}')
            if resource_type == 'AWS::IAM::Role':
                attach_managed_iam_policy(policy, role_name=resource_name, iam_client=iam_client)
            elif resource_type == 'AWS::IAM::User':
                attach_managed_iam_policy(policy, user_name=resource_name, iam_client=iam_client)
    return


def remediation_wrapper(evaluation, resource_id, resource_type, config_client=None):
    """
    Main remediation_wrapper for performing remediation logic
    :param evaluation: string containing new compliance evaluation COMPLIANT or NON_COMPLIANT
    :param resource_id: string containing AWS config resource id
    :param resource_type: string containing AWS config resource type
    :param config_client: optional boto3 client for AWS Config
    :return: string
    """
    resource_response = None
    if config_client is None:
        config_client = boto3.client('config', region_name=aws_region)

    try:
        # Lets look up the AWS resource in Config so we can identify its true ARN
        resource_response = config_client.list_discovered_resources(
            resourceType=resource_type,
            resourceIds=[resource_id]
        )
        code = resource_response['ResponseMetadata']['HTTPStatusCode']
        if code == 200:
            logger.info(f'{resource_id} found')
        else:
            logger.warning(resource_response)
    except ClientError as e:
        logger.error('Unexpected error: %s' % e)

    if len(resource_response.get('resourceIdentifiers', [])) > 0:
        # We found the resource so lets process it
        resource_name = resource_response.get('resourceIdentifiers')[0].get('resourceName', None)
        if resource_name is not None:
            if evaluation == 'COMPLIANT':
                logger.info(f'The resource {resource_id} of type {resource_type} is updated as '
                            f'compliant - no action required')
            else:
                logger.info(f'The resource {resource_id} of type {resource_type} is updated as '
                            f'non-compliant - taking corrective action')
                remediate_iam_identity(resource_id, resource_type, resource_name)
        else:
            logger.warning(f'Invalid resource name returned for {resource_id} or {resource_type}')
    else:
        # The resource was not found and was likely deleted in the mean time
        logger.warning(f'The resource {resource_id} of type {resource_type} was not found and may have been deleted')

    # If we get this far without an exception, then we have completed successfully
    return


def lambda_handler(event, context):
    # Function for when launched by Lambda
    global now
    global logger
    now = datetime.utcnow()
    logger = get_logger()
    logger.info(f'Event = {event}')
    logger.info(f'Context = {str(context)}')

    # Check we have a valid list of required IAM policy ARNs to work with
    if len(iam_policy_arns) > 0:
        # Start by checking the event payload contains the expected fields
        event_request_parameter_evals = event.get('detail', {}).get('requestParameters', {}).get('evaluations', [])
        if len(event_request_parameter_evals) > 0:
            for config_e in event_request_parameter_evals:
                config_evaluation = config_e.get('complianceType', None)
                config_resource_id = config_e.get('complianceResourceId', None)
                config_resource_type = config_e.get('complianceResourceType', None)
                if config_evaluation is not None and config_resource_id is not None and \
                        config_resource_type is not None:
                    # If we have valid values then proceed to perform the remediation function logic
                    remediation_wrapper(config_evaluation, config_resource_id, config_resource_type)
        else:
            # If we do not have valid values, then we raise an error
            logging.error('Invalid event payload received')
            raise
    else:
        # The IAM policy list is empty
        logging.error('Invalid list of IAM policy ARNs found in env vars')
        raise


def main():
    """
    Main
    :param evaluation: string containing new compliance evaluation COMPLIANT or NON_COMPLIANT
    :param resource_id: string containing AWS config resource id
    :param resource_type: string containing AWS config resource type
    :param config_client: optional boto3 client for AWS Config
    :return: string
    """
    # These variables are useful for local testing
    # AROAVJVKMRZFKBYDGFIZY = Role in DEV
    # AIDAVJVKMRZFMQG5TTUNR = User in DEV
    config_eval = os.environ.get('CONFIG_EVALUATION', 'NON_COMPLIANT')
    res_id = os.environ.get('CONFIG_RESOURCE_ID', 'AIDAVJVKMRZFMQG5TTUNR')
    res_type = os.environ.get('CONFIG_RESOURCE_TYPE', 'AWS::IAM::User')
    global iam_policy_arns
    iam_policy_arns = ['arn:aws:iam::364355817034:policy/platform_deny_assume_control_tower_role_policy']
    config_client = boto3.client('config', region_name=aws_region)
    remediation_wrapper(config_eval, res_id, res_type, config_client=config_client)


if __name__ == '__main__':
    main()
