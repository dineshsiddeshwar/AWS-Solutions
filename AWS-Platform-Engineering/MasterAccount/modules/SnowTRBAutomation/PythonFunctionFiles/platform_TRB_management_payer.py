# This lambda was updated as part of bulk ami automation June 24 -2024
import json
import logging
import os
import boto3
import datetime
import random
import time
import requests
import base64
import re


#Cloudwatch logger variables
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
LOGGER.addHandler(CH)

#Environment and global variables
session_client = boto3.session.Session()
secretManager_client = session_client.client('secretsmanager', region_name="us-east-1")
step_function_arn = os.environ['step_function_arn']
allowed_regions_parameter_name = "whitelisted_regions"

SUCCESS = "SUCCESS"
FAILED = "FAILED"
FAILED_RESPONSE = 400
SUCCESS_RESPONSE = 200


RETURN_SUCCESS = {
        'statusCode': 200,
        'message': "Request Successful"
    }
RETURN_FAILURE = {
        'statusCode': 400,
        'message': "Request Failed"
    }

tags = [{
    'Key': 'platform_do_not_delete',
    'Value': 'yes'}]

def get_ssm_param(parameter_name):
    """
    param: parametre_name
    return: parameter value for the given param name
    """
    try:
        ssm_client = boto3.client("ssm")
        parameter = ssm_client.get_parameter(
        Name=parameter_name,
            WithDecryption=True
        )
        if parameter:
            return parameter['Parameter']['Value']
    except Exception as ex:
        LOGGER.error("Encountered error while getting parameters'{0}'".format(ex))
        raise ex

def trim_whitespace_around_comma(input_string):
    # Remove leading and trailing whitespaces
    input_string = input_string.strip()
    # Define the regex pattern to match any whitespace around a comma
    pattern = r'\s*,\s*'
    # Use re.sub() to replace the matched pattern with a single comma
    trimmed_string = re.sub(pattern, ',', input_string)
    return trimmed_string

def multi_value_parser(value):
    """
    method: Parses the comma separated values and returns the list of values
    param: value - comma separated values
    returns: list of values
    """
    try:
        LOGGER.info("Inside the multi value parser method.")

        # only remove whitespaces where after and before comma

        value = trim_whitespace_around_comma(value)
        value = value.split(',')
        
        return value , SUCCESS_RESPONSE

    except Exception as ex:
        error_msg = "Multi-Value Field - {0} could not be split - please make sure value is comma separated, error : '{1}'".format(value,ex)
        LOGGER.error(error_msg)
        #notify_operations(event, ex)
        return error_msg, FAILED_RESPONSE

def multi_event_dresser(event):
    """
    method: Creates the payload of multiple event in case of bulk request
    param: dressed event coming after calling event_dresser() method
    returns: dictionary of multiple events to call multiple lambda invocations in the following format -
    {events: [{event1}, {event2}, ...]
    }

    with format of event-n as follows -

    {
        "BusinessAccountNumber": "AccountNumber",
        "Region": "region",
        "RequestType": "Image ID|Owner Account ID|Image Name",
        "RequestParameter": "<ami owner account id>|<ami_name>",
    }

    total number of possible events = AccountNumberCount * RegionCount * RequestTypeCount
    """
    try:
        LOGGER.info("Inside the multi event dresser method - received event - '{0}'".format(json.dumps(event)))

        # check if all the required fields are present in the event
        if not all(key in event for key in ["ActionType", "BusinessAccountNumbers", "RegionType", "RegionCount", "RegionSet", "AccountNumberCount", "RequestTypeCount", "request_ami_owner", "request_ami_name", "request_ami_id"]):
            error_msg = "Incomplete event received in multi_event_dresser method."
            LOGGER.error(error_msg)
            return FAILED_RESPONSE, error_msg

        BusinessAccountNumbers = event["BusinessAccountNumbers"]
        RegionSet = event["RegionSet"]

        events = []



        # below block to be executed based on whether event keys exist

        dynamic_fields = []
        if event.get("request_ami_owner", False):
            dynamic_fields.append(("Owner Account ID", event["ami_owner_value"]))
        if event.get("request_ami_name", False):
            dynamic_fields.append(("Image Name", event["ami_name_value"]))
        if event.get("request_ami_id", False):
            dynamic_fields.append(("Image ID", event["ami_id_value"]))

        for acc in BusinessAccountNumbers:
            for region in RegionSet:
                for field_name, field_values in dynamic_fields:
                    field_values, response = multi_value_parser(field_values)
                    if response == FAILED_RESPONSE:
                        return FAILED_RESPONSE, field_values
                    for field_value in field_values:
                        event = {}
                        event["BusinessAccountNumber"] = acc
                        event["Region"] = region
                        event["RequestType"] = field_name
                        event["RequestParameter"] = field_value

                        events.append(event)

        return events, SUCCESS
    except Exception as ex:
        error_msg = "Something went wrong inside the function - multi_event_dresser'{0}'".format(ex)
        LOGGER.error(error_msg)
        #notify_operations(event, ex)
        return FAILED_RESPONSE, error_msg

