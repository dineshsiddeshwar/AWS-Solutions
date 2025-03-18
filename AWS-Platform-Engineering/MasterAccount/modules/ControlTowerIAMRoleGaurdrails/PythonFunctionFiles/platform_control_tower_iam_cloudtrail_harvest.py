#!/usr/bin/env python3
# Python3 script to extract CloudTrail events for the use of the AWSControlTowerExecution IAM role across the
# AWS@Shell organization

import boto3
import os
import logging
import time
import sys
import json
from datetime import datetime, timedelta
from botocore.exceptions import ClientError


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
now = datetime.utcnow()
epoch = datetime(1970, 1, 1)
epoch_date = now - epoch
epoch_seconds = round((epoch_date.total_seconds()))
epoch_milliseconds = round((epoch_date.total_seconds())*1000)

max_query_wait_time = 300       # This is seconds
query_wait_time = 3             # This is seconds
max_batch_cw_put_events = 200   # This is to ensure our batch payloads do not go above the max size permitted by AWS
ct_query_max_row_limit = 10000  # 10000 is the limit of rows returned by a CW insights query

ct_default_query = f'fields @timestamp, userIdentity.arn, eventName, @message, @logStream, @log ' \
                   f'| sort @timestamp desc ' \
                   f'| filter userIdentity.arn like /AWSControlTowerExecution/ ' \
                   f'or requestParameters.roleArn like /AWSControlTowerExecution/' \
                   f'or requestParameters.roleName like /AWSControlTowerExecution/ ' \
                   f'or errorMessage like /AWSControlTowerExecution/ ' \
                   f'| filter userIdentity.arn not like /WizAccess-Role/'

query_count_suffix = '| stats count(*) as count'
aws_region = os.environ.get('AWS_REGION', 'us-east-1')
ct_log_group_name = os.environ.get('CT_LOG_GROUP_NAME', 'aws-controltower/CloudTrailLogs')
ct_insights_query = os.environ.get('CT_INSIGHTS_QUERY', ct_default_query)
target_cw_log_group = os.environ.get('CW_LOG_GROUP', 'aws-org-cloudtrail/AWSControlTowerExecution')
target_cw_log_kms_arn = os.environ.get('CW_LOG_KMS', None)
platform_alarm_function_arn = os.environ.get('PLATFORM_ALARM_ARN', None)


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


def start_cw_insights_query(log_group_name, insights_query, query_start, query_end, logs_client=None):
    """
    Function to trigger the CloudWatch insights query
    :param log_group_name: name of log group to query
    :param insights_query: query to be run against the log group
    :param query_start: query window start time in epoch format
    :param query_end: query window end time in epoch format
    :param logs_client: optional boto3 client for CW logs
    :return: cw_insights_query_id: string containing the returned query ID
    """
    cw_insights_query_id = None
    if logs_client is None:
        logs_client = boto3.client('logs', region_name=aws_region)

    try:
        logger.info(f'querying log group {log_group_name} with {insights_query} starting '
                    f'{query_start} ending {query_end}')
        response = logs_client.start_query(
            logGroupName=log_group_name,
            startTime=query_start,
            endTime=query_end,
            queryString=insights_query,
            limit=ct_query_max_row_limit
        )
        code = response['ResponseMetadata']['HTTPStatusCode']
        if code == 200:
            logger.info(f'query started successfully')
            cw_insights_query_id = response.get('queryId', None)
        else:
            logger.warning(response)
    except ClientError as e:
        logger.error('Unexpected error: %s' % e)
    return cw_insights_query_id


def get_cw_insights_query_results(insights_query_id, logs_client=None):
    """
    Function to trigger the CloudWatch insights query
    :param insights_query_id: ID of insights query to get results for
    :param logs_client: optional boto3 client for CW logs
    :return: cw_insights_query_result: query results
    """
    total_wait_time = 0
    query_incomplete = True
    cw_insights_query_result = None
    if logs_client is None:
        logs_client = boto3.client('logs', region_name=aws_region)

    try:
        while query_incomplete or total_wait_time >= max_query_wait_time:
            logger.info(f'getting result for insights query {insights_query_id}')
            response = logs_client.get_query_results(
                queryId=insights_query_id
            )
            code = response['ResponseMetadata']['HTTPStatusCode']
            if code == 200:
                logger.info(f'query check returned a successful code 200')
                query_status = response.get('status', None)
                if query_status == 'Complete':
                    logger.info(f'query complete and result returned successfully')
                    cw_insights_query_result = response.get('results')
                    query_incomplete = False
                elif query_status in ['Scheduled', 'Running']:
                    logger.info(f'query is still incomplete - waiting for {str(query_wait_time)} seconds to retry')
                    total_wait_time = total_wait_time + query_wait_time
                    time.sleep(query_wait_time)
                else:
                    logger.warning(f'query in unexpected state of {str(query_status)} - breaking loop')
                    break
            else:
                logger.warning('unexpected response from query check')
                logger.warning(response)
                break

    except ClientError as e:
        logger.error('Unexpected error: %s' % e)
    return cw_insights_query_result


