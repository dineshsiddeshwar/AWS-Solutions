import boto3
import json
import random
import datetime
import sys

def invoke_TGWAttachmentStepfunction(data):
    try:
        print("Starting invoking TGW attachment automation step function..")
        print('event' + str(data))
        step_function_name = data['ProvisionedProduct']['AccountNumber'] + '-' + \
                                 str(datetime.datetime.now().strftime('%Y%m%d%H%M%S')) + \
                                 str(random.randint(1, 1000)) + data['RequestEventData']['RequestNo']
        print("Step Function Name:", step_function_name)
        client = boto3.client('stepfunctions')
        response = client.start_execution(
                stateMachineArn='arn:aws:states:us-east-1:{}:stateMachine:platform_tgw_attachment_automation_ga'.format(data['SSMParameters']['admin_account']),
                name=step_function_name,
                input=json.dumps(data)
            )

        print(response)
        return True
    except Exception as exception:
        print(str(exception))
        print("Invoke TGW attachment has failed with an error..!!")
        return False         
           
try:
    local_file_path = str(sys.argv[1])+"parameters.json"
    print("Parameters local file path: ", local_file_path)
    with open(local_file_path) as json_data:
        parameters_data = json.load(json_data)
    print(parameters_data)
    if parameters_data : 
        print("parameters are loaded in json format, invokes invoke_TGWAttachmentStepfunction function..")
        if invoke_TGWAttachmentStepfunction(parameters_data):
            print("Invoking of TGW Attachment Automation is success..!!")
        else:
            print("Invoke of TGW Attachment Automation is fialed..!!")
except Exception as ex:
    print("There is an error %s", str(ex))
