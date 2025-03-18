import boto3
import time
from collections import Counter
import datetime
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr
import calendar
import os

def lambda_handler(event, context):
    
    getLatestData()
    
    return {
        "message" : "success"
    }

def getLatestData():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table_name = get_ssm_param('ScoreCardDBTableName')
    table = dynamodb.Table(table_name)
     # Get the start and end timestamps for the current month in milliseconds
    now = datetime.datetime.now()
    start_of_month = datetime.datetime(now.year, now.month, 1)
    end_of_month = datetime.datetime(now.year, now.month+1, 1) - datetime.timedelta(days=1)
    start_timestamp = int(start_of_month.timestamp() * 1000)
    end_timestamp = int(end_of_month.timestamp() * 1000)
    # Initialize dictionaries to hold the latest run for each db_name
    latest_runs = {}
    no_db_name_items = []
    # Scan the DynamoDB table for the latest run of each db_name within the current month
    last_evaluated_key = None
    while True:
        if last_evaluated_key:
            response = table.scan(
                FilterExpression=Key('unix_timestamp').between(start_timestamp, end_timestamp),
                ExclusiveStartKey=last_evaluated_key
            )
        else:
            response = table.scan(
                FilterExpression=Key('unix_timestamp').between(start_timestamp, end_timestamp)
            )
        for item in response['Items']:
             
            db_name = item['db_name'] if 'db_name' in item else None
            timestamp = item['unix_timestamp']
            status = item['status']
            failure_reason = item.get('failure_reason', None) 
            db_engine = item.get('db_engine', None) 
            account = item.get('account', None) 
            region_from_dynamo= item.get('region', None)


            # Update the latest row for this db_name
            if db_name and db_engine:
                if db_name not in latest_runs or latest_runs[db_name]['unix_timestamp'] < timestamp:
                    latest_runs[db_name] = {'unix_timestamp': timestamp, 'status': status, 'account':account ,'failure_reason': failure_reason, 'db_engine': db_engine, 'region': region_from_dynamo}
            else:
                no_db_name_items.append({'unix_timestamp': timestamp, 'status': status, 'failure_reason': failure_reason})
        last_evaluated_key = response.get('LastEvaluatedKey', None)
        if not last_evaluated_key:
            break
        
    # Separate the latest runs into two lists based on status
    latest_passes = []
    latest_failures = []
    db_names = []
    missingInstances = []
    
    for db_name, item in latest_runs.items():
        account=item["account"]
        region=item["region"]
        db_names.append((db_name,account,region))
        if item['status'] == 'Pass':
            latest_passes.append({db_name: item})
        else:
            
            latest_failures.append({db_name: item})
            
    configData = get_rds_config_data()
    
    for configItem in configData:
        isPresent=False
        for dynamoitem in db_names:
            (db_name_d,account_d,region_d)=dynamoitem
            
            if configItem['ResourceName'] ==db_name_d and configItem['SourceAccountId'] ==account_d and configItem['SourceRegion'] ==region_d:
                isPresent=True
                break
        if isPresent==False:
            missingInstances.append((configItem['ResourceName'] ,configItem["SourceAccountId"],configItem["SourceRegion"]))
                
    print(missingInstances)

                
            
    # Append the items without a db_name to the failures list
    # latest_failures.extend(no_db_name_items)

        
    pass_str = f"Total Passed : {summary(latest_passes)}"
    fail_str = f"Failed, during execution : {summary(latest_failures, numberMissing = len(missingInstances))}"
    missing_str = f"Failed, did not run : {len(missingInstances)}"
    total_fail_str = f"Total Failures: {len(latest_failures) + len(missingInstances)}"


    failure_table_html = create_html_table(latest_failures)
    missing_html_table = create_missing_html_table(missingInstances)

    
    
    year_str = datetime.datetime.now().strftime('%Y')
    month_str = datetime.datetime.now().strftime('%B')
    
    data_str = ""
    
    try:
        data_str+= fr"""<p> Total RDS Count from Config {get_rds_count_config()}</p> """
        print(data_str)
    except:
        data_str+= fr"""<p> Could not retrieve total RDS Count from Config </p> """
        
    
    
    subject = f"AWS@Shell RDS Compliance Scanning Status Report - {month_str} {year_str}"
    send_email(subject,data_str,pass_str,fail_str,missing_str,total_fail_str,failure_table_html,missing_html_table,['syed.shakir@shell.com','GX-ITSO-SOM-ET-FND-CHD-OPS-LEADS@shell.com','Ramdas-Rajesh.Ramdas@shell.com'])
    
