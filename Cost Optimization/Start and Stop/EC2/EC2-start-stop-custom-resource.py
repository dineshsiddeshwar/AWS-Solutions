import requests
import boto3
import json
from datetime import datetime, timedelta
import random

SUCCESS = 'SUCCESS'
FAILED = 'FAILED'


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
        if 'PhysicalResourceId' in event:
            response_body['PhysicalResourceId'] = event['PhysicalResourceId']
        else:
            response_body['PhysicalResourceId'] = context.log_stream_name
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

def delete_document(ssm_client,name):
    try:
        response = ssm_client.delete_document(Name=name)
        if response:
            return True
        else:
            raise f"SOmething went wrong in deleting document {name}"
    except Exception as ex:
        raise ex

def create_document(ssm_client,name,content):
    try:
        print(f"Inside create document {name}")
        ssm_response = ssm_client.create_document(
                    Content=content,
                    Name=name,
                    DocumentType='Automation',
                    DocumentFormat='YAML'
                )
        if ssm_response:
            return True
        else:
            raise f"Something went wrong in create document {name}"
    except Exception as ex:
        if 'DocumentAlreadyExists' in str(ex):
            return True
        elif 'DocumentLimitExceeded' in str(ex):
            raise "Document limit exceeded. Please delete few documents"
        raise ex

def next_weekday(weekday_name,next_day):
    # Days of the week mapping (Monday is 0, Sunday is 6)
    weekdays = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6}
    today = datetime.today()
    today_weekday = today.weekday()
    target_weekday = weekdays[weekday_name]
    if not next_day:
        if today_weekday < target_weekday:
            days_to_next = target_weekday - today_weekday
        else:
            days_to_next = 7 - today_weekday + target_weekday
        next_occurrence = today + timedelta(days=days_to_next)
    else:
        days_until_saturday = (target_weekday - today_weekday + 7) % 7 + 7
        next_occurrence = today + timedelta(days=days_until_saturday)
    return next_occurrence.strftime("%Y-%m-%d")

def get_start_end_date(StartWeekDay,StopWeekDay,next_day):
    try:
        return next_weekday(StartWeekDay,next_day),next_weekday(StopWeekDay,next_day)
    except Exception as ex:
        print(ex)
        raise ex
    
def delete_caledar(ResourceProperties):
    try:
        print("Inside delete calendar")
        ssm_client = boto3.client("ssm", region_name=ResourceProperties['Region'])
        calendar_name =f"Solventum-{ResourceProperties['ResourceType']}-scheduler-{ResourceProperties['TagKey']}-{ResourceProperties['TagValue']}-{ResourceProperties['UID']}"
        response = ssm_client.delete_document(Name=calendar_name)
        if response:
            return SUCCESS
        else:
            raise f"SOmething went wrong in deleting document Solvnetum calendar document"
    except Exception as ex:
        raise ex
    
def update_caledar(ResourceProperties,calendar_name):
    
    try:
        print("Inside update calendar")
        ssm_client = boto3.client("ssm", region_name=ResourceProperties['Region'])
        StartTime = ResourceProperties['StartTime'].replace(":","")
        StopTime = ResourceProperties['StopTime'].replace(":","")
        StartWeekDay = ResourceProperties['StartWeekDay']
        StopWeekDay = ResourceProperties['StopWeekDay']
        StartDate, Enddate = get_start_end_date(StartWeekDay,StopWeekDay,None)
        if StartDate > Enddate:
            Enddate = next_weekday(StopWeekDay,True)
        icalendar = f"""BEGIN:VCALENDAR\nX-CALENDAR-TYPE:DEFAULT_CLOSED\nVERSION:2.0\nPRODID:-//AWS//Change Calendar 1.0//EN\nBEGIN:VEVENT\nUID:{str(random.randint(100000000, 200000000))}\nSEQUENCE:0\nDTSTAMP:{str(datetime.today().strftime("%Y%m%d"))}Z\nDTSTART;TZID={ResourceProperties['ScheduleTimeZone']}:{str(StartDate).replace("-","")}T{StartTime}\nDTEND;TZID={ResourceProperties['ScheduleTimeZone']}:{str(Enddate).replace("-","")}T{StopTime}\nRRULE:FREQ=WEEKLY;\nSUMMARY: {ResourceProperties['ResourceType']} {ResourceProperties['TagKey']} {ResourceProperties['ScheduleTimeZone']} Calender\nEND:VEVENT\nEND:VCALENDAR"""
        ssm_response = ssm_client.update_document(
                    Content=icalendar,
                    Name=calendar_name,
                    DocumentVersion="$LATEST",
                    DocumentFormat='TEXT'
                )
        if ssm_response:
            return SUCCESS
        else:
            raise f"Something went wrong in create document {calendar_name}"
        
    except Exception as ex:
        raise ex


    