def validate_aws_region(region_string):
    """
    method: Validates the string whether it is a comma separated string of valid AWS regions or not
    
    Input is allowed to have whitespace characters before and after the comma as the fucntion will strip them off.

    param: region_string

    returns: False | cleaned_regions
    """

    try:
        LOGGER.info("Inside the validate_aws_region method.")
        valid_aws_regions = get_ssm_param(allowed_regions_parameter_name).split(',')
        regions = region_string.split(',')
        for region in regions:

            if region.strip() not in valid_aws_regions:
                return False
        

        cleaned_regions = [region.strip() for region in regions]
        
        # return
        return cleaned_regions
    
    except Exception as ex:
        error_msg = "Something went wrong inside the validate_aws_region'{0}'".format(ex)
        LOGGER.error(error_msg)
        #notify_operations(event, ex)
        return False

def event_dresser(event):
    """
    method: Grooms the event which is coming from the RARS to suit the funcion needs
    param: Lambda event
    returns: dressed event in the following format -
    {
        "ActionType": "Single"|"Bulk",
        "BusinessAccountNumbers": ["AccountNumber1", "AccountNumber2", ...],
        "RegionType": "Single"|"Custom",
        "RegionCount": 1|N,
        "RegionSet": ["RegionName1", "RegionName2", ...],
        "AccountNumberCount": 1|N,
        "RequestTypeCount": 1|N,
        "request_ami_owner": True|False,
        "request_ami_name": True|False,
        "request_ami_id": True|False,

        # in case of true values

        "ami_owner_value": "ami_owner_id1, ami_owner_id2, ...",
        "ami_name_value": "ami_name1, ami_name2, ...",
        "ami_id_value": "ami_id1, ami_id2, ..."

        }
    """
    try:
        LOGGER.info("Inside the event dresser method.")
        dressed_event = {}
        dressed_event['ActionType'] = event['snow_variables']['sh_request_type_ami']
        dressed_event['BusinessAccountNumbers'] = [event['snow_variables']['sh_account_id']]
        dressed_event['RegionType'] = event['snow_variables']['sh_regions']
        dressed_event["AccountNumberCount"] = 1
        if dressed_event["ActionType"] == "Bulk":
            dressed_event["AccountNumberCount"] = int(event['snow_variables']['sh_number_accounts'])
        dressed_event["RegionCount"] = 0
        dressed_event["RegionSet"] = []

        if dressed_event["RegionType"] == "Custom":
            # test failure of this block, should end the function and return failure
            try:
                result = validate_aws_region(event['snow_variables']['sh_custom_rgn_names'])
                if result == False:
                    error_msg = "Invalid AWS region names received."
                    LOGGER.error(error_msg)
                    return FAILED_RESPONSE, error_msg
                
                dressed_event['RegionCount'] = len(result)
                dressed_event['RegionSet'] = result

            except Exception as ex:
                error_msg = "Something went wrong while getting custom region names'{0}'".format(ex)
                LOGGER.error(error_msg)
                return FAILED_RESPONSE, error_msg
        
        elif dressed_event["RegionType"] == "Single":
            # test event for single region and variable name for region ( sh_regions ) - trigger SNOW request selecting this
            dressed_event['RegionCount'] = 1
            dressed_event['RegionSet'] = [event['snow_variables']['sh_region']]
        
        if dressed_event["ActionType"] == "Bulk":

            try:

                # test variable name for all account number count ( 1, 2, 3, 4, 5 ) - trigger different SNOW requests for each account number count

                # for different account number count type, SNOW request should have different variable names like - sh_account_id_1, sh_account_id_2, sh_account_id_3, sh_account_id_4, sh_account_id_5

                for i in range(2, dressed_event["AccountNumberCount"]+1):
                    dressed_event["BusinessAccountNumbers"].append(event['snow_variables'][f'sh_account_id_{i}'])
            
            except Exception as ex:
                error_msg = "Something went wrong while getting account number count in Bulk Request'{0}'".format(ex)
                LOGGER.error(error_msg)
                return FAILED_RESPONSE, error_msg
        
        # set all the request type flags to false
        dressed_event["RequestTypeCount"] = 0
        dressed_event["request_ami_owner"] = False
        dressed_event["request_ami_name"] = False
        dressed_event["request_ami_id"] = False

        # check for the request type and set the flags and values accordingly
        if event["snow_variables"]["sh_owner_acc_id"] == "true":
            dressed_event["RequestTypeCount"] += 1
            dressed_event["request_ami_owner"] = True
            dressed_event["ami_owner_value"] = event["snow_variables"]["sh_request_parameter_owner_ac_id"]
        
        if event["snow_variables"]["sh_img_name"] == "true":
            dressed_event["RequestTypeCount"] += 1
            dressed_event["request_ami_name"] = True
            dressed_event["ami_name_value"] = event["snow_variables"]["sh_request_parameter_image_name"]
        
        if event["snow_variables"]["sh_img_id"] == "true":
            dressed_event["RequestTypeCount"] += 1
            dressed_event["request_ami_id"] = True
            # test variable name for image id ( sh_request_parameter_image_id ) - trigger SNOW request selecting this
            dressed_event["ami_id_value"] = event["snow_variables"]["sh_request_parameter_image_id"]




        # call multi_event_dresser to dress up the event in case of bulk or custom region request so as to trigger multiple lambda invocations 

        dressed_event, response = multi_event_dresser(dressed_event)

        if dressed_event == FAILED_RESPONSE:
            return FAILED_RESPONSE, response

        LOGGER.info("event dresses up after calling multi_event_dresser- '{0}'".format(json.dumps(dressed_event)))


        return dressed_event, SUCCESS
    except Exception as ex:
        error_msg = "Something went wrong inside the event_dresser'{0}'".format(ex)
        LOGGER.error(error_msg)
        #notify_operations(event, ex)
        return FAILED_RESPONSE,error_msg

