import json
import boto3
import datetime
from datetime import date, datetime, timedelta
import csv
import os


def upload_to_s3(file,accountid):
    '''
    This function creates a file and upload to s3 bucket
    '''
    try:
        print("Inside s3 bucket")
        #s3 = boto3.resource('s3')
        s3_client = boto3.client('s3')
        file_name = 'sns-to-be-deleted.csv'
        with open("/tmp/"+file, 'rb') as file:
           content = file.read()        
        bucket = ''
        key = 'SNSTopics/'+accountid+'/'+file_name
        # s3.Bucket(bucket).upload_file("/tmp/"+file, key+file)
        s3_response = s3_client.put_object(
                                Body=content,
                                Bucket=bucket,
                                Key=key)
                                #ServerSideEncryption='aws:kms')
        if s3_response:
            return True
    except Exception as ex:
        print("There is something went wrong in uploading s3 bucket")
        raise ex

def get_number_of_messages_published(topic_arn,cw_client):
    try:
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=90)
        
        response = cw_client.get_metric_statistics(
            Namespace='AWS/SNS',
            MetricName='NumberOfMessagesPublished',
            Dimensions=[
                {'Name': 'TopicName', 'Value': topic_arn.split(':')[-1]}
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=86400,  # Daily metrics
            Statistics=['Sum']
        )
        
        # Check if we have any data, return 0 if no data
        if response['Datapoints']:
            total_messages = sum(datapoint['Sum'] for datapoint in response['Datapoints'])
        else:
            total_messages = 0
        
        return total_messages
    except Exception as ex:
        raise ex

def list_sns_topics(sns_client):
    try:
        sns_response = sns_client.list_topics()
        topic = sns_response['Topics']
        while 'NextToken' in sns_response.keys():
            sns_response = sns_client.list_topics(NextToken=sns_response['NextToken'])
            topic.extend(sns_response['Topics'])
        return topic
    except Exception as ex:
        raise ex


def delete_topics(topic,sns_client):
    try:
        response = sns_client.delete_topic(TopicArn=topic)
        return response
    except Exception as ex:
        raise ex
def lambda_handler(event, context):
    try:
        regions = ['us-east-1']
        sts_client = boto3.client('sts')
        accountid = sts_client.get_caller_identity()["Account"]
        
        rows = []
        for region in regions:
            cw_client = boto3.client('cloudwatch', region_name=region)
            sns_client = boto3.client('sns',region_name=region)
            topics = list_sns_topics(sns_client)
            
            filtered_topics = []

            for topic in topics:
                topic_arn = topic['TopicArn']
                total_messages = get_number_of_messages_published(topic_arn,cw_client)
                if total_messages < 1:
                    filtered_topics.append(topic_arn)
                    rows.append([topic_arn,region,accountid])
            for topic in filtered_topics:
                delete_topics(topic,sns_client)
            
        csv_headers = ['ARN','region','Account']
        file_name = 'SNSTOpics-to-be-deleted.csv'
        with open("/tmp/"+file_name, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(csv_headers)
            csv_writer.writerows(rows)
        status = upload_to_s3(file_name,accountid)
        if status:
            os.remove("/tmp/"+file_name)
        
    except Exception as ex:
        print(f"Something wen wrong {str(ex)}")
        raise ex