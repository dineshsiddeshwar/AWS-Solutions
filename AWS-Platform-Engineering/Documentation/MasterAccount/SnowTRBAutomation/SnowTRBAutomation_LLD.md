## Low-Level Design (LLD) Document: AMI Allowlisting Hyperautomation

### **Table of Contents**

1. [Introduction](#1-introduction)
2. [Architecture Component - with resource names](#2-architecture)
3. [Code Structure and Functionality](#3-code-structure)
4. [Standard Tags](#4-standard-tags)
5. [Child Account Lambda Schedule](#5-user-defined-scheduling)
6. [DynamoDB Table Structure](#9-dynamodb-table-structure)
7. [Error Handling and Logging](#10-error-handling-and-logging)
8. [Testing](#11-testing)
9. [Deployment](#12-deployment)
10. [Monitoring and Alerting](#13-monitoring-and-alerting)

**1. Introduction** <a name="1-introduction"></a>

The AMI Allowlisting Hyperautomation is a feature designed to allow additional EC2 AMIs in the child accounts apart from the standard TOE Compliant Images. AMI allowlisting is performed on exception basis when a user raises an exception request via ServiceNow. This document provides a high-level overview of the feature, its purpose, the process it follows, and the additional components involved in reporting, logging, and notifications.

**2. Architecture Component - with resource names** <a name="2-architecture"></a>

![ami-bulk-hyperautomation-architecture.jpg](./images/Bulk_AMI_Hyperautomation_Architecture.jpg)

The AMI Allowlisting Hyperautomation feature will be implemented using the following AWS services:

- **AWS Lambda**: Serverless compute service used to execute the scheduling logic, reporting, and notification functions.
  - `platform_TRB_management_payer`
  - `platform_TRB_management_payer_child_account_trigger`
  - `platform_TRB_management_payer_result_aggregator`
  - `platform_TRB_management_monitoring`
  - `platform_TRB_management_child`
- **Amazon API Gateway Resources**: Managed service to create, deploy, and secure APIs at any scale.
  - `LatestTRBAuth`
- **Amazon Step Function**: Service to design, deploy, and manage serverless workflows and state machines at scale.
  - `TRB_AMI_Exception_Management`
- **Amazon DynamoDB**: NoSQL database service used to store scheduling metadata, such as resource status and compliance information.
  - `TRB_AMI_Exception_Management` 
- **Amazon CloudWatch**: Monitoring and observability service used for logging, metrics, and triggering the scheduler.
  - `platform_TRB_Management_Expiration_schedule`
- **Amazon Simple Email Service (SES)**: Email service used for sending notifications to stakeholders.
- **AWS Systems Manager Parameter Store**: Secure storage for configuration parameters, such as exception tags and whitelisted regions.
  - `trb_parameter_image_id`
  - `trb_parameter_owner_id`
  - `trb_parameter_ami_name`
- **AWS Identity and Access Management (IAM)**: Access management service used to define permissions and roles for the Lambda functions.
- **Python**: Programming language used to develop the Lambda functions and implement the scheduling logic.

**3. Code Structure and Functionality** <a name="3-code-structure"></a>

The code for the AMI Allowlisting Hyperautomation will be structured as follows:

- `platform_TRB_management_payer.py`: Payer Lambda Function which is called as soon as RARS payload hits AWS@Shell API endpoint. Here the input payload is converted into a concurrent list of payload events which call the next resource in execution flow - mimicing a batch processing of multiple single account - single region - single parameter event call.
  - `lambda_handler(event, context)`: Entry point for the Lambda function.
  - `event_dresser(event)`: Dresses the payload event as input for the next resource in execution flow.
  - `multi_event_dresser(event)`: Creates list of event dictionaries to be used to call the next resource in execution flow.
  - `validate_aws_region(region_string)`: Validates whether provided region list in input is a valid aws region or not.
  - `get_SIMAAS_BearerToken(url, client_id, client_secret,username,password)`: Gets SIMAAS Bearer Token to execute RARS outbound call.
  - `get_secret()`: Gets secret from AWS Secrets Manager stored on Management Account.
  - `notify_RARS_SNOW(event, status)`: Updates SCTASK via RARS outbound call with relevant status code.
  - `payload_injector(event,events,status)`: Calls Step Function with relevant payload.

- `TRB_AMI_Exception_Management` - Step Function which orchestrates various lambda functions and input events coming from intial lambda on the basis of different condition blocks.

- `platform_TRB_management_payer_child_account_trigger.py`: Lambda function that enables single AMI SSM parameter in single account in single region - this works on a 1:1:1 mapping of input event. Multiple invocations of this lamdba is done by asynchronous calls via Step Function Map Feature.
  - `lambda_handler(event, context)`: Entry point for the Lambda function.
  - `enable_child_account(event, context)`: Enables the given AMI SSM Parameter in the given Account in given region.
  - `get_custodian(accountid)`: gets custodian of the given account
  - `validate_paylaod_in_child_account(event, child_assume_role_session, child_account_region)`: validates whether given parameter value exists in child account or not.
  - `put_child_eventbridge_rule(event, child_assume_role_session)`: Generates eventbridge rule in child account to enable periodic trigger of `platform_TRB_management_child` as per a set cron.
  - `verify_boto_response(response)`: returns status code of a boto function call
  - `add_ssm_parameters(event, assume_role_session)`: checks if SSM parameter is to be created or updated in the child account
  - `create_update_ssm_parameters(event, operation_type, parameter_name, param_value, child_ssm_client)`: creates/updates the given SSM parameter in the child account
  - `get_ssm_param(parametre_name)`: returns the given SSM parameter value

- `platform_TRB_management_payer_result_aggregator.py`: Aggregates the result of multiple executions of the child trigger lambda, sends results to stakeholders and updates management account DDB.
  - `lambda_handler(event, context)`: Entry point for the Lambda function.
  - `aggregate_custodian(event)`: Aggregates all custodians from multiple runs of child trigger lambda
  - `send_success_email(event, success_report)`: sends success email to stakeholders in case of successful runs
  - `validate_operation_success(event)`: validates and aggregates failed and successful events together.
  - `dump_data_to_ddb(event)`: uploads the request data to DDB in case of successful run
  - `generate_report(event)`: generates the failed and successful runs in an aggregated manner
  - `notify_operations_automation_failure(event,e, notify_requestor=False)`: notify platform team in case of any failure
  - `trigger_failure_email(event, success_report, failure_report)`: trigger failure email to stakeholders in case of partial failures in some of the events in case of bulk requests.

- `platform_TRB_management_child`: Lambda within the child account running on a schedule to put the allowlist tag on the AMIs in accordance with the AMI parameters enabled in the SSM parameters.

- `platform_TRB_management_monitoring`: Lambda which monitors the DDB data and checks the request whether it has expired or not. It also notifies users in case of expired requests.
  - `lambda_handler(event, context)`: Entry point for the Lambda function.
  - `check_expiration(request_number, date)`: checks whether a request item has expired or not based on the requested date
  - `get_db_items()`: scans DDB
  - `alert_operations(exception)`: alerts platform team in case of any exceptions encountered
  - `send_expiry_email(item,word)`: sends expiry notifications to custodians in case of expired requests

**4. Standard Tags** <a name="4-standard-tags"></a>

The following standard tags will be used in the AMI Allowlisting Hyperautomation:

- `platform_do_not_delete`: Tag which protects platform resource from accidental deletion
- `platform_image_whitelist`: Tag which allows an AMI to be provisioned post allowlisting

**5. Child Account Lambda Schedule** <a name="5-child-account-lambda-scheduling"></a>

The child account lamdba - `platform_TRB_management_child` runs on the below cron schedule -

 - `"cron(0 10 * * ? *)"`

**6. DynamoDB Table Structure** <a name="9-dynamodb-table-structure"></a>

The DynamoDB table will store the resource state, scheduling metadata, and compliance information. The table will have the following structure:

- Primary Key: `RequestNumber` (String)
- Attributes:
  - `RequestNumber` (String): Request-AccountNumber-RandomString hashkey
  - `AccountNumber` (String): Account Number
  - `RequestorEmailID` (String): Requestor who raised the SNOW request
  - `CustodianMailId` (String): Account Custodian Email ID
  - `RequestParameter` (String): AMI Parameter Value
  - `RequestType` (String): Type of AMI Parameter - ami_type, ami_owner, ami_id
  - `CreationTime` (String): The timestamp of the last start action.
  - `status` (String): status of item - active or expired

**7. Error Handling and Logging** <a name="10-error-handling-and-logging"></a>

- The Lambda functions will include comprehensive error handling to gracefully handle exceptions and API failures.
- Detailed logging statements will be added throughout the code to capture important information and aid in troubleshooting.
- CloudWatch Logs will be used to store and monitor the Lambda function logs.

**8. Testing** <a name="11-testing"></a>

- Unit tests will be written for each component of the Lambda functions to ensure code correctness and coverage.
- Integration tests will be performed to validate the interaction between the Lambda functions and the various AWS services.
- End-to-end testing will be conducted to verify the complete scheduling and reporting workflow, including scenarios where resources are manually started during the shutdown period.

**9. Deployment** <a name="12-deployment"></a>

The AMI Allowlisting Hyperautomation will be deployed using Terraform Cloud:

- Terraform configuration files will be created to define the required AWS resources, including Lambda functions, IAM roles, CloudWatch Events rules, and DynamoDB tables.
- Terraform Cloud will be used as the centralized platform for managing and deploying the infrastructure.
- Each AWS account will have its own Lambda `platform_TRB_management_child` deployed using Stackset - `platform-compliance-security`
- Terraform workspaces will be same as workspace for Master Account.
- The deployment process will be automated using Terraform Cloud's CI/CD capabilities, ensuring consistent and reliable deployments across accounts and environments.

**10. Monitoring and Alerting** <a name="13-monitoring-and-alerting"></a>

- Email Alerts will be set up to notify the relevant team if any issues or anomalies are detected.
- RARS Tasks are automatically updated with relevant status - Work In Progress, Closed Completed or Pending as per the status of the execution flow.