def get_SIMAAS_BearerToken(url, client_id, client_secret,username,password):
    """
    Generate SIMAAS Bearer Token to authorise to update the RARS task's status
    param url: url of RARS
    param client_id: RARS Client over SIMAAS
    param client_secret: secret to authenticat from the AAD
    """
    try:
        payload='client_id='+client_id+'&client_secret='+client_secret+'&grant_type=password'+'&username='+username+'&password='+password
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.request("POST", url, headers=headers, data=payload)
        bearer_token = json.loads(response.text)
        if bearer_token :
            LOGGER.info("bearer token has been returned...")
            return bearer_token
        else :
            LOGGER.info("No bearer token has been returned...")
            return None
    except Exception as exception:
        LOGGER.error("Exception while getting SIMAAS Bearer token and error is {}".format(exception))
        return None

def get_secret():
    """
    Retrieve secrets from the secrets manager to authenticate to RARS
    """
    secret_name = "IntegrationCreds-RARS"
    try:
        get_secret_value_response = secretManager_client.get_secret_value( SecretId=secret_name)
        if get_secret_value_response:
            if 'SecretString' in get_secret_value_response:
                secret = get_secret_value_response['SecretString']
                return secret
            else:
                decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
                return decoded_binary_secret
    except Exception as ex:
        LOGGER.error("Something went wrong while reading secrets'{0}".format(ex))
        return None

def notify_RARS_SNOW(event, status):
    """
    sned a notification to RARS api about the processing status
    param event: lambda event
    return: {Action_response, success_message|error_message}
    """
    try:
        LOGGER.info("Inside notify_RARS_SNOW")
        if status == "WORK IN PROGRESS":
            RARS_STATUS_CODE = "2"
            work_notes = "Request has been queued by our automation, please wait for further updates."
            sc_task_notes = "platform_TRB_management_payer has been triggered successfully."
        elif status == "FAILED":
            RARS_STATUS_CODE = "-5"
            work_notes = "An error was encountered in the automation to process this. Please check with the AWS@Shell platform team."
            sc_task_notes = "platform_TRB_management_payer has failed. Please see Cloudtrail logs for more details."
        api_data = json.loads(get_secret())
        if api_data :
                LOGGER.info("Retrieved AWS secret manager data..")
                Bearer_token_data = get_SIMAAS_BearerToken(api_data['SIMAAS_URL'], api_data['SIMAAS_client_id'], api_data['SIMAAS_client_secret'],api_data['SIMAAS_username'],api_data['SIMAAS_password'])
                if Bearer_token_data :
                    LOGGER.info("SIMAAS bearer toaken is retrieved ...")
                    payload = json.dumps({
                            "u_supplier_reference": event['task_number'],
                            "ice4u_target_id": event['task_number'],
                            "u_work_notes": sc_task_notes,
                            "u_close_notes": "The request is processed succesfully.",
                            "u_state": RARS_STATUS_CODE,
                            "u_comments": work_notes
                        })
                    headers = { 'Authorization': 'Bearer '+Bearer_token_data['access_token'] , 'Content-Type': 'application/json'}
                    response = requests.request("POST", api_data['RARS_URL'], headers=headers, data=payload)
                    LOGGER.info("called RARS with the payload'{0}' and recieved '{1}'".format(payload,response.status_code))

                    return SUCCESS_RESPONSE , SUCCESS
                else:
                    LOGGER.info("Failed to get SIMAAS bearer toaken...")
                    raise Exception("Failed to get SIMAAS bearer toaken...")
        else:
            LOGGER.info("failed at getting required secrets from AWS secret manager..")
            raise Exception("failed at getting required secrets from AWS secret manager..")
        
    except Exception as exception:
        error_msg = "Exception while sending response to Snow in notify_RARS_SNOW and error is {}".format(exception)
        LOGGER.error(error_msg)
        return FAILED_RESPONSE, error_msg

