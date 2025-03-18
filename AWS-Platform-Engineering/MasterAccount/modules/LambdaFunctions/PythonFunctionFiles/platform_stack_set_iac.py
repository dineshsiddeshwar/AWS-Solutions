import json
import boto3
import requests
from botocore.exceptions import ClientError
from time import sleep

SUCCESS = "SUCCESS"
FAILED = "FAILED"

"""
This Lambda is used to set up Cloud Formation Stack set in the child accounts
"""
class StackSetFormIaC():
    def __init__(self, event, context):
        try:
            print(event, context)
            self.event = event
            self.context = context
            self.cloudformation_client = boto3.client('cloudformation')
            self.stack_setName = self.event['ResourceProperties']['StackSetName']
            self.stack_setDescription = self.event['ResourceProperties']['StackSetDescription']
            self.Parameter = []
            if "Parameter" in self.event['ResourceProperties']:
                self.Parameter = self.event['ResourceProperties']['Parameter']
            print (self.Parameter)
        except Exception as e:
            raise Exception(str(e))

    """List the stack set operations to check if the stack set is under change"""
    def list_stack_set_operations(self):
        try:
            list_operations = []

            response = self.cloudformation_client.list_stack_set_operations(
                StackSetName=self.stack_setName,
                MaxResults=1
            )

            while (True):
                for operation in response['Summaries']:
                    list_operations.append({"OperationID": operation['OperationId'], "Action": operation['Action'],
                                            "Status": operation['Status']})
                if ('NextToken' not in response):
                    break
                response = self.cloudformation_client.list_stack_set_operations(
                    StackSetName=self.stack_setName,
                    NextToken=response['NextToken'],
                    MaxResults=100
                )


            return list_operations
        except Exception as e:
            raise Exception(str(e))

    """Create the stack set"""
    def create_stack_set(self):
        print("Create Stack set")
        # Wrapper for create_stack_instances
        sleep_time = 15
        retries = 60
        this_try = 0
        while True :
            try:
                response = self.cloudformation_client.create_stack_set(
                    StackSetName=self.stack_setName,
                    Description=self.stack_setDescription,
                    TemplateURL=self.event['ResourceProperties']['TemplateURL'],
                    Parameters=self.Parameter,
                    Capabilities=[
                        'CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM'
                    ],
                    Tags=[
                        {
                            'Key': 'platform_donotdelete',
                            'Value': 'yes'
                        },
                    ],
                    PermissionModel='SERVICE_MANAGED',
                    AutoDeployment={
                        'Enabled': True,
                        'RetainStacksOnAccountRemoval': False
                    }
                )
                print(response['StackSetId'])
                self.PhysicalResourceId = response['StackSetId']
                new_OUs = self.event['ResourceProperties']['OUIDs']
                new_ou_list = [x.strip(' ') for x in new_OUs.split(",")]
                new_Regions = self.event['ResourceProperties']['Regions']
                new_regions_list = [x.strip(' ') for x in new_Regions.split(",")]
                response = self.cloudformation_client.create_stack_instances(
                    StackSetName=self.stack_setName,
                    DeploymentTargets={
                        'OrganizationalUnitIds': new_ou_list
                    },
                    Regions=new_regions_list,
                    OperationPreferences={
                        'FailureTolerancePercentage': 100,
                        'MaxConcurrentPercentage': 50
                    }
                )
                print(response)
                return self.PhysicalResourceId
            except ClientError as e:
                if e.response['Error']['Code'] == 'OperationInProgressException':
                    this_try += 1
                    if this_try == retries:
                        print("Failed to create stack instances after {} tries".format(this_try))
                        raise Exception("Error creating stack instances: {}".format(e))
                    else:
                        print("Create stack instances operation in progress for {} in {}. Sleeping for {} seconds.".format(self.stack_setName, new_regions_list, sleep_time))
                        sleep(sleep_time)
                        continue
                elif e.response['Error']['Code'] == 'Throttling':
                    this_try += 1
                    if this_try == retries:
                        print("Failed to create stack instances after {} tries".format(this_try))
                        raise Exception("Error creating stack instances: {}".format(e))
                    else:
                        print("Throttling exception encountered while creating stack instances. Backing off and retyring. " "Sleeping for {} seconds.".format(sleep_time))
                        sleep(sleep_time)
                        continue
                elif e.response['Error']['Code'] == 'StackSetNotFoundException':
                    raise Exception("No StackSet matching {} found in {}. You must create before creating stack instances.".format(self.stack_setName, new_regions_list))
                else:
                    raise Exception("Error creating stack instances: {}".format(e))

    """Update the stack set"""
    def update_Stack_set(self, create_region):
        # Set up for retries
        sleep_time = 15
        retries = 60
        this_try = 0
        while True :
            try:
                response = self.cloudformation_client.update_stack_set(
                    StackSetName=self.stack_setName,
                    Description=self.stack_setDescription,
                    TemplateURL=self.event['ResourceProperties']['TemplateURL'],
                    Parameters=self.Parameter,
                    Capabilities=[
                        'CAPABILITY_IAM' , 'CAPABILITY_NAMED_IAM' ,
                    ],
                    Tags=[
                        {
                            'Key': 'platform_donotdelete',
                            'Value': 'yes'
                        },
                    ],
                    OperationPreferences={
                        'RegionConcurrencyType': 'SEQUENTIAL',
                        'RegionOrder': create_region,
                        'FailureTolerancePercentage': 100,
                        'MaxConcurrentPercentage': 50
                    },
                    PermissionModel='SERVICE_MANAGED',
                    AutoDeployment={
                        'Enabled': True,
                        'RetainStacksOnAccountRemoval': False
                    }
                )
                if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                    return self.stack_setName
                else:
                    raise Exception("HTTP Error: {}".format(response))
            except ClientError as e:
                if e.response['Error']['Code'] == 'OperationInProgressException':
                    this_try += 1
                    if this_try == retries:
                        raise Exception("Failed to update StackSet after {} tries.".format(this_try))
                    else:
                        print("Update StackSet operation in progress for {}. Sleeping for {} seconds.".format(self.stack_setName, sleep_time))
                        sleep(sleep_time)
                        continue
                elif e.response['Error']['Code'] == 'StackSetNotEmptyException':
                    raise Exception("There are still stacks in set {}. You must delete these first.".format(self.stack_setName))
                else:
                    raise Exception("Unexpected error: {}".format(e))

    """Update Stack Set instances i.e. if new OU's are added to the stack set"""
    def update_stack_set_instances(self):
        # Wrapper for create_stack_instances
        sleep_time = 15
        retries = 60
        this_try = 0
        print("Update Stack set instances..")
        while True:
            try:
                new_regions = self.event['ResourceProperties']['Regions']
                new_OUs = self.event['ResourceProperties']['OUIDs']
                newregionList = [x.strip(' ') for x in new_regions.split(",")]
                newOUList = [x.strip(' ') for x in new_OUs.split(",")]
                response = self.cloudformation_client.create_stack_instances(
                    StackSetName=self.stack_setName,
                    DeploymentTargets={
                        'OrganizationalUnitIds': newOUList
                    },
                    Regions=newregionList,
                    OperationPreferences={
                        'FailureTolerancePercentage': 100,
                        'MaxConcurrentPercentage': 50
                    }
                )
                return response
            except ClientError as e:
                if e.response['Error']['Code'] == 'OperationInProgressException':
                    this_try += 1
                    if this_try == retries:
                        print("Failed to create stack instances after {} tries".format(this_try))
                        raise Exception("Error creating stack instances: {}".format(e))
                    else:
                        print("Create stack instances operation in progress for {} in {}. Sleeping for {} seconds.".format(self.stack_setName, newregionList, sleep_time))
                        sleep(sleep_time)
                        continue
                elif e.response['Error']['Code'] == 'Throttling':
                    this_try += 1
                    if this_try == retries:
                        print("Failed to create stack instances after {} tries".format(this_try))
                        raise Exception("Error creating stack instances: {}".format(e))
                    else:
                        print("Throttling exception encountered while creating stack instances. Backing off and retyring. " "Sleeping for {} seconds.".format(sleep_time))
                        sleep(sleep_time)
                        continue
                elif e.response['Error']['Code'] == 'StackSetNotFoundException':
                    raise Exception("No StackSet matching {} found in {}. You must create before creating stack instances.".format(self.stack_setName, newregionList))
                else:
                    raise Exception("Error creating stack instances: {}".format(e))

    """Delete the stack set"""
    def delete_stack_set(self, delete_regions, delete_ou):
        # Wrapper for delete_stack_instances
        sleep_time = 15
        retries = 60
        this_try = 0
        print("Delete Stack set...")
        while True:
            try:
                """Delete the OU's and regions"""
                if (len(delete_ou) > 0 and len(delete_regions) > 0):
                    response = self.cloudformation_client.delete_stack_instances(
                        StackSetName=self.stack_setName,
                        DeploymentTargets={
                            'OrganizationalUnitIds': delete_ou
                        },
                        Regions=delete_regions,
                        OperationPreferences={
                            'FailureTolerancePercentage': 100,
                            'MaxConcurrentPercentage': 50
                        },
                        RetainStacks=False
                    )
                    return response
                elif (len(delete_ou) > 0):
                    """Delete the OU's"""
                    new_regions = self.event['ResourceProperties']['Regions']
                    newregionList = [x.strip(' ') for x in new_regions.split(",")]
                    response = self.cloudformation_client.delete_stack_instances(
                        StackSetName=self.stack_setName,
                        DeploymentTargets={
                            'OrganizationalUnitIds': delete_ou
                        },
                        Regions=newregionList,
                        OperationPreferences={
                            'FailureTolerancePercentage': 100,
                            'MaxConcurrentPercentage': 50
                        },
                        RetainStacks=False
                    )
                    return response
                else:
                    """Delete only regions"""
                    new_OUs = self.event['ResourceProperties']['OUIDs']
                    newOUList = [x.strip(' ') for x in new_OUs.split(",")]
                    response = self.cloudformation_client.delete_stack_instances(
                        StackSetName=self.stack_setName,
                        DeploymentTargets={
                            'OrganizationalUnitIds': newOUList
                        },
                        Regions=delete_regions,
                        OperationPreferences={
                            'FailureTolerancePercentage': 100,
                            'MaxConcurrentPercentage': 50
                        },
                        RetainStacks=False
                    )
                    return response
            except ClientError as e:
                if e.response['Error']['Code'] == 'OperationInProgressException':
                    this_try += 1
                    if this_try == retries:
                        print("Failed to delete stack instances after {} tries".format(this_try))
                        raise Exception("Error deleting stack instances: {}".format(e))
                    else:
                        print("Delete stack instances operation in progress for {} in {}. Sleeping for {} seconds.".format(self.stack_setName, delete_regions, sleep_time))
                        sleep(sleep_time)
                        continue
                elif e.response['Error']['Code'] == 'Throttling':
                    this_try += 1
                    if this_try == retries:
                        print("Failed to delete stack instances after {} tries".format(this_try))
                        raise Exception("Error deleting stack instances: {}".format(e))
                    else:
                        print("Throttling exception encountered while deleting stack instances. Backing off and retyring. " "Sleeping for {} seconds.".format(sleep_time))
                        sleep(sleep_time)
                        continue
                elif e.response['Error']['Code'] == 'StackSetNotFoundException':
                    return "No StackSet matching {} found in {}. You must create before deleting stack instances.".format(self.stack_setName, delete_regions)
                else:
                    return "Unexpected error: {}".format(e)

    """Check if regions are added/removed """
    def check_regions(self):
        try:
            old_regions = self.event['OldResourceProperties']['Regions']
            new_regions = self.event['ResourceProperties']['Regions']

            newregionList = [x.strip(' ') for x in new_regions.split(",")]
            oldRegionList = [x.strip(' ') for x in old_regions.split(",")]
            old_regions_not_present = []
            new_regions_present = []
            if (old_regions != ""):
                for regions in oldRegionList:
                    if regions not in newregionList:
                        old_regions_not_present.append(regions)
            if (new_regions != ""):
                for regions in newregionList:
                    if regions not in oldRegionList:
                        new_regions_present.append(regions)
            return old_regions_not_present, new_regions_present

        except Exception as e:
            raise Exception(str(e))

    """check if OU's are added/removed"""
    def check_ou(self):
        try:
            old_OUs = self.event['OldResourceProperties']['OUIDs']
            new_OUs = self.event['ResourceProperties']['OUIDs']
            newOuList = [x.strip(' ') for x in new_OUs.split(",")]
            oldOuList = [x.strip(' ') for x in old_OUs.split(",")]
            old_ou_not_present = []
            new_ou_not_present = []
            if (old_OUs != ""):
                for ou in oldOuList:
                    print(ou)
                    if ou not in newOuList:
                        print(ou)
                        old_ou_not_present.append(ou)
            if (new_OUs != ""):
                for ou in newOuList:
                    if ou not in oldOuList:
                        new_ou_not_present.append(ou)
            return old_ou_not_present, new_ou_not_present

        except Exception as e:
            raise Exception(str(e))

    def check_stack_operation(self, stack_operation_list):
        try:

            for operation in stack_operation_list:
                print(operation)
                if operation['Status'] not in ['SUCCEEDED', 'FAILED', 'CANCELLED', 'STOPPED']:
                    return False
            return True
        except Exception as e:
            raise Exception(str(e))

    """
    When performing Update the following can happen
    OperationType = 0, Cloudformation template has changed
    OperationType = 1, New Regions/OU are added
    OperationType = 2, Regions/OU is deleted
    """
    def update_with_operation_type(self,event,create_ou,create_region,delete_ou,delete_regions):
        try:
            if event['ResourceProperties']['OperationType'] == "0":
                print("Update Stack Set")
                print("region to update are as follow :",create_region )
                stacksetupdateresult = self.update_Stack_set(create_region)
                if(stacksetupdateresult):
                    print("Update Stack Set successful..")
            elif event['ResourceProperties']['OperationType'] == "1":
                print("Add Stacks to Stack Set")
                print(create_ou, create_region)
                if (len(create_ou) > 0 or len(create_region) > 0):
                    self.update_stack_set_instances()
            elif event['ResourceProperties']['OperationType'] == "2":
                print("Delete Stack form Stack Set")
                if len(delete_ou) > 0 or len(delete_regions) > 0:
                    self.delete_stack_set(delete_regions, delete_ou)

        except Exception as e:
            raise Exception(str(e))

