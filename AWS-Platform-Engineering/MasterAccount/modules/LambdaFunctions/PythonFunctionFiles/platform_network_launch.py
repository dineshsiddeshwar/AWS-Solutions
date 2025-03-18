'''
Provision Network Request product
'''

import logging
import boto3

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
LOGGER.addHandler(CH)

SUCCESS = "SUCCESS"
"""
# INPROGRESS = "INPROGRESS"
# FAILED = "FAILED"
"""

SESSION = boto3.Session()
STS_CLIENT = SESSION.client('sts')
sc_client = SESSION.client('servicecatalog')


class ProvisionNetwork(object):
    '''
    Class: ProvisionNetwork
    Description: Includes all the properties and methods to create a new network request
    provisioned product
    '''

    def __init__(self, event, context):
        self.event = event
        self.context = context
        LOGGER.info("Event: %s" % self.event)
        LOGGER.info("Context: %s" % self.context)

        # get relevant input params from event
        self.account_number = event['accountNumber']
        self.env = event['ResourceProperties']['AccountType'].capitalize()
        self.resource_properties = event['ResourceProperties']
        session_client = boto3.Session()
        self.ssm_client = session_client.client('ssm')
        self.network_product_id = event['SSMParametres']['platform_network_product_id']
        print(self.network_product_id)

    def provision_network_product(self):
        '''
            The following function invokes th network product to create vpc and subnets in specified regions
        '''
        res = {}
        try:
            provision_artifact = " "
            provision_response = ""

            pa_res = sc_client.list_provisioning_artifacts(
                ProductId=self.network_product_id
            )
            for pa in pa_res['ProvisioningArtifactDetails']:
                if pa['Active'] == True:
                    provision_artifact = pa['Id']
                    print(pa['Id'])
            provision_response = sc_client.provision_product(
                ProductId=self.network_product_id,
                ProvisioningArtifactId=provision_artifact,
                ProvisionedProductName="Network-" + self.resource_properties['AccountName'],
                ProvisioningParameters=[
                    {
                        "Key": "AccountNumber",
                        "Value": self.account_number
                    },
                    {
                        "Key": "Environment",
                        "Value": self.env
                    },
                    {
                        "Key": "RequestNo",
                        "Value": self.resource_properties['RequestNo']
                    },
                    {
                        "Key": "NVirginia",
                        "Value": self.resource_properties['NVirginia']
                    },
                    {
                        "Key": "Ireland",
                        "Value": self.resource_properties['Ireland']
                    },
                    {
                        "Key": "Singapore",
                        "Value": self.resource_properties['Singapore']
                    },                    
                    {
                        "Key": "VPCID1",
                        "Value": ""
                    },
                    {
                        "Key": "VPCID2",
                        "Value": ""
                    },
                    {
                        "Key": "VPCID3",
                        "Value": ""
                    },
                    {
                        "Key": "VPCID4",
                        "Value": ""
                    },
                    {
                        "Key": "IsNonroutableSubnets",
                        "Value": self.resource_properties['IsNonroutableSubnets']
                    },
                    {
                        "Key": "VPCIDnonroutable",
                        "Value": ""
                    }
                ]

            )

            print(provision_response)
            self.event['Network_PP'] = 'PASSED'
        except Exception as exception:
            print(exception)

def lambda_handler(event, context):
    """ Start of the function this function will
     handle creation network product for the account"""
    result = {}
    print('event ' + str(event))
    result.update(event)
    try:
        print("Received a {} Request".format(event['RequestType']))
        product = ProvisionNetwork(event, context)
        product.provision_network_product()
        return result
    except Exception as exception:
        print(exception)