def get_cw_insights_row_count(log_group_name, insights_query, query_start, query_end):
    """
    Function to trigger the CloudWatch insights query
    :param log_group_name: name of log group to query
    :param insights_query: query to be run against the log group
    :param query_start: query window start time in epoch format
    :param query_end: query window end time in epoch format
    :return: row_count: integer containing row count
    """
    row_count_query = f'{insights_query} {query_count_suffix}'
    count_query_id = start_cw_insights_query(log_group_name, row_count_query, query_start, query_end)
    count_result = get_cw_insights_query_results(count_query_id)
    if count_result is not None and len(count_result) > 0:
        row_count = int(count_result[0][0].get('value', 0))
    else:
        row_count = 0
    return row_count


def initialise_target_log_group(cw_log_group=target_cw_log_group, logs_client=None):
    """
    Function to initialise the CloudWatch log group if it does not exist
    :param cw_log_group: string name of the target CW log group
    :param logs_client: optional boto3 client for CW logs
    :return: nothing
    """
    if logs_client is None:
        logs_client = boto3.client('logs', region_name=aws_region)

    try:
        matching_log_groups = logs_client.describe_log_groups(logGroupNamePrefix=cw_log_group).get('logGroups', [])
        if len(matching_log_groups) == 0:
            logger.info(f'cloudwatch log group {target_cw_log_group} does not exist - creating')
            if target_cw_log_kms_arn is None:
                create_response = logs_client.create_log_group(logGroupName=target_cw_log_group)
            else:
                create_response = logs_client.create_log_group(
                    logGroupName=target_cw_log_group,
                    kmsKeyId=target_cw_log_kms_arn
                )
            if create_response.get('ResponseMetadata', {}).get('HTTPStatusCode', None) == 200:
                # We need to retain the data for 1 year / 365 days
                logs_client.put_retention_policy(logGroupName=target_cw_log_group, retentionInDays=365)
                logger.info(f'cloudwatch log group {target_cw_log_group} created successfully')

            if platform_alarm_function_arn is not None:
                # Now add our subscription filter
                logger.info(f'adding cloudwatch log group subscription filter for platform alarm')
                filter_response = logs_client.put_subscription_filter(
                    logGroupName=target_cw_log_group,
                    filterName='PlatformAlarmFilterPermissions',
                    filterPattern='{(($.errorCode=AccessDenied) && ($.errorMessage=*AWSControlTowerExecution*)) || '
                                  '(($.eventName=UpdateAssumeRolePolicy) && '
                                  '($.requestParameters.roleName=*AWSControlTowerExecution*))}',
                    destinationArn=platform_alarm_function_arn,
                )
                if filter_response.get('ResponseMetadata', {}).get('HTTPStatusCode', None) == 200:
                    logger.info(f'cloudwatch log group subscription filter created successfully')
        else:
            logger.info(f'cloudwatch log group {target_cw_log_group} already exists - no initialisation required')

    except ClientError as e:
        logger.error('Unexpected error: %s' % e)


def build_log_stream_name(start_time, end_time):
    """
    Function to build the names for a CloudWatch log stream
    :param start_time: integer with epoch time stamp
    :param end_time: integer with epoch time stamp
    :return: stream_name: string name of the log stream based on the query start/end times
    """
    start_time_string = datetime.fromtimestamp(start_time).strftime('%Y%m%d_%H%M%S')
    end_time_string = datetime.fromtimestamp(end_time).strftime('%Y%m%d_%H%M%S')
    stream_name = f'{start_time_string}-{end_time_string}'
    return stream_name


