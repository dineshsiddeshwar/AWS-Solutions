import csv, boto3, logging, os, datetime

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

class CfnSsMonitoring(object):
    """
    
    # Class: CFN StackSet Monitoring
    # Description: Extracts the StackSet instances status for CloudFormation Monitoring
    """
    def __init__(self, event, context):
        try:
            self.cfn_ss_inventory_bucket_name = os.environ['CFN_SS_INVENTORY_BUCKET']
            self.cfn_client = boto3.client('cloudformation')
            self.s3_client = boto3.client('s3')
            self.year = 'year=' + str(datetime.datetime.today().year)
            self.month = 'month=' + str(datetime.datetime.today().month)
            self.day = 'day=' + str(datetime.datetime.today().day)                        
        except Exception as error:
            LOGGER.info(error)
            return error

    def list_stackset_instances(self):
        """
        List all the CloudFormation StackSet Instances from StackSets in management/payer account.
        """
        try:
            print(f'Listing CloudFormation StackSet Instances for StackSet {self.stack_set_name}')

            if self.instances_next_token:
                params = {
                    'StackSetName': self.stack_set_name,
                    'NextToken': self.instances_next_token
                }
            else:
                params = {
                    'StackSetName': self.stack_set_name
                }
            
            cfn_ss_response = self.cfn_client.list_stack_instances(**params)
            ss_instances_summary = cfn_ss_response['Summaries']
            instances_next_token = cfn_ss_response.get('NextToken')

            return ss_instances_summary, instances_next_token
        
        except Exception as ex:
            print(ex)
            print("Coming from exception of list_stackset_instances method")
            return False

    def list_stacksets(self):
        """
        List all the CloudFormation StackSets in management/payer account.
        """
        try:
            print("Listing CloudFormation StackSets...")
            if self.next_token:
                params = {
                    'Status': 'ACTIVE',
                    'NextToken': self.next_token
                }
            else:
                params = {
                    'Status': 'ACTIVE'
                }

            cfn_ss_list_response = self.cfn_client.list_stack_sets(**params)
            ss_list_summary = cfn_ss_list_response['Summaries']
            ss_next_token = cfn_ss_list_response.get('NextToken')

            return ss_list_summary, ss_next_token
        
        except Exception as ex:
            print(ex)
            print("Exception from list_stacksets method")
            return False

    def get_cfn_data(self):
        """
        Fetches all the required CloudFormation inventory data for StackSets and StackSet instances
        """
        self.ss_instances = []
        self.next_token = None
        try:
            while True:
                self.stackset_list, self.next_token = self.list_stacksets()

                for stackset in self.stackset_list:
                    self.stack_set_name = stackset['StackSetName']
                    self.instances_next_token = None

                    while True:
                        self.instances, self.instances_next_token = self.list_stackset_instances()

                        for ss_instance in self.instances:
                            ss_instance_details = {
                                'StackSetName': self.stack_set_name,
                                'StackId': None,
                                'Account': ss_instance['Account'],
                                'Region': ss_instance['Region'],
                                'Status': ss_instance['Status'],
                                'StatusReason': None, 
                                'StackInstanceStatus': None,
                                'LastOperationId': ss_instance['LastOperationId']
                            }
                            if 'StackId' in ss_instance.keys():
                                ss_instance_details['StackId'] = ss_instance['StackId']
                            if 'StatusReason' in ss_instance.keys():
                                ss_instance_details['StatusReason'] = ss_instance['StatusReason']
                            if 'DetailedStatus' in ss_instance['StackInstanceStatus'].keys():
                                ss_instance_details['StackInstanceStatus'] = ss_instance['StackInstanceStatus']['DetailedStatus']
                            self.ss_instances.append(ss_instance_details)
                        
                        if not self.instances_next_token:
                            break
                
                if not self.next_token:
                    break
        
        except Exception as ex:
            print(ex)
            print("Exception from get_cfn_data method")
            return False

    def upload_json_to_s3(self):
        """
        Uploads the CloudFormation StackSet inventory data to S3 bucket for visualization.
        """
        try:
            list_ss_instances_response = self.get_cfn_data()

            csv_file_name = "cfn_ss_inventory.csv"
            file_path = "/tmp/" + csv_file_name
            key = '/'.join([self.year,self.month,self.day,csv_file_name])
            print("List of StackSet Instances:")
            print(self.ss_instances)

            header = self.ss_instances[0].keys()

            with open(file_path, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=header, quoting=csv.QUOTE_ALL)

                writer.writeheader()

                for data in self.ss_instances:
                    writer.writerow(data)

            self.s3_client.upload_file(
                file_path, self.cfn_ss_inventory_bucket_name, key
            )
            
            return True

        except Exception as ex:
            print(ex)
            print("Exception from upload_json_to_s3 method")
            return False


def lambda_handler(event, context):
    """
    CFN_StackSet_Monitoring Lambda function handler
    """
    try:
        cfn_ss_monitoring = CfnSsMonitoring(event, context)
        cfn_list_response = cfn_ss_monitoring.upload_json_to_s3()
        return True

    except Exception as ex:
        print(ex)
        print("Coming from exception of lambda_handler method")
        return event