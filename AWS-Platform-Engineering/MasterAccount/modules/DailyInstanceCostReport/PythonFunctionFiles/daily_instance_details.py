import boto3
import json
import datetime
import logging
import os
import time
import csv

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Create a boto3 client for Config


class EC2DailyInstanceDetails:

    def __init__(self):
        logging.info("Initializing the class EC2DailyInstanceDetails")
        self.config_client = boto3.client('config')
        self.limit = 100


        #fetch variables from environment variables
        #ConfigurationAggregator_Name = "aws-controltower-ConfigAggregatorForOrganizations"
        self.ConfigurationAggregator_Name = os.environ['ConfigurationAggregator_Name']
        self.bucket_name = os.environ['BUCKET']
        self.s3_client = boto3.client('s3')
        self.cost_explorer_client = boto3.client('ce')



        self.short_name_to_service_name_dict = {
            "EC2": "Amazon Elastic Compute Cloud - Compute",
        }

    def get_aggregated_config_results(self, query_expression):
        try:
            response = self.config_client.select_aggregate_resource_config(
                ConfigurationAggregatorName=self.ConfigurationAggregator_Name,
                Expression=query_expression,  # Query expression
                Limit=self.limit,  # Maximum number of results to return
            )

            if response:
                results = response["Results"]
                while "NextToken" in response:
                    response = self.config_client.select_aggregate_resource_config(
                        ConfigurationAggregatorName='aws-controltower-ConfigAggregatorForOrganizations',
                        Expression=query_expression,
                        Limit=self.limit,
                        NextToken=response["NextToken"])
                    results.extend(response["Results"])

            # convert string to dictionary
            results_dict_list = []
            for each_result in results:
                each_result_dict = json.loads(each_result)
                results_dict_list.append(each_result_dict)

            return results_dict_list
        
        except Exception as e:
            logging.error(f"Error in getting aggregated results: {e}")
            return None

    def store_list_in_s3(self, data, bucket_name, prefix, file_name):
        try:
            s3 = self.s3_client

            file_name = prefix + '/' + file_name

            s3.put_object(Bucket=bucket_name, Key=file_name, Body=json.dumps(data))
            logging.info(f"Data stored in s3 with bucket_name: {bucket_name} and file_name: {file_name}")
        except Exception as e:
            logging.error(f"Error in storing data in s3: {e}")
            return None

    def get_cost_for_service(self, start_date, stop_date):
        """
        Gets UnblendedCost for the Service/linked account. In case of services like EBS where it is a usage catagory within EC2 costs,
        provides ability to have an alternate filter
        """
        short_service_name = self.short_name_to_service_name_dict["EC2"]
        logging.info(f"Getting Cost for Service {short_service_name}")
        filter = {"Dimensions": {"Key": "SERVICE", "Values": [self.short_name_to_service_name_dict["EC2"]]}}
        try:
            ce = self.cost_explorer_client
            response = ce.get_cost_and_usage_with_resources(
                TimePeriod={"Start": start_date, "End": stop_date},
                Granularity="DAILY",
                Metrics=["UnblendedCost"],
                Filter=filter,
                GroupBy=[{"Type": "DIMENSION", "Key": "RESOURCE_ID"}],
            )
            final_response = response["ResultsByTime"]

            while "NextPageToken" in response:
                response = ce.get_cost_and_usage_with_resources(
                    NextPageToken=response["NextPageToken"],
                    TimePeriod={"Start": start_date, "End": stop_date},
                    Granularity="DAILY",
                    Metrics=["UnblendedCost"],
                    Filter=filter,
                    GroupBy=[{"Type": "DIMENSION", "Key": "RESOURCE_ID"}]
                )
                final_response.extend(response["ResultsByTime"])
            return final_response
        except Exception as e:
            logging.error(f"Error in get_cost_for_service: {e}")
            raise e


    def refine_cost_dict(self, cost_dict_list):
        try:
            refined_cost_dict_list = []
            for each_dict in cost_dict_list[0]["Groups"]:
                refined_dict = {}
                if "Metrics" in each_dict:
                    if "UnblendedCost" in each_dict["Metrics"]:
                        if "Amount" in each_dict["Metrics"]["UnblendedCost"]:
                            refined_dict["DailyCost"] = each_dict["Metrics"]["UnblendedCost"]["Amount"]
                        else:
                            refined_dict["DailyCost"] = "NA"
                    else:
                        refined_dict["DailyCost"] = "NA"
                
                if "Keys" in each_dict:
                    refined_dict["resource_id"] = each_dict["Keys"][0]
                
                if "Keys" not in each_dict:
                    refined_dict["resource_id"] = "NA"
                
                if "Metrics" not in each_dict:
                    refined_dict["DailyCost"] = "NA"
                
                refined_cost_dict_list.append(refined_dict)
            return refined_cost_dict_list
        except Exception as e:
            logging.error(f"Error in refining cost dict: {e}")
            return None

    def merge_cost_and_aggregated_data(self, cost_data, aggregated_data):
        try:
            merged_data = []
            for each_cost_dict in cost_data:
                for each_aggregated_dict in aggregated_data:
                    if each_cost_dict["resource_id"] == each_aggregated_dict["resourceId"]:
                        each_aggregated_dict["DailyCost"] = each_cost_dict["DailyCost"]
                        merged_data.append(each_aggregated_dict)
                        break
                
                
            return merged_data
        except Exception as e:
            logging.error(f"Error in merging cost and aggregated data: {e}")
            return None
        
    def check_if_object_exists_in_s3(self, bucket_name, key):
        try:
            s3 = self.s3_client
            response = s3.list_objects_v2(Bucket=bucket_name, Prefix=key)
            if "Contents" in response:
                return True
            else:
                return False
        except Exception as e:
            logging.error(f"Error in checking if object exists in s3: {e}")
            return False
        
    def download_json_file_from_s3(self, bucket_name, key):
        try:
            s3 = self.s3_client
            response = s3.get_object(Bucket=bucket_name, Key=key)
            data = response['Body'].read().decode('utf-8')
            return json.loads(data)
        except Exception as e:
            logging.error(f"Error in downloading json file from s3: {e}")
            return None
        
    def upload_csv_to_s3(self, csv_file_path, bucket_name, object_name):
        try:
            s3_client = boto3.client('s3')
            s3_client.upload_file(csv_file_path, bucket_name, object_name)
        
        except Exception as e:
            logging.error(f"Error in uploading csv to s3: {e}")
            return None
    
    def flatten_dict(self, d, parent_key='', sep='_'):
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self.flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list) and k == 'tags':
                items.append((new_key, json.dumps(v)))
            else:
                items.append((new_key, v))
        return dict(items)


