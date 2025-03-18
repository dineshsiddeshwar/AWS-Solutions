import json
import boto3
import time
import botocore

def get_rds_information(rds_client, db_instance_id):
    paginator = rds_client.get_paginator("describe_db_instances")
    page_iterator = paginator.paginate(
        Filters=[{"Name": "db-instance-id", "Values": [db_instance_id]}],
    )
    isCluster = False
    for page in page_iterator:
        for instance in page["DBInstances"]:
            if "DBClusterIdentifier" in instance:
                  isCluster = True
            return instance["DBInstanceStatus"], isCluster
    return None, None

def lambda_handler(event, context):
    print(event)
    rds_client = boto3.client("rds")
    db_instance_id = event["detail"]["SourceIdentifier"]
    db_instance_status, db_is_cluster = get_rds_information(rds_client, db_instance_id)
    if db_instance_status is None:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": "Backups have not been enabled for the db instance as it could not be discovered",
                }),
        } 
    if db_is_cluster:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": "Backups have not been enabled for the db instance as it is part of a cluster",
                }),
        }   
    while (db_instance_status != "available"):
        time.sleep(120)
        db_instance_status, db_is_cluster = get_rds_information(rds_client, db_instance_id)
        print("RDS Instance Status: ",db_instance_status)
        
    print("Chaning backup retention setting on DB")
    try:
        response = rds_client.modify_db_instance(
            DBInstanceIdentifier = db_instance_id,
            BackupRetentionPeriod =35,
            ApplyImmediately = True
        )
        return {
            'statusCode' :200,
            'body' : json.dumps(response, default=str)
        }  
    except botocore.exceptions.ClientError as error:
        if "backup window and maintenance window must not overlap" in error.response["Error"]["Message"]:
            error_message = f"DB INSTANCE {db_instance_identifier} MODIFICATION FAILED.  BACKUP WINDOW AND MAINTENANCE WINDOW MUST NOT OVERLAP."
            raise Exception(error_message)
        elif "backup window must be at least 30 minutes" in error.response["Error"]["Message"]:
            error_message = (
                f"DB INSTANCE {db_instance_identifier} MODIFICATION FAILED. BACKUP WINDOW MUST BE AT LEAST 30 MINUTES."
            )
            raise Exception(error_message)
        else:
            raise error
        