def lambda_handler(event, context):
    try:
        stack_set_object = StackSetFormIaC(event, context)
        if (event['RequestType'] == "Create"):
            resource_id = stack_set_object.create_stack_set()

            send(
                event=event,
                context=context,
                response_status=SUCCESS,
                response_data={},
                reason_data=""
            )
        else:
            stack_operation_list = stack_set_object.list_stack_set_operations()
            print(stack_operation_list)
            if stack_set_object.check_stack_operation(stack_operation_list) == True:
                delete_regions, create_region = stack_set_object.check_regions()
                delete_ou, create_ou = stack_set_object.check_ou()
                print(delete_regions, delete_ou)
                stack_set_object.update_with_operation_type(event, create_ou, create_region, delete_ou, delete_regions)
                send(
                    event=event,
                    context=context,
                    response_status=SUCCESS,
                    response_data={},
                    reason_data=""
                )
            else:
                send(
                    event=event,
                    context=context,
                    response_status=FAILED,
                    response_data={},
                    reason_data="Stack-Set in Progress"
                )
    except Exception as e:
        print(str(e))
        send(
            event=event,
            context=context,
            response_status=FAILED,
            response_data={},
            reason_data=str(e)
        )


def send(event, context, response_status, response_data, reason_data):
    '''
    Send status to the cloudFormation
    Template.
    '''
    print("Inside send method")
    response_url = event['ResponseURL']

    response_body = {}
    response_body['Status'] = response_status
    response_body['Reason'] = reason_data + ' See the details in CloudWatch Log Stream: ' + \
                              context.log_stream_name
    if (event['RequestType'] == "Create"):
        response_body['PhysicalResourceId'] = context.log_stream_name
    else:
        response_body['PhysicalResourceId'] = event['PhysicalResourceId']

    response_body['StackId'] = event['StackId']
    response_body['RequestId'] = event['RequestId']
    response_body['LogicalResourceId'] = event['LogicalResourceId']
    response_body['Data'] = response_data

    json_responsebody = json.dumps(response_body)

    print("Response body:{}".format(json_responsebody))

    headers = {
        'content-type': '',
        'content-length': str(len(json_responsebody))
    }

    try:
        response = requests.put(response_url,
                                data=json_responsebody,
                                headers=headers)
        print("Status code:{} ".format(response.reason))
    except Exception as exception:
        print("send(..) failed executing requests.put(..):{} ".format(str(exception)))
