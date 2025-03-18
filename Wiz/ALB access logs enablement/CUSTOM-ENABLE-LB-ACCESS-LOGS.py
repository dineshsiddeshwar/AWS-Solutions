
import boto3
from botocore.exceptions import WaiterError
from botocore.exceptions import ClientError

from aws.function.source import constants
from aws.function.source import utils

# Options:
# Future support for passing DRY_RUN param
DRY_RUN = False

    
def remediate(session: boto3.Session, event: dict, lambda_context):
    """
    Main Function invoked by index_parser.py
    """

    lb_arn = event["external_id"]
    region = event["region"]
    scan_id = event["scanId"]
    metadata = event['resource_type']
    presigned_url = event["presignURL"]
    try:
        if metadata == 'loadBalancerv1':
            lb_client = boto3.client('elb', region_name=region)
            desc_response = lb_client.describe_load_balancers(LoadBalancerNames=[event['resource_name']])
            name = 'XXXX'
            s3_bucket_name =  "XXXXXXXX"
            scheme = desc_response['LoadBalancerDescriptions'][0]['Scheme']
            lb_response = lb_client.modify_load_balancer_attributes(
                    LoadBalancerName=event['resource_name'],
                    LoadBalancerAttributes={
                        'AccessLog': {
                            'Enabled': True,
                            'S3BucketName': s3_bucket_name,
                            'S3BucketPrefix': scheme
                        }
                    })
            if lb_response:
                message = f"Attribute modified. S3 bucket location updated for the {lb_arn} to {s3_bucket_name}"
                response_action_status = constants.ResponseActionStatus.SUCCESS
            else:
                message = f"Something went wrong. Modify load balancer attribute response:- {str(lb_response)}"
                response_action_status = constants.ResponseActionStatus.FAILURE
        else:
            lb_client = boto3.client('elbv2', region_name=region)
            desc_response = lb_client.describe_load_balancers(LoadBalancerArns=[lb_arn])
            scheme = desc_response['LoadBalancers'][0]['Scheme']
            lb_type = desc_response['LoadBalancers'][0]['Type']
            if lb_type == 'application':
                name = 'alb-'
            elif lb_type == 'network':
                name = 'nlb-'
            else:
                name = 'elb-'
            s3_bucket_name =  name+"logs-509399619952-"+region
            lb_response = lb_client.modify_load_balancer_attributes(
                    LoadBalancerArn=lb_arn,
                    Attributes=[
                        {
                            'Key': 'access_logs.s3.enabled',
                            'Value': 'true'
                        },
                        {
                            'Key': 'access_logs.s3.bucket',
                            'Value': s3_bucket_name
                        },
                        {
                            'Key': 'access_logs.s3.prefix',
                            'Value': scheme
                        }
                    ]
                )
            if lb_response:
                message = f"Attribute modified. S3 bucket location updated for the {lb_arn} to {s3_bucket_name}"
                response_action_status = constants.ResponseActionStatus.SUCCESS
            else:
                message = f"Something went wrong. Modify load balancer attribute response:- {str(lb_response)}"
                response_action_status = constants.ResponseActionStatus.FAILURE
    
    except Exception as ex:
        message = f"Something went wrong. Modify load balancer attribute response:- {str(ex)}"
        response_action_status = constants.ResponseActionStatus.FAILURE
    response_action_message = message
    utils.send_response_action_result(
        presigned_url, scan_id, response_action_status, response_action_message
    )
    return
