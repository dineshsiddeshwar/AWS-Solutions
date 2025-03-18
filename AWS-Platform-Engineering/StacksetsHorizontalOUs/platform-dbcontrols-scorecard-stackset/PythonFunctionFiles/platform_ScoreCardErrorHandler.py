import json
import time
import boto3
import json
import datetime
import os
import random

def lambda_handler(event, context):
    # 
    accountID = getAccountId()
    item = {}
    
    # instance_name = event['instance_name']
    region = event['region']
    if 'rds_instance_name' in event:
        item['db_name'] = {'S' : event["rds_instance_name"]}

        try:
            db_engine = get_db_engine(event["rds_instance_name"],region)
            item['db_engine'] = {'S' : db_engine}
            
        except:
            pass

    
    if 'instance_name' in event:
        item['db_name'] = {'S' : event["instance_name"]}
        try:
            db_engine = get_db_engine(event["instance_name"],region)
            item['db_engine'] = {'S' : db_engine}
            
        except:
            pass

        
    item['region'] = {'S' : region}
    
    errorObj = event["error"]
    error = errorObj["Error"]
    
    errorCause = errorObj["Cause"]
    
    errorCauseJson = json.loads(errorCause)
    
    
    errorMessage = errorCauseJson["errorMessage"]
    
    writeFailToDynamo(item,errorMessage)

    db_name = item['db_name']['S']
    
    email_func(errorMessage,db_name,region)
    return {
        'messsage' : 'Success'
    }

def get_db_engine(instance_name,region):
    # Create a client object for the RDS service
    rds = boto3.client('rds', region_name=region)
    # Use the describe_db_instances() method to get details about the specified RDS instance
    response = rds.describe_db_instances(DBInstanceIdentifier=instance_name)
    # Extract the DB engine from the response
    db_engine = response['DBInstances'][0]['Engine']
    # Print the DB engine to the console
    return db_engine
    
def writeFailToDynamo(item,failure_reason):
    item['status'] = {'S' : "Fail"}
    item['failure_reason'] = {'S' : failure_reason}
    writeToDynamo(item)
    
def writeToDynamo(item):
        
    session_client = boto3.Session()
    sts_client = session_client.client('sts')
    account_number=os.environ['ACCOUNT_ID']
    secondaryRoleArn = "arn:aws:iam::{}:role/platform_dynamodb_dbcontrols".format(account_number)
    secondarySessionName = "SecondarySession-" + str(random.randint(1, 100000))
    # Logging to child account.
    # LOGGER.info("Logging to Child Account")
    secondaryRoleCreds = sts_client.assume_role(RoleArn=secondaryRoleArn,
                                    RoleSessionName=secondarySessionName)
    credentials = secondaryRoleCreds.get('Credentials')
    accessKeyID = credentials.get('AccessKeyId')
    secretAccessKey = credentials.get('SecretAccessKey')
    sessionToken = credentials.get('SessionToken')
    assumeRoleSession = boto3.session.Session(accessKeyID, secretAccessKey, sessionToken)
    dynamodb_client = assumeRoleSession.client('dynamodb',region_name='us-east-1')
    #dynamodb_client = boto3.client('dynamodb',region_name='us-east-1')
    table_name = os.environ['DYNAMODB_NAME']
    #dynamodb_client = boto3.client('dynamodb',region_name='us-east-1')
    #table_name = 'ComplianceRuns'
    datestr = datetime.datetime.now().strftime("%Y-%m-%d")
    timestr = datetime.datetime.now().strftime("%H:%M:%S")

    unix = time.time() * 1000
    unix = int(unix)
    account = getAccountId() 

    item['unix_timestamp'] = {'N': str(unix)}
    item['account'] = {'S': account}
    item['date'] ={'S' : datestr}
    item['time'] = {'S' : timestr}

    dynamodb_client.put_item(
        TableName=table_name,
        Item=item
        )      

