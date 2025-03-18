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
        file_name = 'notebooks-to-be-deleted.csv'
        with open("/tmp/"+file, 'rb') as file:
           content = file.read()     
        bucket = ''
        key = 'MLNotebooks/'+accountid+'/'+file_name
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
    
def lambda_handler(event, context):
    try:
        region_list = ['us-east-1']
        sts_client = boto3.client('sts')
        accountid = sts_client.get_caller_identity()["Account"]
        current_date = datetime.now()
        threshold_date = current_date - timedelta(days=90)
        rows = []
        for region in region_list:
            sg_client = boto3.client('sagemaker', region_name=region)
            sg_response = sg_client.list_notebook_instances(MaxResults=100)
            notebook_instances = sg_response['NotebookInstances']
            if sg_response['NotebookInstances'] != 0:
                while 'NextToken' in sg_response.keys():
                    sg_response = sg_client.list_notebook_instances(NextToken=sg_response['NextToken'],MaxResults=100)
                    notebook_instances.extend(sg_response['NotebookInstances'])
                print(f"Number of Notebook Instances available in {region} is {len(notebook_instances)}")
                stopped_instances = []
                older_instances = []
                
                for instances in notebook_instances:
                    child_row = []
                    
                    child_row = [instances['NotebookInstanceName'],instances['NotebookInstanceArn'],instances['NotebookInstanceStatus'],instances['InstanceType'],instances['CreationTime'],instances['LastModifiedTime']]
                    if instances['NotebookInstanceStatus'] in ['Stopped','Failed','Stopping']:
                        stopped_instances.append(instances['NotebookInstanceArn'])
                        rows.append(child_row)
                    if instances['NotebookInstanceStatus'] in ['Updating','InService']:
                        if instances['LastModifiedTime'] < threshold_date:
                            older_instances.append(instances['NotebookInstanceArn'])
                            rows.append(child_row)
                    
        csv_headers = ['NAME','ARN','status','InstanceType','CreatioTime','ModifiedTime']
        file_name = 'MLNotebooks-to-be-deleted.csv'
        with open("/tmp/"+file_name, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(csv_headers)
            csv_writer.writerows(rows)
        status = upload_to_s3(file_name,accountid)
        if status:
            os.remove("/tmp/"+file_name)
        for instances in stopped_instances:
            delete_response = sg_client.delete_notebook_instance(NotebookInstanceName=instances.split('/')[1])   
        for instances in older_instances:
            stop_response = sg_client.stop_notebook_instance(NotebookInstanceName=instances.split('/')[1])    
    except Exception as ex:
        raise ex