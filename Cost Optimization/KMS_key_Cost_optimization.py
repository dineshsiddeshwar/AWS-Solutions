##################################################################################################
#                                                                                                #
#                                                                                                #
#  Note:- If there are lots of keys then There are high chances of automation getting Timed out  #
#                                                                                                #
#                                                                                                #
##################################################################################################

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
        file_name = 'KMS-to-be-deleted.csv'
        with open("/tmp/"+file, 'rb') as file:
           content = file.read()     
        bucket = ''
        key = 'KMS/'+accountid+'/'+file_name
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


# def delete_disbale_km(kms_client,key):
#     try:
#         disbale_response = kms_client.disable_key(KeyId=key)
#         if disbale_response:
#             delete_response = kms_client.schedule_key_deletion(KeyId=key)
#             if delete_response:
#                 return True
#             else:
#                 raise "Something went wrong when deleting the key. Please check"
#         else:
#             raise "Something went wrong when disbling the key. Please check"
#     except Exception as ex:
#         if 'KMSInvalidStateException' in str(ex):
#             return True
#         raise ex
    
def lambda_handler(event, context):
    try:
        #print("Start Time:- {}".format(datetime.datetime.now()))
        regions = ['us-east-1']
        sts_client = boto3.client('sts')
        accountid = sts_client.get_caller_identity()["Account"]
        rows = []
        for region in regions:
            ct_client = boto3.client('cloudtrail',region_name=region)
            kms_client = boto3.client('kms')
            ninety_days_ago = datetime.now() - timedelta(days=90)
            # start_time = ninety_days_ago.strftime('%Y-%m-%dT%H:%M:%SZ')
            # end_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
            ct_response = ct_client.lookup_events(
                                    LookupAttributes=[
                                        {'AttributeKey': 'EventSource', 'AttributeValue': 'kms.amazonaws.com'}
                                    ],
                                    StartTime=ninety_days_ago,
                                    EndTime=datetime.now(),
                                    MaxResults=50)
            events = ct_response['Events']
            while 'NextToken' in ct_response.keys():
                ct_response = ct_client.lookup_events(
                                    LookupAttributes=[
                                        {'AttributeKey': 'EventSource', 'AttributeValue': 'kms.amazonaws.com'}
                                    ],
                                    StartTime=ninety_days_ago,
                                    EndTime=datetime.now(),
                                    NextToken=ct_response['NextToken'],
                                    MaxResults=50)
                events.extend(ct_response['Events'])
            used_key_list = []
            for event in events:
                
                event_data = json.loads(event['CloudTrailEvent'])
                event_name = event_data.get('eventName', '')
                resources = event_data.get('resources',False)
                if event_name in ['GenerateDataKey', 'Encrypt', 'Decrypt', 'ReEncrypt','GenerateDataKeyWithoutPlaintext']:
                    if resources:
                        for res in resources:
                            used_key_list.append(res['ARN'])
            disabled_deletion_keys = []
            enabled_keys = []
            list_kms_keys = kms_client.list_keys(Limit=100)
            key_list = list_kms_keys['Keys']
            while 'NextMarker' in list_kms_keys.keys():
                    list_kms_keys = kms_client.list_keys(Limit=100,Marker=list_kms_keys['NextMarker'])
                    key_list.extend(list_kms_keys['Keys'])
            unused_key_list = []
            for key in key_list:
                if key['KeyId'] not in used_key_list:
                    unused_key_list.append(key['KeyId'])
            
            for key in unused_key_list:
                kms_response_dict = kms_client.describe_key(KeyId=key)
                kms_respose = kms_response_dict['KeyMetadata']
                if kms_respose['KeyManager'] == 'CUSTOMER':
                    if kms_respose['Enabled']:
                        enabled_keys.append(key)
                    if kms_respose['KeyState'] in ['Unavailable','PendingDeletion','Disabled','PendingReplicaDeletion']:
                        disabled_deletion_keys.append(key)
                    
                    # for tag in tag_response['Tags']:
                    #     break_loop = False
                    #     if 'cloudformation' in tag['Key']:
                    #         break_loop = True
                    #         break
                    # if break_loop:
                    #     continue 
                    
                    validto = kms_respose.get('ValidTo','NA')
                    deletiondate = kms_respose.get('DeletionDate','NA')
                    rows.append([key,region,kms_respose['KeyId'],kms_respose['Description'],kms_respose['KeyState'],kms_respose['CreationDate'],validto,deletiondate])
                    if kms_respose['KeyState'] not in ['PendingDeletion','PendingReplicaDeletion']:
                        pass
                        #delete_kms_key = delete_disbale_km(kms_client,kms_respose['KeyId'])
        csv_headers = ['ARN','Region','KeyID','Description','State','CreationDate','ValidTo','DeletionDate']
        file_name = 'KMS-to-be-deleted.csv'
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