import boto3
import sys
import os
from tempfile import mkstemp
from shutil import move
from os import fdopen, remove

EnvType= str(sys.argv[1])
print("Env type is: ", EnvType)
AccountNumber= str(sys.argv[2])
print("AccountNumber is: ", AccountNumber)
local_file_path = str(sys.argv[3])+"parameters.json"
print("Parameters local file path: ", local_file_path)
account_param_bucket = "platform-snow-integration-logs-"+EnvType
print("Parameters store bucket name is: ", account_param_bucket)

## Download a file from a S3 bucket.
def download_from_S3bucket(account_param_bucket, local_file_path, object_name):
    s3_client = boto3.client('s3')
    try:
        s3_client.download_file(account_param_bucket, object_name, local_file_path)
    except Exception as exception:
        print("failed at download_from_S3bucket and error is :{} ".format(str(exception)))
        return False
    return True

try:
    print("inside try except block...")

    print("Downloading the parameters.json file..")
    if download_from_S3bucket(account_param_bucket, local_file_path, str(AccountNumber)+"/parameters.json") and os.path.exists(local_file_path):
        print("File is downloaded successfully..")
    else:
        print("file download failed.")
except Exception as ex:
    print("There is an error %s", str(ex))