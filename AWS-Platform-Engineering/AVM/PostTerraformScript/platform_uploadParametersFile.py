import boto3
import json
import os
import sys


## Upload in S3 bucket
def Upload_in_S3bucket(account_param_bucket, accountnumber,data):
    print("All data to upload {}".format(data))
    s3_client = boto3.resource('s3')
    try:
        data['EndToEndComplete'] = "Yes"
        print("account number is {}".format(accountnumber))
        s3_file_name =  accountnumber + "/parameters.json"
        local_file_path = "/tmp/"+"parameters.json"
        print("file path:{}".format(local_file_path))
        with open(local_file_path, 'w') as fp:
            json.dump(data, fp)
        print("all account data is stored in local json file")
        s3_client.meta.client.upload_file(local_file_path, account_param_bucket, s3_file_name)
        print("file uploaded successfully..")
        os.remove(local_file_path)
        print("File deleted after upload to s3 bucket")
    except Exception as exception:
        print("Exception in Lambda Handler and error is {}".format(exception))
    return s3_file_name

try:
    print("reading the parameters.json file")
    local_file_path = str(sys.argv[1])+"parameters.json"
    print("Parameters local file path: ", local_file_path)
    with open(local_file_path) as json_data:
        parameters_data = json.load(json_data)
    print(parameters_data)
    if parameters_data:
        print("Uploading the parameters.json file..")
        if Upload_in_S3bucket("platform-snow-integration-logs-"+parameters_data['Env_type'], parameters_data['ProvisionedProduct']['AccountNumber'], parameters_data):
            print("File is Uploaded successfully..")
        else:
            print("file upload failed.")
    else:
        print("Reading the parameters is failed..")
except Exception as ex:
    print("There is an error %s", str(ex))