def initialise_target_log_stream(start_time, end_time, logs_client=None):
    """
    Function to initialise the CloudWatch log stream if it does not exist
    :param start_time: integer with epoch time stamp
    :param end_time: integer with epoch time stamp
    :param logs_client: optional boto3 client for CW logs
    :return: nothing
    """
    if logs_client is None:
        logs_client = boto3.client('logs', region_name=aws_region)

    try:
        stream_name = build_log_stream_name(start_time, end_time)
        log_stream_exists = True if len(logs_client.describe_log_streams(
            logGroupName=target_cw_log_group,
            logStreamNamePrefix=stream_name
        ).get('logStreams', [])) == 1 else False
        if log_stream_exists:
            logger.info(f'cloudwatch log stream {stream_name} already exists - no initialisation required')
        else:
            logger.info(f'cloudwatch log stream {stream_name} does not exist - creating')
            create_response = logs_client.create_log_stream(
                logGroupName=target_cw_log_group,
                logStreamName=stream_name
            )
            if create_response.get('ResponseMetadata', {}).get('HTTPStatusCode', None) == 200:
                logger.info(f'cloudwatch log stream {stream_name} created successfully')

    except ClientError as e:
        logger.error('Unexpected error: %s' % e)


def write_cw_logs(start_time, end_time, log_events, logs_client=None):
    """
    Function to write the log event data to the target log stream
    :param start_time: integer with epoch time stamp
    :param end_time: integer with epoch time stamp
    :param log_events: list of dictionaries containing the log events
    :param logs_client: optional boto3 client for CW logs
    :return: nothing
    """
    if logs_client is None:
        logs_client = boto3.client('logs', region_name=aws_region)
    stream_name = build_log_stream_name(start_time, end_time)

    try:
        # Split the event writes into batches so as not to breach the put log events limits
        for i in range(0, len(log_events), max_batch_cw_put_events):
            # Now write our data to the log stream
            log_events_batch = log_events[i:i + max_batch_cw_put_events]
            put_events_response = logs_client.put_log_events(
                logGroupName=target_cw_log_group,
                logStreamName=stream_name,
                logEvents=log_events_batch
            )
            response_code = put_events_response.get('ResponseMetadata', {}).get('HTTPStatusCode', None)
            if response_code == 200:
                batch_size = len(log_events_batch)
                logger.info(f'successfully logged {str(batch_size)} events to stream {stream_name}')
            else:
                logger.error(f'unexpected put events response code: {str(response_code)}')

    except ClientError as e:
        logger.error('Unexpected error: %s' % e)


def slice_time_range(start_time, end_time):
    """
    Function to take a start and end time range and split it into smaller slices that are below the max
    row limits in CloudWatch log insights
    :param start_time: integer with epoch time stamp
    :param end_time: integer with epoch time stamp
    :return: range_records: list of dictionaries containing the slices time ranges to be used for insight queries
    """
    range_records = []
    rows_above_threshold = True
    range_divider = 2  # This determines how we repeatedly divide up the range until we are below the threshold
    loop_division_count = 0
    time_diff = end_time - start_time
    while rows_above_threshold:
        range_records = []
        loop_division_count = loop_division_count + range_divider
        time_diff_split = int(time_diff / loop_division_count)
        all_splits_below_threshold = True
        for i in list(range(0, loop_division_count)):
            if i == 0:
                range_start = start_time
            else:
                range_start = start_time + (i * time_diff_split)
            if i == loop_division_count - 1:
                range_end = end_time
            else:
                range_end = range_start + time_diff_split - 1
            range_records.append({'start_time': range_start, 'end_time': range_end})
            range_row_count = get_cw_insights_row_count(ct_log_group_name, ct_insights_query, range_start, range_end)

            if range_row_count > ct_query_max_row_limit:
                # Oh dear we still have too many records in one of the ranges - we continue with smaller splits
                all_splits_below_threshold = False

        if all_splits_below_threshold:
            # We can now break out of the while loop
            rows_above_threshold = False
            logger.info(f'time range successfully split into {str(loop_division_count)}')
            logger.info(f'{str(range_records)}')
        else:
            logger.info(f'time range split into {str(loop_division_count)} is still too large - trying smaller range')
            logger.info(f'{str(range_records)}')

    return range_records


