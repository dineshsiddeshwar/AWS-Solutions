import json
import boto3
import logging
import os


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
trb_parameter_ami_name = os.environ['trb_parameter_ami_name']
trb_parameter_owner_id = os.environ['trb_parameter_owner_id']
trb_parameter_image_id = os.environ['trb_parameter_image_id']
SUCCESS = "SUCCESS"
FAILED = "FAILED"
FAILED_RESPONSE = 400
SUCCESS_RESPONSE = 200


def whitelist_image(request_type, request_param, aws_account_id):
    """
    Whitelist images based on the details such as image name or owner account id of the image as provided by the business. refer platform_TRB_management dynamodb table. 
    Param: request_type SaaS or Name based whitelisting.
    Param: request-param owner account_id or image_name
    Returns: Failure or Success
    """
    try:
        to_be_tagged_id_list = []
        request_param_list = request_param.split(",")
        status_code = 400
        LOGGER.info("Inside whitelist function.")
        ec2_client = boto3.client('ec2')
        #describe the AMIs for given parameter.
        if request_type == 'owner_id':
            LOGGER.info("Owner based enablement")
            response = ec2_client.describe_images(
                ExecutableUsers=[aws_account_id],
                IncludeDeprecated=False,
                Owners = request_param_list,
                DryRun=False)
    
        elif request_type == 'image_id':
            to_be_tagged_id_list 
            LOGGER.info("Image ID based enablement.")
            response = ec2_client.create_tags(
                DryRun=False,
                Resources= request_param_list,
                Tags=[{
                    'Key': 'platform_image_whitelist',
                    'Value': 'yes'},])
            return SUCCESS
        else:
            LOGGER.info("Image name based enablement.")
            ami_list = []
            ami_list.append(request_param)
            response = ec2_client.describe_images(
                Owners=['amazon','self','aws-marketplace'],
                Filters=[
                    {'Name': 'name', 'Values': request_param_list}
                    ])
        status_code = response.get('ResponseMetadata', FAILED_RESPONSE).get('HTTPStatusCode')
        if status_code != SUCCESS_RESPONSE:
            LOGGER.error("Invalid parameter passed in request payload.")
            return FAILED
        images = response['Images']
        if images:
            for item in images:
                if 'Tags' not in item:
                    to_be_tagged_id_list.append(item['ImageId'])
                else:
                    whitelist_flag = 'no'
                    resource_tags = item['Tags']
                    for tag_item in resource_tags:
                        if tag_item['Key'] == 'platform_image_whitelist' and tag_item['Value'] == 'yes':
                            whitelist_flag = 'yes'
                    if whitelist_flag != 'yes':
                        to_be_tagged_id_list.append(item['ImageId'])
            #create tags on ami
            response = ec2_client.create_tags(
                DryRun=False,
                Resources=to_be_tagged_id_list,
                Tags=[{
                    'Key': 'platform_image_whitelist',
                    'Value': 'yes'},])
            status_code = response.get('ResponseMetadata', FAILED_RESPONSE).get('HTTPStatusCode')   
            if status_code != SUCCESS_RESPONSE:
                LOGGER.error("Unable to tag the images- '{0}'".format(to_be_tagged_id_list))
                return FAILED    
            return SUCCESS
        else:
            LOGGER.error("No images are provisioned to this account with the provided details. please check with the business.")
            return FAILED
    except Exception as e:
        LOGGER.error("Something went wrong while describing the images- '{0}'".format(e))
        return FAILED


def lambda_handler(event, context):
    """
    Funcation: Lambda handler
    Param: Lambda Event 
    Param: Lambda Context 
    Return: Success or Failure
    Author: Shanmukha SP 
    Feature: 
    """
    try:
        LOGGER.info("Started the handler.")
        aws_account_id = context.invoked_function_arn.split(":")[4]
        falied_list = success_list = []
        # Retrieve SSM Paramteres
        ssm_client = boto3.client('ssm')
        ssm_response = ssm_client.get_parameters(
            Names = [trb_parameter_ami_name, trb_parameter_owner_id, trb_parameter_image_id],
            WithDecryption = False)
        if ssm_response['Parameters']:
            for parameter in ssm_response['Parameters']:
                if parameter['Name'] == trb_parameter_ami_name:
                    whitelist_image('image_name', parameter['Value'], aws_account_id)
                elif parameter['Name'] == trb_parameter_image_id:
                    whitelist_image('image_id', parameter['Value'], aws_account_id)
                else:
                    whitelist_image('owner_id', parameter['Value'], aws_account_id)
        else:
            LOGGER.error("Something went wrong. There are no parameters.")
            return FAILED
        LOGGER.info("Whitelisting of given images is completed.")
        return SUCCESS
    except Exception as e:
        LOGGER.error("The Lambda handler failed".format(e))
        return FAILED
    