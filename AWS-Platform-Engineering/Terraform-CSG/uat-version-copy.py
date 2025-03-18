import subprocess
import logging
import json
import time
from datetime import datetime
import pytz
import requests
import urllib.request
import boto3



def lambda_handler(event, context):
    ##Requestjson format
    '''
    request_json = {
        "request_id": 123456,
        "timestamp": "11-apr-30",
        "parent_customername": "redmine",
        "new_customername": "honda",
        "callback_url": "https://echotest.proformprofessionals.com"
    }
    '''
    print(event)
    #file_content = event['body']
    file_content = event
    #file_content = print(event)
    request_json = file_content
    #request_json = json.loads(file_content)
    #request_id = str(request_json["request_id"])
    request_id = event["request_id"]
    
    print("request_id = {}".format(request_id))
    #env_name = str(request_json.get("env_name", ""))
    env_name = 'uat'
    print("env_name = {}".format(env_name))
    #new_customername= str(request_json.get("new_customername", ""))
    new_customername= event["new_customername"]
    print("new_customername = {}".format(new_customername))
    #callback_url = str(request_json.get("callback_url", ""))
    callback_url = event["callback_url"]
    
    print("callback_url = {}".format(callback_url))
    
    #Private content bucket bucket details
    source_bucket_private = 'uatprivatecontent'
    print("source_bucket_private = {}".format(source_bucket_private))
    #source_customer_private = str(request_json.get("parent_customername", ""))
    source_customer_private = event["parent_customername"]
    print("source_customer_private = {}".format(source_customer_private))
    dest_bucket_private = 'uatprivatecontent'
    print("dest_bucket_private = {}".format(dest_bucket_private))
    dest_customer_private = new_customername
    print("dest_customer_private = {}".format(dest_customer_private))
    
    #Custom-Report content bucket  details
    source_bucket_custom = 'uatprivatecontent'
    print("source_bucket_custom = {}".format(source_bucket_custom))
    #source_customer_custom = str(request_json.get("parent_customername", ""))
    source_customer_custom = event["parent_customername"]
    print("source_customer_custom = {}".format(source_customer_custom))
    dest_bucket_custom = 'uatprivatecontent'
    print("dest_bucket_custom = {}".format(dest_bucket_custom))
    dest_customer_custom = new_customername
    print("dest_customer_private = {}".format(dest_customer_custom))
    
    
    #Customer content bucket bucket details
    source_bucket_content = 'uatproform'
    print("source_bucket_content = {}".format(source_bucket_content))
    source_customer_content = source_customer_private + "-" + env_name
    print("source_customer_content = {}".format(source_customer_content))
    dest_bucket_content = 'uatproform'
    print("dest_bucket_content = {}".format(dest_bucket_content))
    dest_customer_content = new_customername + "-" + env_name
    print("dest_customer_content = {}".format(dest_customer_content))
    
    ##Getting the build Number From the oauth URL of the curesponding env
    r = requests.get(f'https://{source_customer_content}.proformprofessionals.com/auth/test')
    deployment_status = r.text
    build_number = deployment_status[39:]
    #build_number = '12342'
    print("build_number = {}".format(build_number))
    
    
    ##success Response Json format
    customer_copy_response = {
        "request_id": request_id,
        "timestamp": datetime.now(tz=pytz.UTC).strftime('%Y-%m-%d %H:%M:%S %Z'),
        "env_name": env_name,
        "status": 'success',
        "new_customername": dest_customer_private,
        "customer_url": f'https://{dest_customer_content}.proformprofessionals.com'
    }
    
    #print(customer_copy_response)
    customer_copy_error_response = {
        "request_id": request_id,
        "timestamp": datetime.now(tz=pytz.UTC).strftime('%Y-%m-%d %H:%M:%S %Z'),
        "env_name": env_name,
        "status": 'failed',
        "new_customername": dest_customer_private,
        "customer_url": f'https://{dest_customer_content}.proformprofessionals.com'
    }
    
    #print(event['key1'])
    run_command('/opt/python/lib/python3.7/site-packages/aws --version')
    #COPY PRIVATE-CONTENT
    run_command(f'/opt/python/lib/python3.7/site-packages/aws s3 sync s3://{source_bucket_private}/private-content/{source_customer_private} s3://{dest_bucket_private}/private-content/{dest_customer_private} --exclude ''common/job-data/*')
    
    
    
    #COPY Job-Data VERSIONS
    s3 = boto3.resource('s3')
    bucket_name = 'uatprivatecontent'
    dest_bucket_name = 'uatprivatecontent'
    s3_client = boto3.client('s3')

    list_object_response = s3_client.list_object_versions(Bucket=bucket_name,Prefix=f'private-content/{source_customer_private}/common')
    print("Printing  list_object_response = {}".format(list_object_response))
    versions = list_object_response["Versions"]
    versions.sort(key=extract_time, reverse=False)
    source_folder_name = f'private-content/{source_customer_private}/common/job-data'
    dest_folder_name = f'private-content/{dest_customer_private}/common/job-data'
    print("Printing  source_folder_name = {}".format(source_folder_name))
    print("Printing  dest_folder_name = {}".format(dest_folder_name))
    for version in versions:
        version_id = version['VersionId']
        file_key = version['Key']
        is_latest = version['IsLatest']
        
        if source_folder_name not in file_key:
            continue
        
        dest_file_key = file_key.replace(source_folder_name, dest_folder_name)
        print("file_key  = {}".format(file_key))
        print("Copying this key as = {}".format(dest_file_key))
        
        copy_source = {
        'Bucket': bucket_name,
        'Key': file_key,
        'VersionId': version_id,
        'IsLatest': is_latest
        }
        
        s3_client.copy_object(
            ACL='bucket-owner-full-control',
            Bucket=dest_bucket_name,
            CopySource=copy_source,
            Key=dest_file_key
        )

    #Checking the seize of source private content
    path = f'private-content/{source_customer_private}/'
    #bucket = 'version-test-nijo'
 
    s3 = boto3.resource('s3')
    my_bucket = s3.Bucket(source_bucket_private)
    source_prvte_content_total_size = 0

    for obj in my_bucket.objects.filter(Prefix=path):
        source_prvte_content_total_size += obj.size
    print("source_prvte_content_total_size = {}".format(source_prvte_content_total_size))
    
    #Checking the seize of dest private content
    path = f'private-content/{dest_customer_private}/'
    #bucket = 'version-test-nijo'
 
    s3 = boto3.resource('s3')
    my_bucket = s3.Bucket(dest_bucket_private)
    dest_prvte_content_total_size = 0

    for obj in my_bucket.objects.filter(Prefix=path):
        dest_prvte_content_total_size += obj.size
    print("dest_prvte_content_total_size = {}".format(dest_prvte_content_total_size))
    
    private_content_seize_difference = source_prvte_content_total_size - dest_prvte_content_total_size
    print("private_content_seize_difference = {}".format(private_content_seize_difference))
    
    if private_content_seize_difference >=10000000000:
        print("Private Content Destination fileseize less.")
        request_json["deletion_action"] = 'private-content'
        request_json["error"] = 'Private Content Destination fileseize less'
        request_json["status"] = 'failed'
        return return_s3_delete_invoke(request_json)
    else:
        #COPY CUSTOM_REPORT-CONTENT
        run_command(f'/opt/python/lib/python3.7/site-packages/aws s3 sync s3://{source_bucket_custom}/custom-report-content/{source_customer_custom} s3://{dest_bucket_custom}/custom-report-content/{dest_customer_custom}')
        #Checking the seize of source custom-report content
        path = f'custom-report-content/{source_customer_custom}/'
        print("source custom-report-content path = {}".format(path)) 
        #bucket = 'version-test-nijo'
     
        s3 = boto3.resource('s3')
        my_bucket = s3.Bucket(source_bucket_custom)
        source_customreport_content_total_size = 0
    
        for obj in my_bucket.objects.filter(Prefix=path):
            #print("objects of customreport = {} - {}".format(obj, obj.size))
            source_customreport_content_total_size += obj.size
        print("source_customreport_content_total_size = {}".format(source_customreport_content_total_size))
        
        
        
        #Checking the seize of dest custom-report content
        path = f'custom-report-content/{dest_customer_custom}/'
        #bucket = 'version-test-nijo'
     
        s3 = boto3.resource('s3')
        my_bucket = s3.Bucket(dest_bucket_custom)
        dest_customreport_content_total_size = 0
    
        for obj in my_bucket.objects.filter(Prefix=path):
            dest_customreport_content_total_size += obj.size
        print("dest_customreport_content_total_size = {}".format(dest_customreport_content_total_size))
        
        customreport_content_seize_difference = source_customreport_content_total_size - dest_customreport_content_total_size
        print("customreport_content_seize_difference = {}".format(customreport_content_seize_difference))
        if customreport_content_seize_difference >=10000000000:
            print("Custom-Report-Content Destination fileseize less.")
            request_json["deletion_action"] = 'custom-report-content'
            request_json["error"] = 'Custom-Report-Content Destination fileseize less'
            request_json["status"] = 'failed'
            return return_s3_delete_invoke(request_json)
        else:
            #COPY PROFORM-CONTENT
            run_command(f'/opt/python/lib/python3.7/site-packages/aws s3 sync s3://{source_bucket_content}/proform/{source_customer_content} s3://{dest_bucket_content}/proform/{dest_customer_content}')
            run_command(f'/opt/python/lib/python3.7/site-packages/aws s3 cp s3://{source_bucket_content}/proform/{source_customer_content}/{build_number}/css/{source_customer_content}.css s3://{dest_bucket_content}/proform/{dest_customer_content}/{build_number}/css/{dest_customer_content}.css')
            #run_command(f'/opt/python/lib/python3.7/site-packages/aws s3 cp s3://{source_bucket_content}/proform/{source_customer_content}/v2/assets/fonts/{source_customer_private}.css s3://{dest_bucket_content}/proform/{dest_customer_content}/v2/assets/fonts/{dest_customer_private}.css')
            run_command(f'/opt/python/lib/python3.7/site-packages/aws s3 rm s3://{dest_bucket_content}/proform/{dest_customer_content}/{build_number}/css/{source_customer_content}.css')
            
            #Checking the seize of soure proform-customer content
            path = f'proform/{source_customer_content}/'
            #bucket = 'version-test-nijo'
         
            s3 = boto3.resource('s3')
            my_bucket = s3.Bucket(source_bucket_content)
            source_customer_content_total_size = 0
        
            for obj in my_bucket.objects.filter(Prefix=path):
                source_customer_content_total_size += obj.size
            print("source_customer_content_total_size = {}".format(source_customer_content_total_size))
            #Checking the seize of dest proform-customer content
            path = f'proform/{dest_customer_content}/'
            #bucket = 'version-test-nijo'
         
            s3 = boto3.resource('s3')
            my_bucket = s3.Bucket(dest_bucket_content)
            dest_customer_content_total_size = 0
        
            for obj in my_bucket.objects.filter(Prefix=path):
                dest_customer_content_total_size += obj.size
            print("dest_customer_content_total_size = {}".format(dest_customer_content_total_size))
            
            customer_content_seize_difference = source_customer_content_total_size - dest_customer_content_total_size
            print("customer_content_seize_difference = {}".format(customer_content_seize_difference))
            if customer_content_seize_difference >=10000000000:
                print("Customer-proform-Content Destination fileseize less.")
                request_json["deletion_action"] = 'proform-folder'
                request_json["error"] = 'Customer-proform-folder Destination fileseize less'
                request_json["status"] = 'failed'
                return return_s3_delete_invoke(request_json)
            else:
                ##Checking the status of the customer URL
                #url_status = urllib.request.urlopen(f'https://{dest_customer_content}.proformprofessionals.com/login').getcode()
                url_status = urllib.request.urlopen('https://csgsol.proformprofessionals.com/login').getcode()
                print ("url_status  = {}".format(url_status))
                if url_status == 200:
                    print("sending success Response to call back URL.")
                    request_json["error"] = 'none'
                    request_json["status"] = 'success'
                    request_json["deletion_action"] = 'none'
                    return return_s3_copy_status(request_json)
                else:
                    print("URL still not propagated.")
                    request_json["error"] = 'URL propagation delay'
                    request_json["status"] = 'failed'
                    request_json["deletion_action"] = 'none'
                    return return_s3_copy_status(request_json)
    
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def run_command(command):
    command_list = command.split(' ')

    try:
        logger.info("Running shell command: \"{}\"".format(command))
        result = subprocess.run(command_list, stdout=subprocess.PIPE);
        #logger.info("Command output:\n---\n{}\n---".format(result.stdout.decode('UTF-8')))
    except Exception as e:
        logger.error("Exception: {}".format(e))
        return False

    return True
    
