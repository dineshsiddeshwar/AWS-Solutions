import json
import boto3
import datetime
from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.folders.folder import Folder
from office365.sharepoint.files.file import File
from office365.sharepoint.files.creation_information import FileCreationInformation
import os

def lambda_handler(event, context):
    s3_bucket = event["Records"][0]["s3"]["bucket"]["name"]
    s3_key = event["Records"][0]["s3"]["object"]["key"]
    sm = boto3.client('secretsmanager')
    secrets = sm.list_secrets(
        Filters=[
            {
                'Key': 'name',
                'Values': [
                    'ScoreCardSharePointSecret',
                ]
            },
        ],
    )
    secret = sm.get_secret_value(
        SecretId=secrets['SecretList'][0]['ARN']
    )
    secretitem = json.loads(secret['SecretString'])
    secretid = [key for key,value in secretitem.items()]
    secretvalue = [value for key,value in secretitem.items()]
    client_id = secretid[0]
    client_secret = secretvalue[0]
    
    url = 'https://eu001-sp.shell.com/sites/AAFAA3444/DBS/'
    
    client_credentials = ClientCredential(f'{client_id}',f'{client_secret}')
    ctx = ClientContext(f'{url}').with_credentials(client_credentials)
    
    downloadedFile = downloadFromS3(s3_bucket,s3_key)
    uploadToSharepoint(ctx,downloadedFile,s3_key,"AWS Shell RDS Scorecards")


    # TODO implement
    return {
        'message':'Success'
    }

def downloadFromS3(s3_bucket,s3_key):
    s3 = boto3.client("s3")
    response = s3.get_object(Bucket=s3_bucket,Key=s3_key)
    file_content = response["Body"].read()
    return file_content
    
def uploadToSharepoint(ctx,file_content,s3_key,target_folder_path):
    web = ctx.web
    folder = web.get_folder_by_server_relative_path(target_folder_path)
    file_name = os.path.basename(s3_key)
    info = FileCreationInformation()
    info.content = file_content
    info.url = file_name
    info.time_created = datetime.datetime.now()
    upload_file = folder.files.add(file_name,file_content)
    ctx.execute_query()
    

def createFolder(name,ctx):
    new_folder = folder.folders.add(name)
    ctx.execute_query()
    return new_folder