def main(query_start_time=None, query_end_time=None):

    if query_start_time is None or query_end_time is None:
        # If we have not received a JSON payload via the Lambda handler, then we check for env vars instead
        query_start_time = os.environ.get('QUERY_START_TIME', None)
        query_end_time = os.environ.get('QUERY_START_TIME', None)
    else:
        logger.info(f'query window provided from Lambda payload {query_start_time} {query_end_time}')

    if query_start_time is None or query_end_time is None:
        # If we still have no start and end times after checking for env vars, then we use the last full hour
        last_hour_date = datetime.utcnow() - timedelta(hours=1)
        last_hour_start_date_string = last_hour_date.strftime('%Y-%m-%d %H:00:00')
        current_hour_start_date_string = now.strftime('%Y-%m-%d %H:00:00')
        timestamp_format = '%Y-%m-%d %H:%M:%S'
        query_start_time = int((datetime.strptime(
            last_hour_start_date_string, timestamp_format) - epoch).total_seconds()
        )
        query_end_time = int((datetime.strptime(
            current_hour_start_date_string, timestamp_format) - epoch).total_seconds()
        )
        logger.info(f'query window calculated as last full hour {query_start_time} {query_end_time}')
    else:
        logger.info(f'query window provided from environment variables {query_start_time} {query_end_time}')


    insights_row_count = get_cw_insights_row_count(
        ct_log_group_name, ct_insights_query, query_start_time, query_end_time
    )

    if insights_row_count is None:
        logger.error('unexpected response returned when performing row count check')
        sys.exit(1)

    sliced_times = []
    if insights_row_count > ct_query_max_row_limit:
        logger.info(f'row count is {str(insights_row_count)} which is above the report limits - slicing required')
        sliced_times = slice_time_range(query_start_time, query_end_time)
    else:
        logger.info(f'row count is {str(insights_row_count)} which is below the report limits - proceeding')
        sliced_times.append({'start_time': query_start_time, 'end_time': query_end_time})

    for time_slice in sliced_times:
        query_results = []
        start_time = time_slice.get('start_time')
        end_time = time_slice.get('end_time')
        query_id = start_cw_insights_query(ct_log_group_name, ct_insights_query, start_time, end_time)
        query_result = get_cw_insights_query_results(query_id)
        if query_result is not None:
            for row in query_result:
                message_value, epoch_timestamp = None, None
                for field in row:
                    if field.get('field', None) == '@message':
                        # message_value = json.loads(field.get('value', {}))
                        message_value = field.get('value', '{}')
                    if field.get('field', None) == '@timestamp':
                        timestamp_value = field.get('value', '')
                        if '.' in timestamp_value:
                            timestamp_value = timestamp_value.split('.')[0]
                        timestamp_format = '%Y-%m-%d %H:%M:%S'
                        epoch_timestamp = (datetime.strptime(timestamp_value, timestamp_format) - epoch).total_seconds()

                # We write a list of dictionaries using epoch timestamps that can be re-written to CloudWatch
                query_results.append({
                    'timestamp': int(epoch_timestamp) * 1000,
                    'message': message_value
                })

        initialise_target_log_group()
        initialise_target_log_stream(start_time, end_time)

        if len(query_results) > 0:
            # We have results from this time slice that we need to write to CloudWatch
            chronological_results = sorted(query_results, key=lambda d: d['timestamp'])
            write_cw_logs(start_time, end_time, chronological_results)

    # If we get this far without an exception, then we have completed successfully
    return f'Main function completed successfully'


def lambda_handler(event, context):
    # Function for when launched by Lambda
    # This will accept a JSON payload that includes query_start_time and query_end_time
    # with epoch timestamps i.e. query_start_time = 1698307816, query_end_time = 1699355463
    global now
    global logger
    query_start_time, query_end_time = None, None
    now = datetime.utcnow()
    logger = get_logger()
    logger.info(f'Event = {event}')
    logger.info(f'Context = {str(context)}')
    for message in event.get('Records', [{}]):
        message_id = message.get('messageId', None)
        message_body = message.get('body', None)
        if message_body:
            message_body = json.loads(message_body)
            query_start_time = message_body.get('query_start_time', None)
            query_end_time = message_body.get('query_end_time', None)
        if message_id and query_start_time and query_end_time:
            return main(query_start_time=query_start_time, query_end_time=query_end_time)
        elif message_id and (query_start_time is None or query_end_time is None):
            logging.error('Invalid message body received')
            raise
        else:
            return main()
    return main()


if __name__ == '__main__':
    # Function for when launched from local Python interpreter
    main()