def create_caledar(ResourceProperties,calendar_name):
    try:
        print("Inside Create calendar")
        ssm_client = boto3.client("ssm", region_name=ResourceProperties['Region'])
        StartTime = ResourceProperties['StartTime'].replace(":","")
        StopTime = ResourceProperties['StopTime'].replace(":","")
        StartWeekDay = ResourceProperties['StartWeekDay']
        StopWeekDay = ResourceProperties['StopWeekDay']
        StartDate, Enddate = get_start_end_date(StartWeekDay,StopWeekDay,None)
        if StartDate > Enddate:
            Enddate = next_weekday(StopWeekDay,True)
        icalendar = f"""BEGIN:VCALENDAR\nX-CALENDAR-TYPE:DEFAULT_CLOSED\nVERSION:2.0\nPRODID:-//AWS//Change Calendar 1.0//EN\nBEGIN:VEVENT\nUID:{str(random.randint(100000000, 200000000))}\nSEQUENCE:0\nDTSTAMP:{str(datetime.today().strftime("%Y%m%d"))}Z\nDTSTART;TZID={ResourceProperties['ScheduleTimeZone']}:{str(StartDate).replace("-","")}T{StartTime}\nDTEND;TZID={ResourceProperties['ScheduleTimeZone']}:{str(Enddate).replace("-","")}T{StopTime}\nRRULE:FREQ=WEEKLY;\nSUMMARY: {ResourceProperties['ResourceType']} {ResourceProperties['TagKey']} {ResourceProperties['ScheduleTimeZone']} Calender\nEND:VEVENT\nEND:VCALENDAR"""
        ssm_response = ssm_client.create_document(
                    Content=icalendar,
                    Name=calendar_name,
                    DocumentType='ChangeCalendar',
                    DocumentFormat='TEXT'
                )
        if ssm_response:
            return SUCCESS
        else:
            raise f"Something went wrong in create document {calendar_name}"
    except Exception as ex:
        if 'DocumentAlreadyExists' in str(ex):
            ssm_response = ssm_client.update_document(
                    Content=icalendar,
                    Name=calendar_name,
                    DocumentVersion="$LATEST",
                    DocumentFormat='TEXT'
                )
            if ssm_response:
                return SUCCESS
        raise ex