def email_func(str_value, rds_instance_name, region):
    session_client = boto3.session.Session()
    sts_client = session_client.client('sts')
    account_number = sts_client.get_caller_identity()['Account']
    ssm_prmtr_client=boto3.client('ssm',region_name='us-east-1')
    response = ssm_prmtr_client.get_parameter(Name='/Platform-Tag/platform_Custodian')
    custodian=response['Parameter']['Value']
    platform_dl = ssm_prmtr_client.get_parameter(Name='/Platform-Tag/platform_DL')
    platform_dl_response = platform_dl['Parameter']['Value']
    mail_body_value=str_value
    DNSSESKeyEmail = ssm_prmtr_client.get_parameter(Name='/platform-dns/DNSSESKeyEmail')
    DNSSESKeyEmail = DNSSESKeyEmail['Parameter']['Value']
    DNSSESSecrtEmail = ssm_prmtr_client.get_parameter(Name='/platform-dns/DNSSESSecrtEmail')
    DNSSESSecrtEmail = DNSSESSecrtEmail['Parameter']['Value']
    platform_dl = ssm_prmtr_client.get_parameter(Name='/Platform-Tag/platform_DL')
    platform_dl_response = platform_dl['Parameter']['Value']
    session_client = boto3.session.Session()
    try:
        ses_client = session_client.client('ses', region_name='us-east-1', aws_access_key_id=DNSSESKeyEmail, aws_secret_access_key=DNSSESSecrtEmail)
    except Exception as exception:
        print(exception)
        
    str_value=str_value+" for "+rds_instance_name+" in the region "+region
    mail_body_value=str_value
    mail_body="""Hello,
        We could identify that the following issue has occured while triggering the DB compliance lambda. Please take necessary actions for it: +"""+mail_body_value+"""\nPlease refer to the RDS QRG for remediation instructions: """+"""\nRegards,\nCloud Services Team"""
    mail_subject= "DB Compliance pre-checks failed for the following account number: "+account_number
    body_html = """<html>
            <head>
            </head>
            <body>
            <p style="font-family:'Futura Medium'">Hello Team,</p>
            <p style="font-family:'Futura Medium'"> We could identify that the following issue has occured while triggering the DB compliance lambda. Please take necessary actions for it:</p>
            <p style="font-family:'Futura Medium'"><strong>"""+mail_body_value+"""</strong></p>
            <p style="font-family:'Futura Medium'">Please refer to the RDS QRG for remediation instructions:</p>
            <href>https://eu001-sp.shell.com/:w:/r/sites/AAFAA5187/L3/IB-Cloud%20CoE/AWS%20DA%202.0/QRGs/RDS%20QRGs/Master%20RDS%20QRG.docx?d=w07488d700ebc4b059ed4fa966eb52577&csf=1&web=1&e=D9tFnZ</href>
            <p style="font-family:'Futura Medium'">Best Regards,</p>
            <p style="font-family:'Futura Medium'">AWS@Shell Team</p>
            
            </body>
            </html>
            """
    try:
        # LOGGER.info("Inside custom Send Mail")
        char_set = "utf-8"
        #LOGGER.info("Hello\r\nWe could see the below instances are not having SSM agent installed and this would make the instances SSM non-compliant in our platform. Request you to install the SSM agent ASAP and  update us. \r\nAccount Number:" +self.account_number+mail_body+"\r\nRegards,\r\nCloud Services Team")
        response = ses_client.send_email(
            Destination={
                "ToAddresses": [custodian,
                        ],
                    },
            Message={
                    "Subject": {
                        "Data": mail_subject,
                                },
                    "Body": {
                        "Text": {
                            "Data": mail_body,
                        },
                        "Html":{
                            "Data":body_html
                        }
                            },
                           },
            Source="SITI-CLOUD-SERVICES@shell.com",
                    )
        # LOGGER.info("Email sent!")
    except Exception as exception:
        # LOGGER.error("Lambda failed with the error:'{0}'".format(exception))
        return "FAILED" 
        raise exception

def getAccountId():
    sts_client = boto3.client('sts',region_name=os.environ['AWS_REGION'],endpoint_url=f"https://sts.{os.environ['AWS_REGION']}.amazonaws.com")
    response = sts_client.get_caller_identity()
    account_id = response['Account']
    return account_id