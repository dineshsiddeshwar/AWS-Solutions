#!/usr/bin/env python3
# Python3 script to clean up unique lambda functions and log groups that are created when aws@shell ec2 SSM
# initialisation automation runs.

import boto3
import os
import logging
from datetime import datetime, timedelta, timezone
from botocore.exceptions import ClientError

# Setup log handlers for both local interpreters and Lambda
if len(logging.getLogger().handlers) > 0:
    logging.getLogger().setLevel(logging.INFO)
else:
    logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

now = datetime.utcnow()
epoch_date = now - datetime(1970, 1, 1)
epoch_milliseconds = round((epoch_date.total_seconds())*1000)
aws_region = os.environ.get('AWS_REGION', 'us-east-1')
dry_run_env = os.environ.get('DRY_RUN', 'False')


if dry_run_env in ['T', 'TRUE', 'true', 'True', 'Y', 'y', 'Yes']:
    dry_run = True
else:
    dry_run = False

function_prefix = ['InitPolicyLambda', 'InitRoleLambda', 'InitInstanceProfileLambda']
stack_prefix = ['SetupManagedRoleOnInstanceStack']
log_group_path = '/aws/lambda/'


def get_delete_thresholds(resource_retention_days):
    # We retain ec2 instance initialisation logs in case any debugging is required (86400000ms per day)
    total_retention_milliseconds = resource_retention_days * 86400000
    log_deletion_timestamp_threshold = epoch_milliseconds - total_retention_milliseconds

    # We retain CloudFormation stacks that are newer than the resource retention configuration
    stack_deletion_date_threshold = now - timedelta(days=resource_retention_days)
    stack_deletion_date_threshold = stack_deletion_date_threshold.replace(tzinfo=timezone.utc)
    return log_deletion_timestamp_threshold, stack_deletion_date_threshold


def find_stacks(cf_client=None, create_time_older_than=None):
    """
    Function to find all relevant cloudformation stacks that need housekeeping
    :param cf_client: optional boto3 client for cloudformation
    :param create_time_older_than: the datetime object that is the deletion threshold
    :return: list of strings containing cloudformation stacks
    """
    list_stacks = []
    if cf_client is None:
        cf_client = boto3.client('cloudformation', region_name=aws_region)
    if create_time_older_than is None:
        log_date, create_time_older_than = get_delete_thresholds(os.environ.get('RESOURCE_RETENTION_DAYS', 1))
    paginator = cf_client.get_paginator('list_stacks')
    page_iterator = paginator.paginate()
    for page in page_iterator:
        for stack in page['StackSummaries']:
            # We are only interested in stacks that have not already been deleted and have a create time older
            # than our set resource retention period
            stack_creation_time = stack.get('CreationTime', datetime(2015, 1, 1))
            if stack.get('StackStatus', None) != 'DELETE_COMPLETE':
                if stack_creation_time < create_time_older_than:
                    list_stacks.append(stack['StackName'])
    filtered_list_stacks = filter_stacks(list_stacks)
    return filtered_list_stacks


def filter_stacks(stack_list):
    """
    Function to filter cloudformation stack names to only include those in function prefix
    :param stack_list: list of strings containing stack names
    :return: filtered list of strings containing stack names
    """
    filtered_stacks = []
    for prefix in stack_prefix:
        filtered_stacks.extend(list(filter(lambda x: x.startswith(prefix), stack_list)))
    return filtered_stacks


def filter_log_groups(log_list):
    """
    Function to filter log groups names to only include those in function prefix
    :param log_list: list of strings containing function names
    :return: filtered list of strings containing lambda function names
    """
    filtered_logs = []
    for prefix in function_prefix:
        filtered_logs.extend(list(filter(lambda x: x.startswith(log_group_path + prefix), log_list)))
    return filtered_logs