def payload_injector(event,events,status):
    """
    method: Injects the payload to the child account trigger lambda
    param: event
    returns: {status, response_message}
    """
    try:

        LOGGER.info("Inside the payload injector method.")
        event['RequestNumber'] = event['requested_item_number']
        event['RequestorEmailID'] = event['requested_for_email']
        event["RequestedDate"] = event['snow_variables']['estimated_delivery_date']
        event["SCTaskNumber"] = event['task_number']

        payload = {
            "status": status,
            "RequestNumber": event["RequestNumber"],
            "RequestorEmailID": event["RequestorEmailID"],
            "RequestedDate": event["RequestedDate"],
            "SCTaskNumber": event["SCTaskNumber"],
            "events" : events
        }

        # Invoke step function with the payload
        step_function_client = boto3.client('stepfunctions')
        # random number to avoid the duplicate execution name with the same request number

        execution_name = event["RequestNumber"] + "-" + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + "-" + str(random.randint(1, 1000))
        response = step_function_client.start_execution(
            stateMachineArn=step_function_arn,
            name=execution_name,
            input=json.dumps(payload)
        )

        if response:
            LOGGER.info("Step function invoked with the payload - '{0}'".format(json.dumps(payload)))
            return SUCCESS_RESPONSE, SUCCESS
    except Exception as ex:
        error_msg = "Something went wrong inside the payload_injector method'{0}'".format(ex)
        LOGGER.error(error_msg)
        return FAILED_RESPONSE, error_msg

def lambda_handler(event, context):
    """
    function: Lambda handler
    param: event from the lambda fucntion(API gateway).
        {
            "ActionType": "Single"|"Bulk",
            "BusinessAccountNumber1": "AccountNumber1",
            ...
            "BusinessAccountNumberN": "AccountNumberN",
            "RegionType": "Single"|"Custom"|"All",
            "Region": "RegionName"|["RegionName1", "RegionName2", ...]|"All",
            "RequestType": "owner_id|image_name|image_id",
            "RequestParameter": "<ami owner account id comma delimited string>|<ami_name_comma_delimited>|<ami_id_comma_delimited>",
            "RequestNumber": "RITM*",
            "TRBId": "12345",
            "RequestedDdate": "<time>"
    }
    param: lambda context/runtime
    returns: json response
    """
    try:
        LOGGER.info("Inside the Lambda handler with the event - '{0}'".format(json.dumps(event)))
        #Enable changes in the child account
        events, response = event_dresser(event)

        status = {
            'statusCode': 200,
            'message': response,
        }
        RARS_status = "WORK IN PROGRESS"

        if events == FAILED_RESPONSE:

            

            status = {
                'statusCode': 400,
                'message': response,
                'error_lambda': "platform_TRB_management_payer"
            }

        injector_status, response = payload_injector(event,events,status)

        
        
        if injector_status == FAILED_RESPONSE:

            status =  {
                'statusCode': 400,
                'message': response,
                'error_lambda': "platform_TRB_management_payer"
            }

            RARS_status = "FAILED"


        
        
        # uncomment to enable RARS response
        response_code, response_message = notify_RARS_SNOW(event, RARS_status)

        return RETURN_SUCCESS
    
    except Exception as ex:
        LOGGER.error("Something went wrong inside the Lambda handler'{0}'".format(ex))
        status = "FAILED"
        # uncomment to enable RARS response
        #notify_RARS_SNOW(event, status)
        return RETURN_SUCCESS