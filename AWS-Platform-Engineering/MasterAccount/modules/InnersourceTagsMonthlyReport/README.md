# AWS-at-Shell-Platform-Engineering
This repository is for creating monthly report for IT engineering Team for the resoources that are created using terraform innersource modules and having tag as "Platform_IAC_Source".

## Fetching Config Aggregator Data

Config Aggregator is used to get all the relevant data.


## Storing in s3 bucket

 Output of config query is a JSON file and stored in s3 bucket.

The query runs on monthly basis and saves the data in S3 bucket then code converts it into csv file and sends it to the recipients over email.

This csv file contains these fields:

accountId,resourceName,resourceType,awsRegion,tags

## Bucket and Lambda Details

Lambda Name - platform_monthly_innersource_report
S3 Bucket Name - platform-innersource-tags-monthly-report-{PayerAccountID}

## Lambda Trigger

Lambda is triggered 1st of every month at 5 AM UTC.
