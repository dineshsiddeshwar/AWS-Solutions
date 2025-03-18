"""
This module is used to tag the newly vended account at Organization level
"""
import boto3
import json
import datetime

class TagAccount(object):

    def __init__(self, event):
        try:  
            self.event = event   
            session_client = boto3.session.Session()
            self.ssm_client = session_client.client('ssm')
            create_case_ccadress = self.ssm_client.get_parameter(Name='create_case_ccadress')
            self.create_case_ccadress = create_case_ccadress['Parameter']['Value']
            print("create case ccadress", self.create_case_ccadress)
            self.request_type = self.event['RequestType']
            print("request type", self.request_type)
            self.dl_for_new_account = self.event['ProvisionedProduct']['AccountDL']
            print("Account DL", self.dl_for_new_account)
            self.account_number = self.event['ProvisionedProduct']['AccountNumber']
            print("Account Number", self.account_number)
            self.completed_time_stamp = datetime.datetime.now().strftime("%Y:%m:%d:%I:%M:%S")
            print("Account Creation Time stamp", self.completed_time_stamp)
            resource_properties = self.event['RequestEventData']
            self.account_name = self.event['ProvisionedProduct']['Name']
            print("Account Name", self.account_name)
            self.budget_value = resource_properties['Budget']
            print("Budget Value", self.budget_value )
            self.line_of_business = resource_properties['LOB']
            print("LOB", self.line_of_business )
            self.is_RESPC_Account = resource_properties['IsRESPCAccount']
            print("Is RESPC", self.is_RESPC_Account )
            self.sold_to_code = resource_properties['SoldToCode']
            print("Sold to Code Value", self.sold_to_code )
            self.support_dl = resource_properties['SupportDL']
            print("Support DL", self.support_dl )
            self.request_id = resource_properties['RequestNo']
            print("Request Number", self.request_id  )
            self.custodian_user = resource_properties['CustodianUser']
            print("Custodian User", self.custodian_user )
            self.apex_id = resource_properties['ApexID']
            print("Apex ID", self.apex_id )
            self.workload_type = resource_properties['WorkLoadType']
            print("Workload Type", self.workload_type )
            self.ppid = self.event['ProvisionedProduct']['Id']
            print("Provision Product ID", self.ppid )
            self.org=self.event['ProvisionedProduct']['OU']
            print("OU Name", self.org)
        except Exception as exception:
            print("Missing required property:", exception)
    def tag_newly_vended_account(self, event):
        try:
            print('Tagging new Account')
            if self.request_type == 'Create' or self.request_type == 'Update':
                TagsList = []
                for key , value in event['RequestEventData'].items():
                    dict = {}
                    dict['Key'] = key
                    dict['Value'] = str(value)
                    print(type(dict))
                    TagsList.append(dict)
                print(type(TagsList))
                print('tagging newly vended account', self.account_number)
                client = boto3.client('organizations')
                '''
                client.tag_resource(
                    ResourceId=str(self.account_number),
                    Tags=TagsList
                )
                '''
                client.tag_resource(
                    ResourceId=str(self.account_number),
                    Tags=[{
                            'Key': 'platform_workload',
                            'Value': self.workload_type
                        }]
                )
                
            return True
        except Exception as exception:
            print('Error while adding tag to vended account', exception)
            return False

    def create_case(self, account_number,account_name,request_type):
        """
        Raise a ticket in Master account to enable technical
        support(Enterprise Support) for child account.
        :return:
        """
        try:
            session_client = boto3.session.Session()
            supp_master_client = session_client.client('support')
            print("accountNumber", account_number)
            print("accountName", account_name)
            response_describe_cases = supp_master_client.describe_cases()
            print("response_describe_cases", response_describe_cases)
            response_describe_services = supp_master_client.describe_services()
            print("response_describe_services", response_describe_services)
            res_desc_sev_level = supp_master_client.describe_severity_levels()
            print("response_describe_severity_levels", res_desc_sev_level)
            print("RequestType>>>", request_type)
            if request_type == 'Create':
                response = supp_master_client.create_case(
                    issueType="customer-service",
                    subject='Enabled Enterprise Support for account ' + account_number,
                    serviceCode='account-management',
                    categoryCode='billing',
                    severityCode='low',
                    communicationBody='Hi Team,' +
                    'Please enable Enterprise Support for newly created accounts mentioned : '
                    + account_number+" "+account_name,
                    ccEmailAddresses=[self.create_case_ccadress],
                    language='en'
                )
                print("Response>>>>", response)
                pass
            else:
                print('The request type is ' + request_type + ', so no request created')
            return True
        except Exception as exception:
            print("Error while creating enterprise support case", exception)
            exception.append(str(exception))
            return False
        
def lambda_handler(event, context):
    try:
        print(event)
        if event : 
            failCheckFlag = 0
            print("Invoking tag_newly_vended_account function..")
            TagAccountobj = TagAccount(event)
            if TagAccountobj.tag_newly_vended_account(event):
                print("Invoke tag_newly_vended_account is success..!!")
            else:
                print("Invoke tag_newly_vended_account is fialed..!!")
                failCheckFlag +=1

            print("Invoking create_case function..")
            if TagAccountobj.create_case(event['ProvisionedProduct']['AccountNumber'],event['ProvisionedProduct']['Name'], event['RequestType'] ):
                print("Enterprise support enablement success..!!")
            else:
                print("Enterprise support enablement fialed..!!")
                failCheckFlag +=1
                
        if failCheckFlag == 0:
            event['IsSupportTagComplete'] = True
        else:
            event['IsSupportTagComplete'] = False
            
        return event
    except Exception as ex:
        print("There is an error %s", str(ex))
        event['IsSupportTagComplete'] = False
        return event