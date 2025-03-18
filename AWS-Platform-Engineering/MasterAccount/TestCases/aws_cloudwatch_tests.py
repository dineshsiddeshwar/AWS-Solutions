def aws_cw_logs_check_if_metric_filter_is_created(logs_client, filter_name):
    try:
        response = logs_client.describe_metric_filters()
        if len(response['metricFilters']) > 0:
            for item in response['metricFilters']:
                if item['filterName'] == filter_name:
                    print(item)
                    return True
        else:
            return False

    except Exception as e:
        print("error occured while aws_cw_logs_check_if_metric_filter_is_created and error is {}".format(e))
        return False
    
def aws_cw_check_if_alarm_is_created(cloudwatch_client, alarm_name):
    try:
        response = cloudwatch_client.describe_alarms(
            AlarmNames=[
                alarm_name,
            ]
        )
        if len(response['MetricAlarms']) > 0:
            print(response['MetricAlarms'])
            return True
        else:
            return False

    except Exception as e:
        print("error occured while aws_cw_check_if_alarm_is_created and error is {}".format(e))
        return False

def aws_cw_check_if_log_group_is_created(logs_client, log_group_name):
    try:
        response = logs_client.describe_log_groups(logGroupNamePrefix='/aws/lambda/platform')
        result = response['logGroups']
        while 'nextToken' in response:
            response = logs_client.describe_log_groups(logGroupNamePrefix='/aws/lambda/platform',nextToken=response['nextToken'])
            result.extend(response['logGroups'])
            print(result)
        if result:
            print(result)
            for item in result:
                print(item['logGroupName'])
                if item['logGroupName'] == '/aws/lambda/platform_close_account':
                    return True
            
        else:
            return False

    except Exception as e:
        print("error occured while aws_cw_check_if_log_group_is_created and error is {}".format(e))
        return False