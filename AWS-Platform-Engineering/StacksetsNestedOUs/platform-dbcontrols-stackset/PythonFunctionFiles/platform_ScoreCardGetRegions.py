import json
import boto3
import time
import datetime
import os
import random
import time
def lambda_handler(event, context):


    ssm_client = boto3.client('ssm')
    regions_response = ssm_client.get_parameter(Name='platform_whitelisted_regions')
    regions_results = regions_response['Parameter']['Value']
    regions = regions_results.split(',')
    region_dicts = [{"region": r} for r in regions]
    print(region_dicts)
    regionsOutput = json.dumps(regions)
    delay = random.uniform(1,200)
    time.sleep(delay)

    # print(regionsOutput)
    
    return {
        'regions':region_dicts
    }