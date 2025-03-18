# Snow AMI Allowlisting Automation

This document provides detailed information about the hyper-automation designed to manage AWS EC2 AMI allowlisting process which is integrated with ServiceNow ( SNOW ) requests via RARS integration. The automation adds the required ami information to the allowlisted amis, this can be either adding the ami name or the ami owner in the SSM parameters of the repective child accounts. The ami informtion is provided in the SNOW request raised by the requestor.

The SNOW request for AMI Allowlisting can be raised by going to `AWS Account - Exception Management` --> `AMI Allow-Listing` at this [link](https://shell2.service-now.com/sp?id=sc_cat_item_guide&table=sc_cat_item&sys_id=ae72bdb6db9bec5079c7d18c68961929). 


## Documentation

- [High-Level Design (HLD) Document](../../../Documentation/MasterAccount/SnowTRBAutomation/SnowTRBAutomation_HLD.md)
  - The HLD document provides a detailed overview of the feature, including the system architecture, components, data flow, and other key considerations.
- [Low-Level Design (LLD) Document](../../../Documentation/MasterAccount/SnowTRBAutomation/SnowTRBAutomation_LLD.md)
  - The LLD document delves into the implementation specifics, code structure, integration points, and execution flow of the Lambda function.

## Functionality

The Lambda function, `platform_TRB_management_payer`, is triggered by the AWS API Gateway as soon as a RARS integrated SNOW request hits the API Gateway with the payload information. This triggers the lambda which in turn invokes a child workflow to execute the ami - allowlisting automation, in accordance with the input payload.

THe child workflow is orchestrated by the state machine - `TRB_AMI_Exception_Management`

THe Lambda function, `platform_TRB_management_monitoring` is triggered periodically to check if the exception SNOW request has crossed its expiration date by referencing our internal database in management account. If it finds an expired request, it triggers a notification to the respective custodian to raise a fresh request if they wish to extend the exception granted to them.
 
## Setup Instructions

### Requirements

- AWS CLI already configured with Administrator permission
- Python 3.8 or newer
- Boto3 library
- Access to AWS RDS and the ability to manage RDS instances and clusters

### Local Development

1. **Install Dependencies**

   Install the required Python libraries:

    ```bash
        pip install boto3
    
    ```

2. **Setting up Environment Variables**

   Ensure that your AWS credentials are configured as environment variables:

    ```bash
    export AWS_ACCESS_KEY_ID="your-access-key-id"
    export AWS_SECRET_ACCESS_KEY="your-secret-access-key"
    export AWS_DEFAULT_REGION="us-east-1"
    
    ```


