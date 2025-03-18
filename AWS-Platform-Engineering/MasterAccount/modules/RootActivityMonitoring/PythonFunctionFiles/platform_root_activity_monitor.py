import json
import boto3
import os
import logging
import time
import datetime
import dateutil.tz
from botocore.vendored import requests

import urllib.request

# setup script logging
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

client = boto3.client('logs')
org_client = boto3.client('organizations')
s3 = boto3.resource('s3')

bucket_name = os.environ['ROOT_LOGIN_BUCKET']
exemption_days = os.environ['ExemptionDays']

def get_source_location(ip_address):
    response = urllib.request.urlopen(f"https://ipapi.co/{ip_address}/json/")
    body = response.read()
    response = json.loads(body)
    print(response)
    location_data = {
        "ip": ip_address,
        "city": response.get("city"),
        "region": response.get("region"),
        "country": response.get("country_name")
    }

    city = response.get("city")
    region = response.get("region")
    country_name = response.get("country_name")

    print(location_data)

    location = f"{city}, {region}, {country_name}"
    return location


def lambda_handler(event, context):
    account_list = []
    flag = False
    now = datetime.datetime.now(tz=dateutil.tz.gettz('UTC'))
    print(f"now--{now}")

    ip_address = event['detail']['sourceIPAddress']

    location = get_source_location(ip_address)
    event['location'] = location

    paginator = org_client.get_paginator('list_accounts')
    page_iterator = paginator.paginate()
    print(type(event["detail"]["eventTime"]))

    date_time_stamp = event["detail"]["eventTime"]

    print(type(date_time_stamp))
    print(date_time_stamp)

    # stamp = date_time_stamp.strftime("%m/%d/%Y, %H:%M:%S")

    for page in page_iterator:
        if flag == False:
            for acct in page['Accounts']:
                account_list.append(acct)
                print(f"acct---{acct}")

                if acct["Id"] == event["account"]:
                    flag = True
                    joined_date = acct['JoinedTimestamp']

                    root_activity_record_date = joined_date + datetime.timedelta(days=int(exemption_days))

                    print(f"Creation date --- {joined_date} Type -- {type(joined_date)}")
                    print(acct['Name'])

                    # Adding account Name to Event
                    event['account_name'] = acct['Name']
                    break

    # Check if account joining date is within n days
    if root_activity_record_date < now:
        print("recoding root activity")

        s3object = s3.Object(bucket_name, f"events-{date_time_stamp}.json")

        s3object.put(
            Body=(bytes(json.dumps(event).encode('UTF-8')))
        )

    else:
        print("Exempting root activity tracking for first two days")