def return_s3_copy_status(request_json):
    print("Returning since S3 copy status.")
    '''
    request_json = {
        "request_id": 123456,
        "timestamp": "11-apr-30",
        "env_name": "pfapps",
        "parent_customername": "csgsol",
        "new_customername": "samsung",
        "callback_url": "https://echotest.proformprofessionals.com"
        "error": true,
        "status": "Customer already exist"
    }
    '''
    print("Invoking response lambda.")
    client = boto3.client('lambda')
    uat_s3_copy_response = client.invoke(
        FunctionName='arn:aws:lambda:us-east-1:876984124922:function:UAT-Customer-copy-response',
        InvocationType='Event',
        Payload=json.dumps(request_json)
    )
    
    print("uat_s3_copy_lambda_response = {}".format(uat_s3_copy_response))
    return {"status": "S3 copy status"}
    
def get_size(bucket, path):
    s3 = boto3.resource('s3')
    my_bucket = s3.Bucket(bucket)
    total_size = 0

    for obj in my_bucket.objects.filter(Prefix=path):
        total_size = total_size + obj.size

    return total_size    
    print("total_size = {}".format(total_size))
    
   

def send_api_response(callback_url, customer_copy_response):
    response = requests.post(
        url=callback_url, 
        data=json.dumps(customer_copy_response),
        headers={'Content-Type': "application/json"}
    )

def send_api_error_response(callback_url, customer_copy_error_response):
    response = requests.post(
        url=callback_url, 
        data=json.dumps(customer_copy_error_response),
        headers={'Content-Type': "application/json"}
    )
    
def extract_time(json):
    try:
        return json['LastModified']
    except KeyError:
        return 0   

def return_s3_delete_invoke(request_json):
    print("Invoking S3 delete since S3 copy failed.")
    '''
    request_json = {
        "request_id": 123456,
        "timestamp": "11-apr-30",
        "env_name": "pfapps",
        "parent_customername": "csgsol",
        "new_customername": "samsung",
        "callback_url": "https://echotest.proformprofessionals.com"
        "error": true,
        "status": "Customer already exist"
    }
    '''
    print("Invoking S3 delete lambda.")
    print ("Invoking S3 delete invoking request  = {}".format(request_json))
    client = boto3.client('lambda')
    uat_s3_delete_response = client.invoke(
        FunctionName='arn:aws:lambda:us-east-1:876984124922:function:uat-customer-copy-proform-folder-remove',
        InvocationType='Event',
        Payload=json.dumps(request_json)
    )