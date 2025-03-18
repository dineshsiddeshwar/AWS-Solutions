import json
import os
import boto3

CRAWLER_NAME = os.environ['CRAWLER_NAME']
DATABASE_NAME = os.environ['DATABASE_NAME']
TABLE_NAME = 'aws_instanceinformation'
COLUMN_NAME = 'resourcetype'
glue_client = boto3.client('glue')

def lambda_handler(event, context):
    print(json.dumps(event, default=str))
    # Get the crawler name from the event.
    event_crawler_name = event['detail']['crawlerName']
    if event_crawler_name == CRAWLER_NAME:
        # This is the crawler we're looking for, so get a reference to the right
        # table and delete the column.
        response = glue_client.get_table(
            CatalogId=context.invoked_function_arn.split(":")[4],
            DatabaseName=DATABASE_NAME,
            Name=TABLE_NAME
        )
        # Update the column name if the table exists.
        if response['Table']:
            table = response['Table']
            # We have a reference to the table, so get the columns.
            columns = table['StorageDescriptor']['Columns']
            # Remove the unwanted column.
            updated_columns = [i for i in columns if not (i['Name'] == COLUMN_NAME)]
            # Updat the columns for the table object.
            table['StorageDescriptor']['Columns'] = updated_columns
            # Remove unnecessary fields.
            table.pop('DatabaseName', None)
            table.pop('CreatedBy', None)
            table.pop('CreateTime', None)
            table.pop('UpdateTime', None)
            table.pop('IsRegisteredWithLakeFormation', None)
            table.pop('CatalogId', None)
            table.pop('VersionId', None)
            # Update the table with the removed 'resourcetype' column.
            response = glue_client.update_table(
                CatalogId=context.invoked_function_arn.split(":")[4],
                DatabaseName=DATABASE_NAME,
                TableInput=table
            )