def lambda_handler(event, context):

    # fetch the date in dd-mm-yyyy format
    try:

        date_today = datetime.datetime.now().strftime("%d-%m-%Y")
        year = str(datetime.datetime.now().year)
        month_name = datetime.datetime.now().strftime("%B")

        EC2DailyInstanceDetails_obj = EC2DailyInstanceDetails()
        

        logging.info(f"Function called on {date_today}")


        


        # get cost of EC2 instances for the date which was 2 days ago

        # After careful analysis between the cost explorer and the cost and usage report, it was found that the cost explorer accurately displays the cost for the service for the date which was 2 days ago
        # Hence, the cost for the service for the date which was 2 days ago is fetched

        start_date_two_days_ago = (datetime.datetime.now() - datetime.timedelta(days=2)).strftime("%Y-%m-%d")
        end_date_two_days_ago = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

        day_two_days_ago = str((datetime.datetime.now() - datetime.timedelta(days=2)).strftime("%d"))

        prefix_cost_details = year + '/' + month_name + '/' + day_two_days_ago

        logging.info(f"Fetching cost details for the EC2 service for the date {start_date_two_days_ago}")
        
        cost_details = EC2DailyInstanceDetails_obj.get_cost_for_service(start_date_two_days_ago, end_date_two_days_ago)

        refined_cost_details = EC2DailyInstanceDetails_obj.refine_cost_dict(cost_details)

        # store the cost details in s3

        EC2DailyInstanceDetails_obj.store_list_in_s3(refined_cost_details, EC2DailyInstanceDetails_obj.bucket_name, prefix_cost_details, 'daily_instance_cost_details.json')


        aggregator_query = """ SELECT
            resourceId,
            accountId,
            configuration.state.name,
            configuration.instanceType,
            configuration.vpcId,
            configuration.subnetId,
            configuration.publicDnsName,
            configuration.privateIpAddress,
            configuration.privateDnsName,
            configuration.platform,
            configuration.launchTime,
            configuration.imageId,
            tags.tag,
            awsRegion,
            availabilityZone,
            resourceCreationTime
            WHERE
            resourceType = 'AWS::EC2::Instance'"""


        logging.info("Calling aggregator query to get aggregated data for instances")

        result_status_ec2_nested_list = EC2DailyInstanceDetails_obj.get_aggregated_config_results(aggregator_query)

        day_today = str(datetime.datetime.now().strftime("%d"))

        prefix_ec2_aggragator_data = year + '/' + month_name + '/' + day_today

        EC2DailyInstanceDetails_obj.store_list_in_s3(result_status_ec2_nested_list, EC2DailyInstanceDetails_obj.bucket_name, prefix_ec2_aggragator_data, 'daily_instance_aggregated_data.json')

        # check if the aggregated data exists in s3 two days ago

        key_aggregated_data = prefix_cost_details + '/daily_instance_aggregated_data.json'

        if EC2DailyInstanceDetails_obj.check_if_object_exists_in_s3(EC2DailyInstanceDetails_obj.bucket_name, key_aggregated_data):
            logging.info("Both Cost and Aggregated data exists in s3 for date : {start_date_two_days_ago}")

            # merge the cost and aggregated data

            cost_data = refined_cost_details

            # get the aggregated data from s3 object with given prefix and key

            aggregated_data = EC2DailyInstanceDetails_obj.download_json_file_from_s3(EC2DailyInstanceDetails_obj.bucket_name, key_aggregated_data)

            merged_data = EC2DailyInstanceDetails_obj.merge_cost_and_aggregated_data(cost_data, aggregated_data)

            logging.info("Merging cost and aggregated data")

            EC2DailyInstanceDetails_obj.store_list_in_s3(merged_data, EC2DailyInstanceDetails_obj.bucket_name, prefix_cost_details, 'daily_instance_merged_data.json')

            # convert merged data to csv file with the required fields

            

            # dump the merged data as csv to s3
            csv_file_path = '/tmp/daily_instance_report_data.csv'

            with open(csv_file_path, 'w', newline='') as csv_file:
                fieldnames = ['accountId', 'resourceId']  # Start with accountId and resourceId
                for item in merged_data:
                    flattened_item = EC2DailyInstanceDetails_obj.flatten_dict(item)
                    fieldnames.extend(sorted(set(flattened_item.keys()) - set(fieldnames)))
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writeheader()
                for item in merged_data:
                    flattened_item = EC2DailyInstanceDetails_obj.flatten_dict(item)
                    writer.writerow(flattened_item)

            object_name = prefix_cost_details + '/daily_instance_report_data.csv'

            EC2DailyInstanceDetails_obj.upload_csv_to_s3(csv_file_path, EC2DailyInstanceDetails_obj.bucket_name, object_name)
                    
        else:
            logging.error("Cost and Aggregated data does not exist in s3 for date : {start_date_two_days_ago}")


    
    except Exception as e:
        logging.error(f"Error in lambda_handler: {e}")
        raise e