def find_log_groups(logs_client=None, create_time_older_than=None):
    """
    Function to find all relevant log groups that need housekeeping
    :param logs_client: optional boto3 client for CW logs
    :param create_time_older_than: Integer value that is milliseconds since epoch
    :return: list of strings containing log groups
    """
    list_log_groups = []
    if logs_client is None:
        logs_client = boto3.client('logs', region_name=aws_region)
    if create_time_older_than is None:
        create_time_older_than, cf_date = get_delete_thresholds(os.environ.get('RESOURCE_RETENTION_DAYS', 1))
    paginator = logs_client.get_paginator('describe_log_groups')
    operation_parameters = {'logGroupNamePrefix': log_group_path}

    page_iterator = paginator.paginate(**operation_parameters)
    for page in page_iterator:
        for group in page['logGroups']:
            group_create_time = group.get('creationTime', None)
            if group_create_time is not None:
                if group_create_time < create_time_older_than:
                    list_log_groups.append(group['logGroupName'])
    filtered_list_log_groups = filter_log_groups(list_log_groups)
    return filtered_list_log_groups


def delete_log_groups(log_groups, logs_client=None):
    """
    Function to delete all log groups provided in the log_groups param
    :param log_groups: list of strings containing log group names
    :param logs_client: optional boto3 client for CW logs
    :return: nothing
    """
    if logs_client is None:
        logs_client = boto3.client('logs', region_name=aws_region)
    for group in log_groups:
        if dry_run is False:
            try:
                logger.info(f'deleting log group {group}')
                response = logs_client.delete_log_group(logGroupName=group)
                code = response['ResponseMetadata']['HTTPStatusCode']
                if code == 200:
                    logger.info(f'{group} deleted')
                else:
                    logger.warning(response)
            except ClientError as e:
                logger.error('Unexpected error: %s' % e)
        else:
            logger.info(f'Would have deleted log group: {group}')


def delete_cf_stacks(stacks, cf_client=None):
    """
    Function to delete all cloudformation stacks provided in the lambda_functions param
    :param stacks: list of strings containing cloudformation stacks
    :param cf_client: optional boto3 client object for cloudformation
    :return: nothing
    """
    if cf_client is None:
        cf_client = boto3.client('cloudformation', region_name=aws_region)
    for stack in stacks:
        if dry_run is False:
            try:
                logger.info(f'deleting cloudformation stack {stack}')
                response = cf_client.delete_stack(StackName=stack)
                code = response['ResponseMetadata']['HTTPStatusCode']
                if code == 200:
                    logger.info(f'{stack} deleted')
                else:
                    logger.warning(response)
            except ClientError as e:
                logger.error('Unexpected error: %s' % e)
        else:
            logger.info(f'Would have deleted cloudformation stack: {stack}')


def main():
    moto_endpoint_url = os.environ.get('MOTO_HTTP_ENDPOINT', None)
    if moto_endpoint_url is not None:
        # We are using moto so use a custom endpoint_urls for our Boto clients
        logs_client = boto3.client('logs', region_name=aws_region, endpoint_url=moto_endpoint_url)
        cf_client = boto3.client('cloudformation', region_name=aws_region, endpoint_url=moto_endpoint_url)
        resource_retention_days = 0
    else:
        # Construct standard Boto clients
        logs_client = boto3.client('logs', region_name=aws_region)
        cf_client = boto3.client('cloudformation', region_name=aws_region)
        resource_retention_days = os.environ.get('RESOURCE_RETENTION_DAYS', 1)

    # Check our deletion thresholds based on our retention settings
    log_deletion_threshold, stack_deletion_threshold = get_delete_thresholds(resource_retention_days)

    # Now perform the main functionality
    target_log_groups = find_log_groups(logs_client=logs_client, create_time_older_than=log_deletion_threshold)
    delete_log_groups(target_log_groups, logs_client=logs_client)
    target_cf_stacks = find_stacks(cf_client=cf_client, create_time_older_than=stack_deletion_threshold)
    delete_cf_stacks(target_cf_stacks, cf_client=cf_client)

    # If we get this far without an exception, then we have completed successfully
    return f'Main function completed successfully'


def lambda_handler(event, context):
    # Function for when launched by Lambda
    logger.info(event)
    logger.info(str(context))
    logger.info('DRY_RUN = ' + dry_run_env)
    logger.info('REGION  = ' + aws_region)
    return main()


if __name__ == '__main__':
    # Function for when launched from local Python interpreter
    main()
