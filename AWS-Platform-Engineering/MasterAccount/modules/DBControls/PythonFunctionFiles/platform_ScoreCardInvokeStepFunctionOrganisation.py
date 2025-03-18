import boto3
import os
def execute_step_function_in_child_accounts(region,name):
    child_account_ids = get_child_account_ids()  # Implement the function to retrieve the child account IDs
    
    for child_account_id in child_account_ids:
        try:
            step_function_arn = f'arn:aws:states:{region}:{child_account_id}:stateMachine:{name}'  # Replace with the ARN of your Step Function

            # Assume the IAM role in the child account
            role_arn = f'arn:aws:iam::{child_account_id}:role/platform_InvokeStepFunctionChildAccountRole'  # Replace ROLE_NAME with the actual role name
            assumed_role_session = boto3.Session().client('sts').assume_role(
                RoleArn=role_arn,
                RoleSessionName='AssumeRoleSession'
            )
            # Extract the temporary credentials
            credentials = assumed_role_session['Credentials']
            access_key = credentials['AccessKeyId']
            secret_key = credentials['SecretAccessKey']
            session_token = credentials['SessionToken']
            # Create a new boto3 session using the assumed role credentials
            session = boto3.Session(
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                aws_session_token=session_token
            )
            # Use the session to execute the Step Function in the child account
            step_functions_client = session.client('stepfunctions')
            response = step_functions_client.start_execution(
                stateMachineArn=step_function_arn
            )
            # Print the execution ARN for each child account
            print(f"Step Function execution started in child account {child_account_id}. Execution ARN: {response['executionArn']}")
        except Exception as e:
            print(e)
    
        
def get_child_account_ids():
    client = boto3.client('organizations')
    child_account_ids = []
    # Paginate through the list of accounts in the organization
    paginator = client.get_paginator('list_accounts')
    response_iterator = paginator.paginate()
    # Iterate over the accounts and filter for child accounts
    for response in response_iterator:
        for account in response['Accounts']:
            child_account_ids.append(account['Id'])
    return child_account_ids
    
def lambda_handler(event, context):
    region = "us-east-1"
    name = os.environ['StateMachine_Name']
    execute_step_function_in_child_accounts(region,name)
    return {
        'statusCode': 200,
        'body': 'Step Function executed in child accounts'
    }
