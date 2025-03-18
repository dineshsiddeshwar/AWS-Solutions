# accoutlist lambda

import boto3
import csv
from itertools import zip_longest
import os

organizations_client = boto3.client('organizations')
s3_client = boto3.client('s3')

class AccountsDetails(object):

    def __init__(self, event, context):
        try:
            self.bucket_name = os.environ['ACCOUNTS_DETAILS_BUCKET_NAME']            
            print("init complete")
        except Exception as exception:
            print("unable to init")
            raise Exception(str(exception))

    def get_account_name(self,account_number):
        account_name = organizations_client.describe_account(AccountId=account_number)['Account']['Name']
        return account_name

    def get_account_workload_tag(self,account_number):
        response = organizations_client.list_tags_for_resource(ResourceId=account_number)
        bc_tag = 'No workload tag'
        if response['Tags']:
            for tag in response['Tags']:
                if tag['Key']=='platform_workload':
                    bc_tag = tag['Value']
        return bc_tag
        # platform_workload=BC/Non-BC

    def create_csv(self,types,ids,names,workloads):
        file_name = "accounts_details.csv"
        file_path = "/tmp/" + file_name
        data = [types, ids, names, workloads]
        export_data = zip_longest(*data, fillvalue = '')
        with open(file_path, 'w', newline='\n') as file:
            write = csv.writer(file)
            write.writerow(('ou_name', 'account_id', 'account_name', 'account_workload'))
            write.writerows(export_data)
            file.close()
        try:
            print("Trying to upload consolidated file")
            response = s3_client.upload_file(file_path, self.bucket_name, file_name)
            print("Consolidated file uploaded successfully")
        except Exception as e:
            print('File uploaded failed {}'.format(str(e)))
            raise Exception(str(e))
            

    def get_accounts(self):
        account_types = []
        account_numbers = []
        account_names = []
        account_workload_tags = []
        paginator = organizations_client.get_paginator('list_accounts')
        page_iterator = paginator.paginate()
        for page in page_iterator:
            accounts_list = page['Accounts']
            for account in accounts_list:
                try:
                    account_id = account['Id']
                    if account['Status'] == "ACTIVE":
                        response = organizations_client.list_parents(ChildId=account_id)
                        if response['Parents'][0]['Type']=='ORGANIZATIONAL_UNIT':
                            account_type = organizations_client.describe_organizational_unit(OrganizationalUnitId=response['Parents'][0]['Id'])['OrganizationalUnit']['Name'].lower()
                        elif response['Parents'][0]['Type']=='ROOT':
                            account_type = 'root'
                        # account_name = self.get_account_name(account_id)
                        # workload_tag = self.get_account_workload_tag(account_id)
                        account_types.append(account_type)
                        account_numbers.append(account_id)
                        account_names.append(self.get_account_name(account_id))
                        account_workload_tags.append(self.get_account_workload_tag(account_id))
                        
                except Exception as exception:
                    print(account + str(exception))
                    account_types.append('No details')
                    account_numbers.append('No details')
                    account_names.append('No details')
                    account_workload_tags.append('No details')
        self.create_csv(account_types,account_numbers,account_names,account_workload_tags)


def lambda_handler(event, context):
    accounts_details = AccountsDetails(event, context)
    accounts_details.get_accounts()