def create_all_document(ResourceProperties):
    try:
        ssm_client = boto3.client("ssm", region_name=ResourceProperties['Region'])
        startassocdocument = """
        description: |
          ### Document Name - StartStateManagerAssociations
          ## What does this document do?
          This document starts the State Manager Association

          ## Input Parameters
          * AutomationAssumeRole: (Required) The ARN of the IAM role that this runboon will use to execution automation.
          * Association IDs: (Required) The association IDs that you want to run immediately and only one time.
        schemaVersion: '0.3'
        assumeRole: '{{ AutomationAssumeRole }}'
        parameters:
          AssociationIDs:
            type: StringList
            description: List of the State Manager Association IDs to start
          AutomationAssumeRole:
            type: String
            description: (Required) The ARN of the role that allows Automation to perform the actions on your behalf.
        mainSteps:
          - name: StartAssociation
            action: aws:executeAwsApi
            inputs:
              Service: ssm
              Api: StartAssociationsOnce
              AssociationIds: '{{ AssociationIDs }}'
        """
        create_document(ssm_client,"Solventum-start-association-Document-EC2",startassocdocument)
        start = """
        description: |
          ### Document Name - EC2StartSSMDocument
          ## What does this document do?
          This document finds the tagged EC2 instances and start them.

          ## Input Parameters
          * TagKey: (Required) Tag Key to filter list of EC2 Instances
          * TagValue: (Required) Tag Value to filter list of EC2 Instances
          * ResourceTagMapList: (Required) The tags to add to the resources.
        schemaVersion: '0.3'
        assumeRole: '{{ AutomationAssumeRole }}'
        parameters:
          TargetTagKey:
            type: String
            description: (Required) The tag name (key) to filter list of EC2 Instances
          TargetTagValue:
            type: String
            description: (Required) The change calendar name to filter list of EC2 Instances
          AutomationAssumeRole:
            type: String
            description: Automation role to be used by the runbook
            default: ''
          ChangeCalendarName:
            type: String
            description: Name of change calendar to use
            default: ''
        outputs:
          - startInstances.OutputPayload
        mainSteps:
          - name: startInstances
            description: Start the selected instances
            maxAttempts: 3
            action: aws:executeScript
            timeoutSeconds: 600
            onFailure: Abort
            inputs:
              Runtime: python3.8
              Handler: start_instances
              InputPayload:
                tagKey: '{{TargetTagKey}}'
                tagValue: '{{TargetTagValue}}'
                changeCalendarName: '{{ChangeCalendarName}}'
              Script: |
                def start_instances(events, context):
                    import boto3
                    import time

                    # Initialize boto clients
                    ec2_resource = boto3.resource('ec2')
                    ec2_client = boto3.client('ec2')
                    ssm_client = boto3.client('ssm')

                    # Get input values to the script
                    tag_key = events['tagKey']
                    tag_value = events['tagValue']
                    change_calendar_name = events['changeCalendarName']

                    # Define the constant batch size for number of instances started/stopped in one boto call
                    batch_size = 1000

                    def get_calendar_state(calendar_name):
                        return ssm_client.get_calendar_state(
                            CalendarNames=[calendar_name]
                        )

                    def get_tagged_instance_ids():
                        instances = ec2_resource.instances.filter(
                            Filters=[
                                {
                                    'Name': tag_key,
                                    'Values': [tag_value]
                                },
                                {
                                    'Name': 'instance-state-name',
                                    'Values': ['stopped']
                                }
                            ]
                        )

                        return [instance.id for instance in instances]

                    def create_batches(list_instance_ids):
                        for i in range(0, len(list_instance_ids), batch_size):
                            yield list_instance_ids[i:i + batch_size]

                    def start_tagged_instances(list_batches):
                        for batch in list_batches:
                            try:
                                ec2_client.start_instances(
                                    InstanceIds=batch
                                )
                            except Exception:
                                pass
                            time.sleep(0.5)

                    calendar_state = get_calendar_state(change_calendar_name)
                    if calendar_state.get('State') == 'OPEN':
                        list_tagged_instance_ids = get_tagged_instance_ids()
                        batches = create_batches(list_tagged_instance_ids)
                        start_tagged_instances(list(batches))
                        return list_tagged_instance_ids
        """
        create_document(ssm_client,"Solventum-start-SSM-Document-EC2",start)
        stop = """
        description: |
          ### Document Name - EC2StopSSMDocument
          ## What does this document do?
          This document finds the tagged EC2 instances and stops them.

          ## Input Parameters
          * TargetTagKey: (Required) Tag Key to filter list of EC2 Instances
          * TagValue: (Required) Tag Value to filter list of EC2 Instances
          * ResourceTagMapList: (Required) The tags to add to the resources.
        schemaVersion: '0.3'
        assumeRole: '{{ AutomationAssumeRole }}'
        parameters:
          TargetTagKey:
            type: String
            description: (Required) The tag name (key) to filter list of EC2 Instances
          TargetTagValue:
            type: String
            description: (Required) The change calendar name (tag value) to filter list of EC2 Instances
          AutomationAssumeRole:
            type: String
            description: Automation role to be used by the runbook
            default: ''
          ChangeCalendarName:
            type: String
            description: Name of change calendar to use
            default: ''
        outputs:
          - stopInstances.OutputPayload
        mainSteps:
          - name: stopInstances
            description: Start the selected instances
            maxAttempts: 3
            action: aws:executeScript
            timeoutSeconds: 600
            onFailure: Abort
            inputs:
              Runtime: python3.8
              Handler: stop_instances
              InputPayload:
                tagKey: '{{TargetTagKey}}'
                tagValue: '{{TargetTagValue}}'
                changeCalendarName: '{{ChangeCalendarName}}'
              Script: |
                def stop_instances(events, context):
                    import boto3
                    import time

                    # Initialize boto clients
                    ec2_resource = boto3.resource('ec2')
                    ec2_client = boto3.client('ec2')
                    ssm_client = boto3.client('ssm')

                    # Get input values to the script
                    tag_key = events['tagKey']
                    tag_value = events['tagValue']
                    change_calendar_name = events['changeCalendarName']

                    # Define the constant batch size for number of instances started/stopped in one boto call
                    batch_size = 1000

                    def get_calendar_state(calendar_name):
                        return ssm_client.get_calendar_state(
                            CalendarNames=[calendar_name]
                        )

                    def get_tagged_instance_ids():
                        instances = ec2_resource.instances.filter(
                            Filters=[
                                {
                                    'Name': tag_key,
                                    'Values': [tag_value]
                                },
                                {
                                    'Name': 'instance-state-name',
                                    'Values': ['running']
                                }
                            ]
                        )

                        return [instance.id for instance in instances]

                    def create_batches(list_instance_ids):
                        for i in range(0, len(list_instance_ids), batch_size):
                            yield list_instance_ids[i:i + batch_size]

                    def stop_tagged_instances(list_batches):
                        for batch in list_batches:
                            try:
                                ec2_client.stop_instances(
                                    InstanceIds=batch
                                )
                            except Exception:
                                pass
                            time.sleep(0.5)

                    calendar_state = get_calendar_state(change_calendar_name)
                    if calendar_state.get('State') == 'CLOSED':
                        list_tagged_instance_ids = get_tagged_instance_ids()
                        batches = create_batches(list_tagged_instance_ids)
                        stop_tagged_instances(list(batches))
                        return list_tagged_instance_ids
        """
        create_document(ssm_client,"Solventum-Stop-SSM-Document-EC2",stop)
        return SUCCESS
        #create_document(name,content)
    except Exception as ex:
        raise ex


