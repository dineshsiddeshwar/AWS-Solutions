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
    
def create_billing_excel(billing_df,marketplace_df,support_df,s3_cost_tracker_df):
    try:
        support_cost = support_df['line_item_unblended_cost']
        support_cost = float(support_cost)
        print(support_cost)
        billing_df = billing_df.merge(marketplace_df, how='left', on='Account ID')
        print(billing_df)
        billing_df.eval("total_support_cost = NetUnblendedCostWithoutVAT * 0", inplace = True)
        billing_df['cost'] = (billing_df['total_support_cost'] + support_cost)
        billing_df['net_cost'] = billing_df['NetUnblendedCostWithoutVAT']
        billing_df['net_cost'] = billing_df['NetUnblendedCostWithoutVAT'].sum()
        billing_df.eval("support_cost = cost * NetUnblendedCostWithoutVAT / net_cost", inplace = True)
        billing_df = billing_df.drop(columns=['line_item_tax_type', 'TotalVAT','total_support_cost','cost','net_cost'])
        s3_cost_tracker_df = s3_cost_tracker_df.merge(billing_df, how='left', on='Account ID')
        s3_cost_tracker_df.rename(columns = {'Marketplacecost':'Type 4:Cloud 3rd Party License Charges $:WP_RU052', 'NetUnblendedCostWithoutVAT':'Type 4:Cloud-AWS Dedicated Account $:WP_RU061','support_cost': 'Type 4:AWS Enterprise Support  $:WP_RU063'}, inplace = True)
        s3_cost_tracker_df.to_excel("/tmp/main_billing.xlsx",index=False)
        response = s3_client.upload_file('/tmp/main_billing.xlsx', s3_bucket, main_billing_file)
        return response
    except Exception as error:
        LOGGER.info(error)
        return error
    
def create_presigned_url():
    try:
        response = s3_client.generate_presigned_url('get_object',Params={'Bucket': s3_bucket,'Key': main_billing_file},ExpiresIn=86400)    
        print(response)
        return response
    except Exception as error:
        LOGGER.info(error)
        return error    

def send_email(url):
    try:
        response = ses_client.send_email(
        Source='SITI-ECP-AWS-AT-SHELL@shell.com',
        Destination={
        'ToAddresses': [
            'vishal.ladkani@shell.com',
        ]
        },
        Message={
            'Subject': {
                'Data': main_billing_file
            },
            'Body': {
                'Text': {
                    'Data': url 
                }
            
            }
        })
        return response
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
        marketplace_query = """SELECT line_item_usage_account_id AS "Account ID", (SUM(line_item_unblended_cost)) Marketplacecost FROM {0}.{1} where  bill_payer_account_id = '{2}' and month = '{3}' and year = '{4}' and bill_billing_entity = 'AWS Marketplace' and line_item_tax_type != 'VAT' group by line_item_usage_account_id""".format(athena_database,athena_table,account_id,previous_month, previous_month_year)
        support_query = """SELECT line_item_unblended_cost FROM {0}.{1} where product_product_name='AWS Premium Support' and month= '{2}' and year= '{3}' and line_item_line_item_type = 'Fee' """.format(athena_database,athena_table,previous_month, previous_month_year)
        billing_query = """SELECT line_item_usage_account_id AS "Account ID",line_item_tax_type,SUM(CASE WHEN line_item_tax_type != 'VAT' and bill_bill_type = 'Anniversary' or (bill_bill_type = 'Purchase' and line_item_line_item_type = 'SavingsPlanUpfrontFee') THEN "line_item_net_unblended_cost" END) AS NetUnblendedCostWithoutVAT,SUM(CASE WHEN line_item_tax_type = 'VAT' and bill_bill_type = 'Anniversary' or (bill_bill_type = 'Purchase' and line_item_line_item_type = 'SavingsPlanUpfrontFee') THEN "line_item_net_unblended_cost" END) AS TotalVAT FROM {0}.{1} where bill_payer_account_id = '{2}' and month = '{3}' and year = '{4}' and bill_billing_entity = 'AWS' and line_item_legal_entity LIKE '%Amazon Web Services%' GROUP BY 1,2;""".format(athena_database,athena_table,account_id,previous_month, previous_month_year)
        billing_query_response = execute_query(billing_query,previous_month,previous_month_year)
        marketplace_query_response = execute_query(marketplace_query,previous_month,previous_month_year)
        support_query_response = execute_query(support_query,previous_month,previous_month_year)
        time.sleep(25)
        billing_file = get_csv_file_from_s3(s3_bucket,billing_query_response)
        billing_file =  billing_file[billing_file['line_item_tax_type'] != "VAT"]
        marketplace_file = get_csv_file_from_s3(s3_bucket,marketplace_query_response)
        support_file = get_csv_file_from_s3(s3_bucket,support_query_response)
        s3_cost_tracker_file = get_csv_file_from_s3(s3_bucket,cost_tracker)
        billing_df = create_dataframe_for_csv(billing_file)
        marketplace_df = create_dataframe_for_csv(marketplace_file)
        support_df = create_dataframe_for_csv(support_file)
        s3_cost_tracker_df = create_dataframe_for_csv(s3_cost_tracker_file)
        response = create_billing_excel(billing_df,marketplace_df,support_df,s3_cost_tracker_df)
        get_s3_presign_url = create_presigned_url()
        send_mail_response = send_email(get_s3_presign_url)
        return send_mail_response
    except Exception as error:
        LOGGER.info(error)
        return error