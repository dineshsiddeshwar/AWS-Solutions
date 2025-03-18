"""
This module is used by Custom Resource in Config CFN to wait for 10 minutes
"""
import requests
import json
import time

SUCCESS = "SUCCESS"
FAILED = "FAILED"


def lambda_handler(event, context):
    """"
    Lambda handler that calls the function to Wait & Send Response to Config CFN
    """
    send(event=event,
         context=context,
         response_status=SUCCESS,
         response_data={'Data': 'SUCCESS'})


def send(event, context, response_status, response_data):
    """"
    Function to Wait 10 Minutes & Send Response to Config CFN
    """
    response_url = event['ResponseURL']
    print(event)
    print(response_url)

    response_body = {'Status': response_status,
                     'Reason': 'See the details in CloudWatch Log Stream: ' + context.log_stream_name,
                     'PhysicalResourceId': context.log_stream_name,
                     'StackId': event['StackId'],
                     'RequestId': event['RequestId'],
                     'LogicalResourceId': event['LogicalResourceId'],
                     'NoEcho': False,
                     'Data': response_data}
    json_response_body = json.dumps(response_body)
    print("Response body:\n" + json_response_body)
    headers = {
        'content-type': '',
        'content-length': str(len(json_response_body))
    }

    try:
        if event['RequestType'] == 'Delete':
            response = requests.put(response_url,
                                    data=json_response_body,
                                    headers=headers)
        else:
            time.sleep(600)
            response = requests.put(response_url,
                                    data=json_response_body,
                                    headers=headers)
        print("Status code: " + response.reason)
    except Exception as e:
        time.sleep(240)
        requests.put(response_url,
                     data=json_response_body,
                     headers=headers)
        print("send(..) failed executing requests.put(..): " + str(e))
