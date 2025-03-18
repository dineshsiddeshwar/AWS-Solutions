import random
import datetime
import logging
import json
import boto3

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
LOGGER.addHandler(CH)


class GetlatestAMI(object):
    '''
    This lambda triggered every 20th of month to check
    for the latest AMI
    '''

    def __init__(self, event, context):

        global session
        global master_account
        self.resultvalue = []
        session = boto3.session.Session()
        ssm_client = session.client('ssm')
        master_response = ssm_client.get_parameter(Name='master_account')
        master_account = master_response['Parameter']['Value']
        os_flavour_list = ssm_client.get_parameter(Name='TOE_Complaint_OS_Flavours')
        self.os_flavour_list = (os_flavour_list['Parameter']['Value']).split(',')
        print("OS falvour from SSM PS", type(self.os_flavour_list))
        owner = ssm_client.get_parameter(Name='ami_owner_account')
        print("ami_owners are ", owner)
        self.ami_owners = (owner['Parameter']['Value']).split(',')
        print(self.ami_owners, self.os_flavour_list)

    def get_latest_ami(self):
        """
            # Function: get_latest_ami
            # Description: Get latest ami for each os flavour
            :return:
        """
        try:
            ec2_client = session.client('ec2', region_name='us-east-1')
            for os_flavour in self.os_flavour_list:
                response = ec2_client.describe_images(
                    Owners=self.ami_owners,
                    Filters=[{'Name': 'name', 'Values': [os_flavour]},
                             {'Name': 'architecture', 'Values': ['x86_64']},
                             {'Name': 'root-device-type', 'Values': ['ebs']},
                             ]
                )
                print("Received event:{} ".format(response))
                images = sorted(response['Images'],
                                key=lambda os_flavour: os_flavour['CreationDate'], reverse=True)
                print("Images >>>>", images)
                ami_id = images[0]['ImageId']
                ami_name = os_flavour
                self.resultvalue = {'ami_id': ami_id, 'ami_name': ami_name}
                self.cis_report_workflow()

        except Exception as exception:
            print(str(exception))

    def cis_report_workflow(self):
        '''
        This lambda function is called by get latest ami lambda function,
        for calling the step function.
        '''
        try:
            step_function_name = 'CIS' + \
                                 str(datetime.datetime.now().strftime('%Y%m%d%H%M%S')) + \
                                 str(random.randint(1, 100000))
            print(step_function_name)
            step_client = boto3.client('stepfunctions')
            sf_response = step_client.start_execution(
                stateMachineArn='arn:aws:states:us-east-1:{}\
:stateMachine:platform_CISStatemachine'.format(master_account),
                name=step_function_name,
                input=json.dumps(self.resultvalue)
            )
            print(self.resultvalue)
            print("Received event:{} ".format(sf_response))
        except Exception as exception:
            print("Exception Block of cis_report_workflow...", exception)
            return exception


def lambda_handler(event, context):
    '''
    Lamda handler that calls the Step functions for each ami
    '''
    try:
        print("Event is", event)
        get_latest_ami_object = GetlatestAMI(event, context)
        out_put = get_latest_ami_object.get_latest_ami()
        print(out_put)
    except Exception as exception:
        print(str(exception))
