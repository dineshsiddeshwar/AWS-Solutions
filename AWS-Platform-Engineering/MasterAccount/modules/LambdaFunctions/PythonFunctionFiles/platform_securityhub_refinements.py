'''
Security Hub Controls Refinement as part of PBI - 328593
https://docs.aws.amazon.com/cli/latest/reference/securityhub/update-standards-control.html
'''
import logging
import random
import boto3

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
LOGGER.addHandler(CH)


class SecurityHubRefinements(object):
    """
    # Security Hub Controls Refinement as part of PBI - 328593
    """

    def __init__(self, event, context):
        self.event = event
        self.context = context
        LOGGER.info("Event: %s" % self.event)
        LOGGER.info("Context: %s" % self.context)
        try:
            self.reason_data = ""
            self.res_dict = {}
            session_client = boto3.Session()
            self.sts_client = session_client.client('sts')
            self.ssm_client = session_client.client('ssm')
            self.child_account_number = event['accountNumber']
            print(self.child_account_number)
            self.private_region = event['SSMParametres']['whitelisted_regions_private'].split(',')
            print("Private Regions are ", self.private_region)
            self.public_region = event['SSMParametres']['whitelisted_regions_public'].split(',')
            print("Public Regions are ", self.public_region)
            self.child_account_arn = "arn:aws:iam::{}:role/AWSControlTowerExecution". \
                format(self.child_account_number)
            self.child_account_sessionname = "linkedAccountSession-" + \
                                             str(random.randint(1, 100000))
            child_account_role_creds = self.sts_client.assume_role \
                (RoleArn=self.child_account_arn, RoleSessionName=self.child_account_sessionname)
            child_credentials = child_account_role_creds.get('Credentials')
            child_access_keyid = child_credentials.get('AccessKeyId')
            child_secret_access_key = child_credentials.get('SecretAccessKey')
            child_session_token = child_credentials.get('SessionToken')
            self.child_assume_role_session = boto3.Session(child_access_keyid, child_secret_access_key,
                                                           child_session_token)
        except Exception as exception:
            self.reason_data = "Missing required property %s" % exception
            LOGGER.error(self.reason_data)
            raise Exception(str(exception))

    def refine_securityhub_public(self, CIS_AWS_Securityhub_Controls, AWS_Securityhub_Controls):
        '''
        Security Hub Controls Refinement as part of PBI - 328593 - Public
        '''
        try:
            for region in self.public_region:
                print(region)
                self.securityhub_childaccount_client = self.child_assume_role_session.client('securityhub', region_name=region)
                for CIS_Controls in CIS_AWS_Securityhub_Controls:
                    DynamicStandardsControlArn ="arn:aws:securityhub:{}:{}:subscription/cis-aws-foundations-benchmark/v/1.2.0/{}".format(region, self.child_account_number, CIS_Controls )
                    print("ARN is : {}".format(DynamicStandardsControlArn))
                    awsresponse = self.securityhub_childaccount_client.update_standards_control(StandardsControlArn=DynamicStandardsControlArn,ControlStatus='DISABLED',DisabledReason='As part of security hub refinement')
                    print("Successfully updated the security hub controls of CIS in public and response is:{}".format(awsresponse))

                for AWS_Controls in AWS_Securityhub_Controls:
                    DynamicStandardsControlArn ="arn:aws:securityhub:{}:{}:subscription/aws-foundational-security-best-practices/v/1.0.0/{}".format(region, self.child_account_number, AWS_Controls )
                    print("ARN is : {}".format(DynamicStandardsControlArn))
                    if(AWS_Controls == "SSM.1"):
                        awsresponse = self.securityhub_childaccount_client.update_standards_control(StandardsControlArn=DynamicStandardsControlArn,ControlStatus='ENABLED')
                    else:
                        awsresponse = self.securityhub_childaccount_client.update_standards_control(StandardsControlArn=DynamicStandardsControlArn,ControlStatus='DISABLED',DisabledReason='As part of security hub refinement')
                    print("Successfully updated the security hub controls of AWS in public and response is:{}".format(awsresponse))
                self.res_dict['security_hub_refinement_public'] = "PASSED"
        except Exception as exception:
            print("Exception occurred while disabling some of security hub controls in public and error is : {}".format(str(exception)))
            self.res_dict['security_hub_refinement_public'] = "FAILED"
            return self.res_dict

    def refine_securityhub_private(self, CIS_AWS_Securityhub_Controls, AWS_Securityhub_Controls):
        '''
        Security Hub Controls Refinement as part of PBI - 328593 - Private
        '''
        try:
            for region in self.private_region:
                print(region)
                self.securityhub_childaccount_client = self.child_assume_role_session.client('securityhub', region_name=region)
                for CIS_Controls in CIS_AWS_Securityhub_Controls:
                    DynamicStandardsControlArn ="arn:aws:securityhub:{}:{}:subscription/cis-aws-foundations-benchmark/v/1.2.0/{}".format(region, self.child_account_number, CIS_Controls )
                    print("ARN is : {}".format(DynamicStandardsControlArn))
                    awsresponse = self.securityhub_childaccount_client.update_standards_control(StandardsControlArn=DynamicStandardsControlArn,ControlStatus='DISABLED',DisabledReason='As part of security hub refinement')
                    print("Successfully updated the security hub controls of CIS in private and response is:{}".format(awsresponse))
                    
                for AWS_Controls in AWS_Securityhub_Controls:
                    DynamicStandardsControlArn ="arn:aws:securityhub:{}:{}:subscription/aws-foundational-security-best-practices/v/1.0.0/{}".format(region, self.child_account_number, AWS_Controls )
                    print("ARN is : {}".format(DynamicStandardsControlArn))
                    if(AWS_Controls == "SSM.1"):
                        awsresponse = self.securityhub_childaccount_client.update_standards_control(StandardsControlArn=DynamicStandardsControlArn,ControlStatus='ENABLED')
                    else:
                        awsresponse = self.securityhub_childaccount_client.update_standards_control(StandardsControlArn=DynamicStandardsControlArn,ControlStatus='DISABLED',DisabledReason='As part of security hub refinement')
                    print("Successfully updated the security hub controls of AWS in private and response is:{}".format(awsresponse))
                self.res_dict['security_hub_refinement_private'] = "PASSED"
        except Exception as exception:
            print("Exception occurred while disabling some of security hub controls in private and error is : {}".format(str(exception)))
            self.res_dict['security_hub_refinement_private'] = "FAILED"
            return self.res_dict

    def add_childaccount_SSMparameters(self, whitelisted_regions, accounttype, ostype, amiowner, amitag):
        '''
        Security Hub Controls Refinement as part of PBI - 328593 - Private
        Updated to add the Child account level SSM parameters in 'us-east-1' region
        '''
        try:
            self.ssm_childaccount_client = self.child_assume_role_session.client('ssm', region_name='us-east-1')

            ## platform_whitelisted_regions - SSM parameters
            region_response = self.ssm_childaccount_client.put_parameter(
                                Name='platform_whitelisted_regions',
                                Description='AWS@Shell platform whitelisted regions',
                                Value=whitelisted_regions,
                                Type='String',
                                Overwrite=True
                            )
            if region_response:
                print("platform_whitelisted_regions SSM parameter added successfully..")
            else:
                print("platform_whitelisted_regions SSM parameter add failed..!")

            ## platform_account_type - SSM parameters
            accounttype_response = self.ssm_childaccount_client.put_parameter(
                                Name='platform_account_type',
                                Description='AWS@Shell platform account type',
                                Value=accounttype,
                                Type='String',
                                Overwrite=True
                            )
            if accounttype_response:
                print("platform_account_type SSM parameter added successfully..")
            else:
                print("platform_account_type SSM parameter add failed..!")

            ## platform_TOE_Complaint_OS_list - SSM parameters
            ostype_response = self.ssm_childaccount_client.put_parameter(
                                Name='platform_TOE_Complaint_OS_list',
                                Description='AWS@Shell platform TOE Complaint OS list',
                                Value=ostype,
                                Type='StringList',
                                Overwrite=True
                            )
            if ostype_response:
                print("platform_TOE_Complaint_OS_list SSM parameter added successfully..")
            else:
                print("platform_TOE_Complaint_OS_list SSM parameter add failed..!")

            ## platform_ami_owner_account - SSM parameters
            amiowner_response = self.ssm_childaccount_client.put_parameter(
                                Name='platform_ami_owner_account',
                                Description='AWS@Shell platform ami owner account list',
                                Value=amiowner,
                                Type='StringList',
                                Overwrite=True
                            )
            if amiowner_response:
                print("platform_ami_owner_account SSM parameter added successfully..")
            else:
                print("platform_ami_owner_account SSM parameter add failed..!")

            ## platform_ami_tags - SSM parameters
            amitag_response = self.ssm_childaccount_client.put_parameter(
                                Name='platform_ami_tags',
                                Description='AWS@Shell platform ami tags list',
                                Value=amitag,
                                Type='StringList',
                                Overwrite=True
                            )
            if amitag_response:
                print("platform_ami_tags SSM parameter added successfully..")
            else:
                print("platform_ami_tags SSM parameter add failed..!")

            self.res_dict['add_childaccount_SSMparameters'] = "PASSED"
        except Exception as exception:
            print("Exception occurred while adding childaccount SSM parameters and error is : {}".format(str(exception)))
            self.res_dict['add_childaccount_SSMparameters'] = "FAILED"
            return self.res_dict
        

