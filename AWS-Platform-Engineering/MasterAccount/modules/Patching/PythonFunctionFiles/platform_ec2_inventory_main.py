# accoutlist lambda

import boto3

organizations_client = boto3.client('organizations')

class ListAccounts(object):

    def __init__(self, event, context):
        try:
            print("init complete")
        except Exception as exception:
            print("unable to init")
            raise Exception(str(exception))

    def get_accounts(self):
        account_list = []
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
                        account_details = {"accountNumber": account_id, "AccountType": account_type}
                        account_list.append(account_details)
                except Exception as exception:
                    print(exception)
        return account_list

def lambda_handler(event, context):
    list_accounts = ListAccounts(event, context)
    accounts_list = list_accounts.get_accounts()
    return {
        'statusCode': 200,
        'Payload': accounts_list
    }
