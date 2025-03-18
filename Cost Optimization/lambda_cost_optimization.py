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
        file_name = 'Fuction-to-be-deleted.csv'
        with open("/tmp/"+file, 'rb') as file:
           content = file.read()       
        bucket = ''
        key = 'Lambda/'+accountid+'/'+file_name
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
        #print("Start Time:- {}".format(datetime.datetime.now()))
        regions = ['us-east-1']
        sts_client = boto3.client('sts')
        accountid = sts_client.get_caller_identity()["Account"]
        default_lambdas = ['aws-controltower', 'SC-'+accountid,'Stackset']
        rows = []
        for region in regions:
            lambda_client = boto3.client('lambda',region_name=region)
            lambda_response = lambda_client.list_functions(MaxItems=100)
            list_functions = lambda_response['Functions']
            while 'NextMarker' in lambda_response.keys():
                lambda_response = lambda_client.list_functions(Marker=lambda_response['NextMarker'],MaxItems=100)
                list_functions.extend(lambda_response['Functions'])
            print(f"Length of lambda fuctions available in {region} is {len(list_functions)}")
            delete_lambda_functions = []
            cw_client = boto3.client('logs',region_name=region)
            for function in list_functions:
                count = 0
                for defaults in default_lambdas:
                    if defaults in function['FunctionArn']:
                        count = count + 1
                if count > 0 :
                    continue
                log_grou_name = function['LoggingConfig']['LogGroup']
                try:
                    cw_response = cw_client.describe_log_streams(
                                    logGroupName=log_grou_name,
                                    orderBy='LastEventTime',
                                    descending=True,
                                    limit=1)
                    if 'logStreams' in cw_response and len(cw_response['logStreams']) > 0:
                        latest_log_stream = cw_response['logStreams'][0]
                        #print(latest_log_stream['lastEventTimestamp'])
                        last_event_time = latest_log_stream['lastEventTimestamp'] / 1000.0
                        last_event_time = datetime.utcfromtimestamp(last_event_time)
                        threshold_date = datetime.utcnow() - timedelta(days=90)
                        if last_event_time < threshold_date:
                            
                            delete_lambda_functions.append(function['FunctionArn'])

                    else:
                        delete_lambda_functions.append(function['FunctionArn'])
                except Exception as ex:
                    if 'ResourceNotFoundException' in str(ex):
                        delete_lambda_functions.append(function['FunctionArn'])
                    else:
                        raise ex
            final_delete_functions = delete_lambda_functions
            for dl_functions in delete_lambda_functions:
                tag_response = lambda_client.list_tags(Resource=dl_functions)
                
                for tag in tag_response['Tags'].keys():
                    break_loop = False
                    if 'cloudformation' in tag:
                        final_delete_functions.remove(dl_functions)
                        break_loop = True
                        break
                if break_loop:
                    continue
            print(f"Length of lambda that can be deleted as there is no log group or not been used in last 90 days:- {len(final_delete_functions)}")
            for dl_functions in final_delete_functions:
                tag_response = lambda_client.list_tags(Resource=dl_functions)
                child_row = [dl_functions,dl_functions.split(':')[4],dl_functions.split(':')[3],dl_functions.split(':')[6]]
                   
                rows.append(child_row)
                ####################################################################
            
            for function in final_delete_functions:
                try:
                    delete_lambda_response = lambda_client.delete_function(FunctionName=function)
                    delete_log_group_response = cw_client.delete_log_group(logGroupName="/aws/lambda/"+function.split(':')[6]) # check with rob
                except Exception as ex:
                    if 'ResourceNotFoundException' in str(ex):
                        pass
                    else:
                        raise ex
        if final_delete_functions != []:
            csv_headers = ['ARN','ACCOUNTID','REGION','FUNCTIONNAME']
            file_name = 'Fuction-to-be-deleted.csv'
            with open("/tmp/"+file_name, 'w', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(csv_headers)
                csv_writer.writerows(rows)
            status = upload_to_s3(file_name,accountid)
            if status:
                os.remove("/tmp/"+file_name)
        else:
            print("You saved Money!!. There is no functions to delete")
        return True
    except Exception as ex:
        raise ex