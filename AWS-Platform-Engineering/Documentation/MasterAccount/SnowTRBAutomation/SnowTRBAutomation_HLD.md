## **High-Level Design (HLD) Document: AMI Allowlisting Hyperautomation**

### Table of Contents
1. [Introduction](#1-introduction)
2. [Purpose](#2-purpose)
3. [Process Overview](#3-process-overview)
4. [Architecture Components](#4-architecture-components)
5. [Reporting and Logging](#5-reporting-and-logging)
6. [Notifications](#6-notifications)
7. [Conclusion](#7-conclusion)


**1. Introduction** <a name="1-introduction"></a>

The AMI Allowlisting Hyperautomation is a feature designed to allow additional EC2 AMIs in the child accounts apart from the standard TOE Compliant Images. AMI allowlisting is performed on exception basis when a user raises an exception request via ServiceNow. This document provides a high-level overview of the feature, its purpose, the process it follows, and the additional components involved in reporting, logging, and notifications.

**2. Purpose** <a name="2-purpose"></a>

The primary purpose of the feature is to allowlist additional EC2 AMIs in the respective child account(s) as per the exception granted to the requestor. 

Below are the standard TOE compliant images available in each business account -

**"TOE_Complaint_OS_Flavours_Private"** : `"RHEL-7*,RHEL-8*,RHEL-9*,amzn2-ami-hvm*,amzn2-ami-*hvm-*,aws-storage-gateway-*,aws-datasync-*,bottlerocket-aws-k8s-*,aws-parallelcluster-*-amzn2*,Windows_Server-2019-English-Full-Base*,Windows_Server-2016-English-Full-Base*,Windows_Server-2016-English-Full-ECS_Optimized-*,Windows_Server-2019-English-Full-ECS_Optimized-*,Windows_Server-2022-English-Full-Base*,Windows_Server-2022-English-Full-ECS_Optimized-*,ubuntu/images/hvm-ssd/ubuntu-focal-20.04*,ubuntu/images/hvm-ssd/ubuntu-jammy-22.04*,amzn2-ami-ecs-hvm-*,amazon-eks-node-*,amazon-eks-gpu-node-*,amazon-eks-arm64-node-*,ShellCorp-GI-RHEL-7.9*,ShellCorp-GI-RHEL-8*"`

**"TOE_Complaint_OS_Flavours_Public"**: `"RHEL-7*,RHEL-8*,RHEL-9*,amzn2-ami-hvm*,amzn2-ami-*hvm-*,aws-storage-gateway-*,bottlerocket-aws-k8s-*,aws-datasync-*,aws-parallelcluster-*-amzn2*,Windows_Server-2019-English-Full-Base*,Windows_Server-2016-English-Full-Base*,Windows_Server-2016-English-Full-ECS_Optimized-*,Windows_Server-2019-English-Full-ECS_Optimized-*,Windows_Server-2022-English-Full-Base*,Windows_Server-2022-English-Full-ECS_Optimized-*,ubuntu/images/hvm-ssd/ubuntu-focal-20.04*,ubuntu/images/hvm-ssd/ubuntu-jammy-22.04*,amzn2-ami-ecs-hvm-*,amazon-eks-node-*,amazon-eks-gpu-node-*,amazon-eks-arm64-node-*,ShellCorp-GI-RHEL-7.9*,ShellCorp-GI-RHEL-8*"`

If a user wants to request for an AMI apart from the above ones, they have to follow the AMI Allowlisting Exception Process. When an exception request is granted, the SNOW request which is integrated with our AWS@Shell backend via RARS, triggers this automation, which is then used to automate the allowlisting of the additional AMIs. This saves time for the platform team from having to manually allowlist the AMI(s) required by the user.


**3. Process Overview** <a name="3-process-overview"></a>

The AMI Allowlisting Hyperautomation follows the following process:

1. **RARS Integration with AWS API Gateway**: Service Now Requests raised under this catalog (`AWS Account - Exception Management` --> `AMI Allow-Listing`) are integrated with AWS API Gateway via RARS. As soon as the API gateway is triggered using the RARS payload, it starts the underlying workflow of this automation.
2. **Request Type Identification**: The workflow identifies whether the required AMIs are to be allow-listed in a single account or multiple accounts. 
3. **Region Identification**: The workflow identifies whether the required AMIs are to be allow-listed in a single region or multiple regions. 
4. **Parallel AMI Allowlisting using Multi-Event Trigger**: The workflow creates necessary payloads as per the requirmement (multi-account/single-account, multi-region/single-region, multiple-amis/single-amis) and then triggers the child workflows which are parallelly executed to allowlist the required amis.
5. **Schedule Creation for periodic run of allowlisting function** : The workflow creates a schedule in each child account to ensure periodic run of the allowlisting automation.
6. **Result Aggregation**: The result of the parallel child workflows are aggregated at a single step for consolidation of notification and logging.
7. **Error Handling**: The automation includes error handling mechanisms to gracefully handle any exceptions or API failures encountered during the process. It also notifies the platform team about any failures encountered with the logged error messages.

**4. Architecture Components** <a name="4-architecture-components"></a>

![ami-bulk-hyperautomation-architecture.png](./images/Bulk_AMI_Hyperautomation_Architecture.jpg)

The AMI Allowlisting Hyperautomation feature utilizes the following AWS services and components:

- **AWS Lambda**: Serverless compute service used to execute the scheduling logic, reporting, and notification functions.
- **Amazon API Gateway Resources**: Managed service to create, deploy, and secure APIs at any scale.
- **Amazon Step Function**: Service to design, deploy, and manage serverless workflows and state machines at scale.
- **Amazon DynamoDB**: NoSQL database service used to store scheduling metadata, such as resource status and compliance information.
- **Amazon CloudWatch**: Monitoring and observability service used for logging, metrics, and triggering the scheduler.
- **Amazon Simple Email Service (SES)**: Email service used for sending notifications to stakeholders.
- **AWS Systems Manager Parameter Store**: Secure storage for configuration parameters, such as exception tags and whitelisted regions.
- **AWS Identity and Access Management (IAM)**: Access management service used to define permissions and roles for the Lambda functions.
- **Python**: Programming language used to develop the Lambda functions and implement the scheduling logic.

**5. Reporting and Monitoring** <a name="5-reporting-and-logging"></a>

In addition to the core allowlisting functionality, the feature includes reporting and monitoring components:

- **Aggregator and Reporting**: Stores the execution results from parallel child workflows and stores the relevant details about the execution summary like account details, request and ami information into a DynamoDB.
- **Logging**: Relevant information, such as resource actions, errors, and summary data, is logged using Amazon CloudWatch Logs for monitoring and auditing purposes.
- **Central Database**: A central database (e.g., Amazon RDS) for long-term storage,analysis and monitoring is maintained.
- **Monitoring Lambda Function**: Scheduled monitoring of the central DDB for overseeing request expiration, and sending call-to-action emails to stakeholders.

**6. Notifications** <a name="6-notifications"></a>

To keep stakeholders informed about the automation process, the feature includes a notification component:

- **Notification Lambda Function**: Sends email notifications to designated recipients using Amazon SES.
- **Notification Triggers**: Notifications can be triggered based on specific events, such as successful scheduling, errors, or resource non-compliance.
- **SNOW RARS Task Updates** - SNOW Tasks are updated with relevant state and messages in different stages of the automation.

**7. Conclusion** <a name="7-conclusion"></a>

The AMI Allowlisting Hyperautomation feature provides an automated solution for allowing additional EC2 AMIs in the child accounts. The high-level design outlined in this document covers the core process overview including reporting, logging, and notification components. By leveraging AWS services such as Lambda, DynamoDB, CloudWatch, and SES, the feature offers a scalable and efficient approach to managing the AMI allowlisting process.