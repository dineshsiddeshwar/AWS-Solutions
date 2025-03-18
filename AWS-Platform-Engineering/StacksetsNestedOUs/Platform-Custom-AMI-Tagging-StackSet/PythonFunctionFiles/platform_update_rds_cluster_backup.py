import json
import boto3

def lambda_handler(event, context): 
    print(event)
    client = boto3.client("rds")
    response = client.modify_db_cluster(
        DBClusterIdentifier = event["detail"]["SourceIdentifier"],
        BackupRetentionPeriod =35,
        ApplyImmediately = True
    )
    return {
        'statusCode' :200,
        'body' : json.dumps(response, default=str)
    }