def lambda_handler(event, context):
    """"
    # Security Hub Controls Refinement as part of PBI - 328593
    """
    try:
        CIS_AWS_Securityhub_Controls = ["1.14"]
        AWS_Securityhub_Controls = ["IAM.6", "ELB.3", "SSM.1"]
        result_values = {}
        result_values.update(event)
        print("Event {}".format(event))
        create_securityhub_obj = SecurityHubRefinements(event, context)
        account_type = event['ResourceProperties']['AccountType']
        if 'private' in account_type:
            print('account is private')
            create_securityhub_obj.refine_securityhub_private(CIS_AWS_Securityhub_Controls, AWS_Securityhub_Controls)
            create_securityhub_obj.add_childaccount_SSMparameters(event['SSMParametres']['whitelisted_regions_private'], event['ResourceProperties']['AccountType'], event['SSMParametres']['TOE_Complaint_OS_Flavours_Private'], event['SSMParametres']['ami_owner_account'], event['SSMParametres']['ami_tags'] )
            result_values.update(create_securityhub_obj.res_dict)
            return result_values
        elif 'hybrid' in account_type:
            print('account is private')
            create_securityhub_obj.refine_securityhub_private(CIS_AWS_Securityhub_Controls, AWS_Securityhub_Controls)
            create_securityhub_obj.add_childaccount_SSMparameters(event['SSMParametres']['whitelisted_regions_private'], event['ResourceProperties']['AccountType'], event['SSMParametres']['TOE_Complaint_OS_Flavours_Private'], event['SSMParametres']['ami_owner_account'], event['SSMParametres']['ami_tags'] )
            result_values.update(create_securityhub_obj.res_dict)
            return result_values
        elif 'public' in account_type or 'Managed_Services' in account_type or 'Data-Management' in account_type or 'Migration' in account_type:
            print('its public account')
            create_securityhub_obj.refine_securityhub_public(CIS_AWS_Securityhub_Controls, AWS_Securityhub_Controls)
            create_securityhub_obj.add_childaccount_SSMparameters(event['SSMParametres']['whitelisted_regions_public'], event['ResourceProperties']['AccountType'], event['SSMParametres']['TOE_Complaint_OS_Flavours_Public'], event['SSMParametres']['ami_owner_account'], event['SSMParametres']['ami_tags'] )
            result_values.update(create_securityhub_obj.res_dict)
            return result_values
        else:
            print("Security Hub Controls Refinement failed")
            return result_values
    except Exception as exception:
        print("Exception in Lambda Handler", exception)
        return event