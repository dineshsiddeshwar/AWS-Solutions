'''
This module is used to enable CIS AWS Foundations Benchmark v1.4.0 across all the accounts
'''

import random
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

child_account_role_session_name = 'ChildAccountSession-' + str(random.randint(1, 100000))

class EnableCISBenchmark(object):
    '''
    # Description: Enables CIS Foundation Benchmark version 1.4.0
    '''

    def __init__(self, event, context):
        try:
            session_client = boto3.Session()
            self.event = event
            self.context = context
            self.sts_client = session_client.client('sts')
            ssm_client = boto3.client('ssm')
            logger.info('Event: %s' % self.event)
            logger.info('Context: %s' % self.context)
            
            # parameter value
            if event['detail']['eventName'] == 'UpdateManagedAccount':
                 self.child_account_number = event['detail']['serviceEventDetails']['updateManagedAccountStatus']['account']['accountId']
                 self.account_status =  'updateManagedAccountStatus'
            else:
                self.child_account_number = event['detail']['serviceEventDetails']['createManagedAccountStatus']['account']['accountId']      
                self.account_status =  'createManagedAccountStatus'
            #Seggragate regions environment wise
            if "Private" in event['detail']['serviceEventDetails'][ self.account_status]['organizationalUnit']['organizationalUnitName'] or "Hybrid" in event['detail']\
            ['serviceEventDetails'][ self.account_status]['organizationalUnit']['organizationalUnitName']:
                self.whitelisted_regions_response = ssm_client.get_parameter(Name='whitelisted_regions_private')
                self.whitelisted_regions = self.whitelisted_regions_response['Parameter']['Value'].split(',')
            else:
                self.whitelisted_regions_response = ssm_client.get_parameter(Name='whitelisted_regions_public')
                self.whitelisted_regions = self.whitelisted_regions_response['Parameter']['Value'].split(',')


            # Assume role in child Account
            self.child_account_arn = 'arn:aws:iam::{}:role/AWSControlTowerExecution'.format(self.child_account_number)
            self.child_account_sessionname = 'linkedAccountSession-' + str(random.randint(1, 100000))
            child_account_role_creds = self.sts_client.assume_role(RoleArn=self.child_account_arn, RoleSessionName=self.child_account_sessionname)
            child_credentials = child_account_role_creds.get('Credentials')
            child_access_keyid = child_credentials.get('AccessKeyId')
            child_secret_access_key = child_credentials.get('SecretAccessKey')
            child_session_token = child_credentials.get('SessionToken')
    
            self.assumeRoleSession = boto3.Session(child_access_keyid, child_secret_access_key, child_session_token)
            
        except Exception as e:
            print(str(e))
            logger.debug(str(e))
            raise Exception(str(e))
        

    def invoke_enablement(self):
        '''Invoke the Lambda function for each child account to enable the CIS foundation benchmark version 1.4.0'''
        try:
            for region in self.whitelisted_regions:
                try:
                    securityhub = self.assumeRoleSession.client('securityhub', region_name=region)
                    
                    #Change it to the desired standard to enable
                    standardArn=f'arn:aws:securityhub:{region}::standards/cis-aws-foundations-benchmark/v/1.4.0'
                    print(standardArn)
                    
                    standards_subscription_request = [{'StandardsArn': standardArn}]
                    if (self.event['detail']['eventName'] == 'CreateManagedAccount' or self.event['detail']['eventName'] == 'UpdateManagedAccount'):
                                        
                            securityhub.batch_enable_standards(StandardsSubscriptionRequests=standards_subscription_request)
                            print('Security Hub standard enabled')

                except Exception as e:
                    print("region failed in loop -", region)
                    print(str(e))
                    logger.debug(str(e))
                    continue 
        except Exception as ex:
                    print('failed executing actions: ' + str(ex))
        return

def lambda_handler(event, context):
    '''
    Lambda handler calls the function that Enables CIS in child accounts
    '''
    try:
        enable_obj = EnableCISBenchmark(event, context)
        enable_obj.invoke_enablement()
        return event
    except Exception as e:
        logger.debug(str(e))
        print(str(e))
        raise Exception(str(e))