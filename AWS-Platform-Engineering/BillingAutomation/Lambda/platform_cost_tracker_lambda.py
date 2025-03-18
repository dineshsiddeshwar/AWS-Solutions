import time
import boto3
import pandas as pd
import io
import os 
import time
from datetime import datetime
import logging
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

athena_client = boto3.client('athena')
s3_client = boto3.client('s3')
ses_client = boto3.client('ses')
ddb_resource = boto3.resource('dynamodb')
account_id = os.environ['account_id']
athena_database = os.environ['athena_database']
athena_table = os.environ['athena_table']
s3_output_location = os.environ['s3_output_location']
s3_bucket = os.environ['s3_bucket']
main_billing_file = os.environ['main_billing_file']
cost_tracker = os.environ['cost_tracker']




def execute_query(query,previous_month,previous_month_year):
    try:
        response = athena_client.start_query_execution(
            QueryString=query,
            QueryExecutionContext={
                'Database': athena_database,
                'Catalog': "AWSDATACATALOG"        },
            ResultConfiguration={
                'OutputLocation': s3_output_location,
            })
        query_execution_file = response['QueryExecutionId'] + ".csv"
        print(query_execution_file)
        return query_execution_file
    except Exception as error:
        LOGGER.info(error)
        return error
    
def get_csv_file_from_s3(s3_bucket,key):
    try:
        response = s3_client.get_object(Bucket=s3_bucket, Key=key)
        file = pd.read_csv(response.get("Body"))
        return file
    except Exception as error:
        LOGGER.info(error)
        return error
        
def create_dataframe_for_csv(file):
    try:
        df = pd.DataFrame(file)
        return df
    except Exception as error:
        LOGGER.info(error)
        return error    


def get_item_from_ddb(account_id):
    try:
        account_details_list = []
        account_id = str(account_id)
        if (len(account_id))==11:
            account_id = '0' + account_id
        if (len(account_id))==10:
            account_id = '00' + account_id
        if (len(account_id))==9:
            account_id = '000' + account_id    
        table = ddb_resource.Table('Account_Details')
        response = table.get_item(
            Key={
                'AccountNumber': account_id
            }
        )
        item = response['Item']
        account_details_list = [str(item['RequestNo'][0]),str(item['AccountNumber']),str(item['AccountName']),'AWSatShell','AWSatShell',str(item['LoB']),str(item['SoldToCode'])]
        return account_details_list  
    except Exception as error:
        LOGGER.info(error)
        return error 

def lambda_handler(event, context):
    try:
        previous_month = datetime.now().month -1 
        if previous_month == 1:
            previous_month_year = datetime.now().year -1
        else:
            previous_month_year = datetime.now().year
        billing_query = """SELECT line_item_usage_account_id AS "Account ID",line_item_tax_type,SUM(CASE WHEN line_item_tax_type != 'VAT' and bill_bill_type = 'Anniversary' or (bill_bill_type = 'Purchase' and line_item_line_item_type = 'SavingsPlanUpfrontFee') THEN "line_item_net_unblended_cost" END) AS NetUnblendedCostWithoutVAT,SUM(CASE WHEN line_item_tax_type = 'VAT' and bill_bill_type = 'Anniversary' or (bill_bill_type = 'Purchase' and line_item_line_item_type = 'SavingsPlanUpfrontFee') THEN "line_item_net_unblended_cost" END) AS TotalVAT FROM {0}.{1} where bill_payer_account_id = '{2}' and month = '{3}' and year = '{4}' and bill_billing_entity = 'AWS' and line_item_legal_entity LIKE '%Amazon Web Services%' GROUP BY 1,2;""".format(athena_database,athena_table,account_id,previous_month, previous_month_year)
        billing_query_response = execute_query(billing_query,previous_month,previous_month_year)
        time.sleep(25)
        billing_file = get_csv_file_from_s3(s3_bucket,billing_query_response)
        s3_cost_tracker_file = get_csv_file_from_s3(s3_bucket,'cost_s3.csv')
        billing_df = create_dataframe_for_csv(billing_file)
        billing_df.drop(billing_df.index[billing_df['line_item_tax_type'] == "VAT"], inplace=True)
        billing_df.reset_index(inplace = True, drop = True)
        s3_cost_tracker_df = create_dataframe_for_csv(s3_cost_tracker_file)
        for i in range(0,len(billing_df['Account ID'])):
            response = get_item_from_ddb(billing_df['Account ID'][i])
            s3_cost_tracker_df.loc[len(s3_cost_tracker_df.index)] = response
        s3_cost_tracker_df.to_csv("/tmp/main_billing.csv",index=False)
        response = s3_client.upload_file('/tmp/main_billing.csv', s3_bucket, cost_tracker)
        return response
    except Exception as error:
        LOGGER.info(error)
        return error
    
    