def create_missing_html_table(data):
    table_html = '<table style="border-collapse: collapse; border: 1px solid black;">\n'
    table_html += '<tr><th style="border: 1px solid black;">Database Name</th><th style="border: 1px solid black;">Database Account</th><th style="border: 1px solid black;">Database Region</th></tr>\n'
    for entry in data:
        table_html += '<tr>'
        table_html += '<td style="border: 1px solid black;">{}</td>'.format(entry[0])
        table_html += '<td style="border: 1px solid black;">{}</td>'.format(entry[1])
        table_html += '<td style="border: 1px solid black;">{}</td>'.format(entry[2])
        table_html += '</tr>\n'
    table_html += '</table>'
    return table_html
    
def summary(data,numberMissing = 0):
    actual_count = len(data) 
    
    #including non runs.
    total_count = len(data) + numberMissing
    engines = {}
    for item in data:
        # 
        db_engine = item[list(item.keys())[0]]['db_engine']
        
        
        if db_engine in engines:
            engines[db_engine] += 1
        else:
            engines[db_engine] = 1
    

    engine_summary = ', '.join([f"{engine}: {count}" for engine, count in engines.items()])
    summary_str = f"{actual_count}, ({engine_summary})"
    return summary_str
    
def create_html_table(data):
    
    
    if not data:
        return ''
    html = '<table style="border-collapse: collapse;">'
    # Create the table header row using the keys from the first JSON object
    header_keys = list(data[0].values())[0].keys()
    html += '<tr>'
    html += f'<th style="border: 1px solid black; padding: 5px;">db_name</th>'

    for key in header_keys:
        html += f'<th style="border: 1px solid black; padding: 5px;">{key}</th>'
    html += '</tr>'
    # Create a table row for each JSON object
    for json_obj in data:
        db_name, db_data = list(json_obj.items())[0]
        timestamp = datetime.datetime.fromtimestamp(int(db_data['unix_timestamp']) / 1000)
        timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')
        db_data['unix_timestamp'] = timestamp_str
        html += '<tr>'
        html += f'<td style="border: 1px solid black; padding: 5px;">{db_name}</td>'
        for value in db_data.values():
            # )
            html += f'<td style="border: 1px solid black; padding: 5px;">{value}</td>'
        html += '</tr>'
    html += '</table>'
    
    return html
def get_ssm_param(parameter_name):
    """
    param: parametre_name
    return: parameter value for the given param name
    """
    try:
        ssm_client = boto3.client("ssm")
        parameter = ssm_client.get_parameter(Name=parameter_name,WithDecryption=True)
        if parameter:
            return parameter['Parameter']['Value']
    except Exception as ex:
        return ex
            
def send_email(subject, data_str,pass_str,fail_str,missing_str,total_fail_str,failure_table_html,missing_html_table, recipient):
    ses = boto3.client('ses', region_name='us-east-1')
    receiverid_name=get_ssm_param('DPSOMDL')
    recipient.append(receiverid_name)
    senderid_name=get_ssm_param('sender_id')
    response = ses.send_email(
        Destination={
            'ToAddresses': recipient,
        },
        Message={
            'Body': {
                'Html': {
                    'Charset': 'UTF-8',
                    'Data': f"""{data_str}<p>{pass_str}</p> <p>{fail_str}</p> {failure_table_html} 
                    <p>{missing_str}</p>
                    <p> The following instances were not evaluated. Please review.</p> 
                    {missing_html_table}
                    <p>{total_fail_str}</p>
                    
                    """
                },
            },
            'Subject': {
                'Charset': 'UTF-8',
                'Data': subject,
            },
        },
        Source=senderid_name,
    )
    return response

def count_db_engines(data):
    engine_counts = {}
    for entry in data:
        engine = entry['db_engine']
        if engine in engine_counts:
            engine_counts[engine] += 1
        else:
            engine_counts[engine] = 1
    engine_counts_str = ', '.join([f'{key}: {value}' for key, value in engine_counts.items()])
    return engine_counts_str
    
def get_rds_count_config():
    return len(get_rds_config_data())
    
def get_rds_config_data():

  
    # Create a boto3 client for the Config service
    
    config_client = boto3.client('config')
    # Define the aggregator name and query string
    aggregator_name = 'aws-controltower-ConfigAggregatorForOrganizations'
    query_string = """
    SELECT
    count(*)
    WHERE
    resourceType = 'AWS::RDS::DBInstance'
    """
    paginator = config_client.get_paginator('list_aggregate_discovered_resources')
    # Run the query on the aggregator
    response = paginator.paginate(
      ConfigurationAggregatorName=aggregator_name,
      ResourceType='AWS::RDS::DBInstance')
    result_array=[]
    for page in response:
        print(page)
        result_array += page['ResourceIdentifiers']
    # Print the query results
    
    return result_array