def delete_all_document(ResourceProperties):
    try:
        ssm_client = boto3.client("ssm", region_name=ResourceProperties['Region'])
        delete_document(ssm_client,"Solventum-start-SSM-Document")
        delete_document(ssm_client,"Solventum-start-association-Document")
        delete_document(ssm_client,"Solventum-Stop-SSM-Document")
        return SUCCESS
    except Exception as ex:
        raise ex

def lambda_handler(event,context):
    try:
        print(event)
        response_data = {}
        print("Received a {} Request".format(event['RequestType']))
        calendar_name =f"Solventum-{event['ResourceProperties']['ResourceType']}-scheduler-{event['ResourceProperties']['TagKey']}-{event['ResourceProperties']['TagValue']}-{event['ResourceProperties']['UID']}"
        if event['RequestType'] == 'Create':
            
            response_data["CalendarCreated"] =  create_caledar(event["ResourceProperties"],calendar_name)
            response_data["DocumentCreated"] =  create_all_document(event["ResourceProperties"])

        elif event['RequestType'] == 'Update':
            if event['ResourceProperties'] != event['OldResourceProperties']:
                print("Inside checking the resource property")
                if event['ResourceProperties']['TagValue'] != event['OldResourceProperties']['TagValue'] or event['ResourceProperties']['TagKey'] != event['OldResourceProperties']['TagKey']:
                    print("There is a difference in tags")
                    response_data["CalendarUpdated"] = delete_caledar(event["OldResourceProperties"])
                    response_data["CalendarCreated"] =  create_caledar(event["ResourceProperties"],calendar_name)
                else:
                    response_data["CalendarUpdated"] =  update_caledar(event['ResourceProperties'],calendar_name)
                    response_data["DocumentUpdated"] =  SUCCESS
            else:
                response_data["CalendarUpdated"] = SUCCESS
                response_data["DocumentUpdated"] =  SUCCESS
        elif event['RequestType'] == 'Delete':
            response_data["CalendarDeleted"] =  delete_caledar(event["ResourceProperties"])
            #response_data["DocumentDeleted"] =  delete_all_document(event["ResourceProperties"])

        send(event, context, SUCCESS, response_data, "All good \n ")
    except Exception as ex:
        print(ex)
        response_data = {
             "CalendarCreated": "FAILED",
             "AssociationCreated": "FAILED",
             "DocumentCreated": "FAILED"
        }
        reason_data = "Something went wrong in the beginning of the lambda"
        send(event, context, FAILED, response_data, reason_data)
        return True
