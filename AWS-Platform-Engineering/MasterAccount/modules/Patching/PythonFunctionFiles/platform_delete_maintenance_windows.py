import random
import boto3
import logging
import time
import json

organizations_client = boto3.client('organizations')

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class DeleteMaintenanceWindow(object):
    """
    # Class: DeleteMaintenanceWindow
    # Description: create maintance window
    """

    def __init__(self, event, context):
        global session
        session = boto3.session.Session()
        # get approved regions
        try:
            self.account_type = str(event['AccountType'])
            ssm_client = session.client('ssm')
            if 'private' in self.account_type:
                private_regions = ssm_client.get_parameter(Name='whitelisted_regions_private')
                self.approved_regions = (private_regions['Parameter']['Value']).split(',')
            else:
                public_regions = ssm_client.get_parameter(Name='whitelisted_regions_public')
                self.approved_regions = (public_regions['Parameter']['Value']).split(',')
        except Exception as exception:
            logger.info("unable to init")
            raise Exception(str(exception))

        # assume role in child account
        try:
            self.account_number = str(event['accountNumber'])
            self.account_name = organizations_client.describe_account(AccountId=self.account_number)['Account']['Name']
            secondary_rolearn = "arn:aws:iam::{}:role/AWSControlTowerExecution".format(self.account_number)
            secondary_session_name = "SecondarySession-" + str(random.randint(1, 100000))
            self.sts_client = session.client('sts')
            # Logging to child account.
            secondaryRoleCreds = self.sts_client.assume_role(RoleArn=secondary_rolearn,
                                                             RoleSessionName=secondary_session_name)
            credentials = secondaryRoleCreds.get('Credentials')
            accessKeyID = credentials.get('AccessKeyId')
            secretAccessKey = credentials.get('SecretAccessKey')
            sessionToken = credentials.get('SessionToken')
            self.assumeRoleSession = boto3.session.Session(accessKeyID, secretAccessKey, sessionToken)
            logger.info('Assumed in role in child account {}'.format(self.account_number))
        except Exception as exception:
            logger.info("Failed to assume role in child account {}".format(self.account_number))
            raise Exception(str(exception))

            
    def delete_maintenance_window_call(self,mw_name):
        deleted_mw = 0
        for region in self.approved_regions:
            ssm_client = self.assumeRoleSession.client('ssm',region_name=region) 
            try:
                response = ssm_client.describe_maintenance_windows(
                    Filters=[{'Key': 'Name', 'Values': [mw_name]}]
                )
                for window in response['WindowIdentities']:
                    window_id = window['WindowId']
                    # response = ssm_client.delete_maintenance_window(
                    #     WindowId=window_id
                    # )
                    response = ssm_client.update_maintenance_window(                        
                        WindowId=window_id,
                        Enabled=False
                    )
                deleted_mw = deleted_mw + 1
                logger.info("SUCCEDED MW {} deleted in child account {} in region {}".format(mw_name,self.account_number,region))
            except Exception as exp:  
                logger.info("FAILED MW {} delete failed in child account {} in region {}".format(mw_name,self.account_number,region))
        return deleted_mw
    def config_reevalute(self):
        reevaluted_reports = 0
        for region in self.approved_regions:
            try:
                config_client = self.assumeRoleSession.client('config',region_name=region)
                response = config_client.delete_evaluation_results(
                    ConfigRuleName='platform_instances_tags'
                )
                time.sleep(10)
                response = config_client.start_config_rules_evaluation(
                    ConfigRuleNames=[
                        'platform_instances_tags'
                    ]
                )
                reevaluted_reports = reevaluted_reports + 1
                logger.info("SUCCEDED config rule reevalute in child account {} in region {}".format(self.account_number,region))
            except Exception as exp:  
                logger.info("FAILED config rule reevalute in child account {} in region {}".format(self.account_number,region))
        return reevaluted_reports

def lambda_handler(event,context):
    account_number = str(event['accountNumber'])
    maintenance_window = DeleteMaintenanceWindow(event,context)
    mw_names = ['Scan', 'Patch_Window_Default', 'Patch_Window_CUSTOM_01', 'Patch_Window_CUSTOM_02']
    deleted_mw_count = 0
    for mw_name in mw_names:
        deleted_mw = maintenance_window.delete_maintenance_window_call(mw_name)
        deleted_mw_count + deleted_mw
    reevaluted_report = maintenance_window.config_reevalute()    
    return {
            'statusCode': 200,
            'body': json.dumps('In account {} deleted {} maintenance windows and reevaluted {} config reports'.format(account_number,str(deleted_mw_count),str(reevaluted_report)))
        }

