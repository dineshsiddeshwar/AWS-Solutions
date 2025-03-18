import boto3
import logging

LOGGER = logging.getLogger('logging')
LOGGER.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
LOGGER.addHandler(CH)

SUCCESS = "SUCCESS"
FAILED = "FAILED"

SESSION = boto3.Session()
STS_CLIENT = SESSION.client('sts')
servicecatalogclient = SESSION.client('servicecatalog')


def check_provision_product_status(id, name):
    try:
        LOGGER.info("Inside check provision product status....")
        cft_product_name = 'AFPP-'+name
        avm_sc_response = servicecatalogclient.describe_provisioned_product(Id=id)
        avm_status = avm_sc_response["ProvisionedProductDetail"]["Status"]
        if avm_status == 'AVAILABLE':
            cft_response = servicecatalogclient.describe_provisioned_product(Name=cft_product_name)
            cft_status = cft_response["ProvisionedProductDetail"]["Status"]
            return cft_status
        else:
            return avm_status
    except Exception as exception:
        print("send(..) failed in checking status of the provision product:{} ".format(str(exception)))        
        return 'ERROR'

def lambda_handler(event, context):
    """
    This lambda handler will check the status of the provisioned product
    """
    try:
        LOGGER.info("Recieved the event :- ".format(event))
        modified_event = {}
        modified_event.update(event)
        status =  check_provision_product_status(event["provision_product_id"], event["provision_product_name"]) 
        modified_event.update({"provision_product_status": status})
        return modified_event
    except Exception as exception:
        print("Error in Lambda Handler", exception)
        modified_event.update({"provision_product_status": "ERROR"})
        return event