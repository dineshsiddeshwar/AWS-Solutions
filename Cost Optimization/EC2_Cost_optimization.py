import json
import boto3
import csv
import os
BUCKET = ''
def upload_to_s3(file,accountid):
    '''
    This function creates a file and upload to s3 bucket
    '''
    try:
        print("Inside s3 bucket")
        #s3 = boto3.resource('s3')
        s3_client = boto3.client('s3')
        file_name = 'EC2-to-be-deleted.csv'
        with open("/tmp/"+file, 'rb') as file:
           content = file.read()     
        bucket = BUCKET
        key = 'EC2/'+accountid+'/'+file_name
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
        #regions = ['us-east-1']
        sts_client = boto3.client('sts')
        accountid = sts_client.get_caller_identity()["Account"]
        tr_client = boto3.client('support')
        #arn:aws:trustedadvisor:::check/Qch7DwouX1
        tr_response = tr_client.describe_trusted_advisor_check_result(checkId='Qch7DwouX1',language='en')
        
        rows = []
        metadata = tr_response['result']['flaggedResources']
        rows = []
        for res in metadata:
            region = res['metadata'][0]
            instance = res['metadata'][1]
            name = res['metadata'][2]
            type_ins = res['metadata'][3]
            saveings = res['metadata'][4]
            rows.append([region,instance,name,type_ins,saveings])
        csv_headers = ["Region","InstanceID","Name","Type","Estimated Monthly Savings"]
        file_name = 'Ec2-to-be-deleted.csv'
        with open("/tmp/"+file_name, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(csv_headers)
            csv_writer.writerows(rows)
        status = upload_to_s3(file_name,accountid)
        if status:
            os.remove("/tmp/"+file_name)
               
        return True
    except Exception as ex:
        raise ex