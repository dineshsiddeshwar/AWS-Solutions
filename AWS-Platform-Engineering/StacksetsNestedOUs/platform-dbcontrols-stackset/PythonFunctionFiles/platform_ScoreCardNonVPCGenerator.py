import boto3
import csv
import io
import datetime
import json
import socket
import os
import time
import random

class PreCheckError(Exception):
    pass

class MasterUserSecretNotFoundError(Exception):
    pass

class SecretNotFoundError(Exception):
    pass

class RDSNotAvailableError(Exception):
    pass

class db_controls(object):
    def __init__(self,event,context,region,endpoint_ip):
        # LOGGER.info("in init")
        self.s3_client=boto3.client("s3")
        self.rds_client = boto3.client('rds', region_name = region)
        self.lambda_client = boto3.client('lambda', region_name = region)
        self.s3_resource = boto3.resource('s3')
        self.secretsmanager_client = boto3.client('secretsmanager', region_name = region)
        self.session = boto3.session.Session()
        self.ssm_client = self.session.client('ssm', region_name = region)
        
        self.region = region
        self.endpoint_ip = endpoint_ip

    def prechecks(self,event,rds_instance_name,region):
        
        db_instance = self.get_db_boto_object(rds_instance_name)
        
        isRDSAvailable = self.check_rds_status(db_instance)
        
        # try:
        #     username, password = self.get_username_and_password(db_instance)
        #     canGetUsernameAndPassword = True
        # except Exception as e:
        #     raise e
        
        if isRDSAvailable is False:
            raise RDSNotAvailableError(f"{rds_instance_name} is not Available.")

        
        if isRDSAvailable:
            
            return self.main(event,db_instance,region)
            
    def run_control_plane_checks(self, db_instance):
        check_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        check = []
        try:
            clusterCheckName = "AWSSecHub.RDS.8 Ensure Deletion Protection is Enabled. For clustered instances this check is performed at the cluster level"
            if self.is_database_part_of_cluster(db_instance):
                if self.is_delete_protection_enabled_for_cluster(db_instance):
                    check_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    check.append((check_timestamp,clusterCheckName,"Pass",""))
                else:
                    check.append((check_timestamp,clusterCheckName,"Fail","False"))
            else:
                if 'DeletionProtection' in db_instance:
                    check.append((check_timestamp,clusterCheckName,"Pass",""))
                else:
                    check.append((check_timestamp,clusterCheckName,"Fail","False"))

        except Exception as e:
            check.append((check_timestamp,clusterCheckName,"Fail",str(e)))

        try:
            copyTagsCheckName = "AWSSecHub.RDS.17 Ensure Copy Tags to Snapshot is Enabled"
            if self.is_copy_tags_enabled(db_instance):
                check.append((check_timestamp,copyTagsCheckName,"Pass",""))
            else:
                check.append((check_timestamp,copyTagsCheckName,"Fail","False"))
        except Exception as e:
            check.append((check_timestamp,copyTagsCheckName,"Fail",str(e)))

        try:
            autoMinorCheckName = "AWSSecHub.RDS.13 Ensure Auto Minor Version is Enabled"
            if self.is_auto_minor_version_enabled(db_instance):
                check.append((check_timestamp,autoMinorCheckName,"Pass",""))
            else:
                check.append((check_timestamp,autoMinorCheckName,"Fail","False"))
        except Exception as e:
            check.append((check_timestamp,autoMinorCheckName,"Fail",str(e)))


        return check
    
    def is_copy_tags_enabled(self,db_instance):
        return db_instance['CopyTagsToSnapshot']

    def is_auto_minor_version_enabled(self,db_instance):
        return db_instance['AutoMinorVersionUpgrade']
    
    def is_database_part_of_cluster(self,db_instance):
        
        # Check if the DB instance is part of a cluster
        if 'DBClusterIdentifier' in db_instance:
            # If the DB instance is part of a cluster, get the cluster identifier
            return True
        else:
            return False

    def is_delete_protection_enabled_for_cluster(self,db_instance):

        db_name = db_instance['DBInstanceIdentifier']

        # Initialize the RDS client
        rds_client = boto3.client('rds')
        # Check if the DB instance is part of a cluster
        response = rds_client.describe_db_instances(DBInstanceIdentifier=db_name)
        if 'DBClusterIdentifier' in response['DBInstances'][0]:
            # If the DB instance is part of a cluster, get the cluster identifier
            db_cluster_identifier = response['DBInstances'][0]['DBClusterIdentifier']
            # Check if delete protection is enabled for the cluster
            # response = rds_client.describe_db_clusters(DBClusterIdentifier=db_cluster_identifier)
            response = (self.rds_client.get_paginator('describe_db_clusters').paginate(DBClusterIdentifier=db_cluster_identifier).build_full_result())

            if response['DBClusters'][0]['DeletionProtection']:
                return True
            else:
                return False
        else:
            raise PreCheckError(f"The DB instance {db_name} is not part of a cluster")

    def main(self,event,db_instance,region):
        
        # Create an S3 client
        # Read the file from the S3 bucket
        bucket_name = os.environ['QUERY_BUCKET_NAME']
        file_names = self.get_data_plane_checks_filenames(db_instance)
        
        print(file_names)
        
        #Get username and password
        # username, password = self.get_username_and_password(db_instance)
        # Create a CSV buffer to store the results
        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer)
        # writer.writerow(["Timestamp","Check Name", "Compliance Status", "Actual Value"])
        writer.writerow(["Timestamp","Db Name","Account","Region","Engine","Engine Version","Check Name","Compliance Status", "Actual Value"])
        
        db_name = db_instance["DBInstanceIdentifier"]
        db_engine = db_instance["Engine"]
        db_engine_version = db_instance["EngineVersion"]
        rds_db_name = "None"
        if 'DBName' in db_instance:
            rds_db_name = db_instance['DBName']

        (db_endpoint, db_port) = self.get_db_endpoint(db_instance)
        
        secret_arn = self.get_secret_arn(db_instance)
        
        accountID = self.getAccountId(region)
        
    
        # Iterate over the checks
        num_checks = 0
        num_passed_checks = 0
        
        # Control Plane
        control_plane_checks = self.run_control_plane_checks(db_instance)
        num_checks += len(control_plane_checks)


        for cp_check in control_plane_checks:
            check_timestamp,check_name,status,result = cp_check

            if status == "Pass":
                num_passed_checks += 1

            # writer.writerow([check_timestamp,check_name, status, result])
            writer.writerow([check_timestamp,db_name,accountID,region,db_engine,db_engine_version,check_name, status, result])

                
        for file_name in file_names:
            print(file_name)
            response = self.s3_client.get_object(Bucket=bucket_name, Key=f'rds-json-files/{file_name}')
            content = response["Body"].read().decode("utf-8")
            # Parse the JSON content
            data = json.loads(content)
            
            # for dd in data:
            #     print(dd)
            # # print(data)
            
            inputPayload = {
                "rds_db_name": rds_db_name,
                "invocationType": "execute_checks",
                "endpoint_ip":self.endpoint_ip,
                "rds_instance_name":db_name,
                "rds_endpoint": db_endpoint,
                "rds_port": db_port,
                "rds_engine": db_engine,
                "db_engine_version":db_engine_version,
                "checks": data,
                "secret_arn" :secret_arn,
                "account_id": accountID,
                "region": region
            }
            
            functionName = os.environ['FUNCTION_NAME']
            
            response = self.lambda_client.invoke(
                FunctionName=functionName,
                Payload=json.dumps(inputPayload)
            )
        
            responsePayload = response['Payload'].read()
            response_arr = json.loads(responsePayload)
            print("retrusning")
            print(response_arr)
        
            if 'errorMessage' in response_arr:
                raise Exception(response_arr['errorMessage'])
            
            for row in response_arr["results"]:
                writer.writerow(row)


            # #Data Plane
            # num_checks += len(data)
            # for check_data in data:
            #     check_name = check_data["checkname"]
            #     check_type = check_data.get("check_type", "all")
            #     query = check_data["query"]
            #     checks = check_data["checks"]
            
            #     try:
            #         # Execute the SQL query and fetch the results
            #         with conn.cursor() as cur:
            #             cur.execute(query)
            #             fetched_result = cur.fetchone()
            #             if fetched_result is None:
            #                 result = fetched_result
            #             else:
            #                 result = fetched_result[0]
            #     # Check the expected output values against the actual result
            #         if check_type == "all":
            #             if self.all_checks_pass(checks, result):
            #                 status = "Pass"
            #                 num_passed_checks += 1
            #             else:
            #                 status = "Fail"
            #         elif check_type == "any":
            #             if self.any_checks_pass(checks, result):
            #                 status = "Pass"
            #                 num_passed_checks += 1
            #             else:
            #                 status = "Fail"
            #         else:
            #             raise ValueError("Invalid check type: " + check_type)
            #         # Write the results to the CSV buffer
            #         check_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
            #         if status == "Pass":
            #             result = ''
                
            #         # writer.writerow([check_timestamp,check_name, status, result])
            #         writer.writerow([check_timestamp,db_name,accountID,region,db_engine,db_engine_version,check_name, status, result])

            #     except Exception as e:
            #         conn = self.connect_to_db(db_instance,username,password)
            #         writer.writerow([check_timestamp,db_name,accountID,region,db_engine,db_engine_version,check_name, "Error", str(e).strip('\n')])

            
    
    
            # Write the summary to the CSV buffer
            num_passed_checks = num_passed_checks + response_arr['num_passed_checks']
            num_checks = num_checks + response_arr['num_checks']
        

        
        
        
        writer.writerow(["Checks Passed", "Total Checks", "Score"])
        score = round((num_passed_checks / num_checks) * 100)
        writer.writerow([num_passed_checks, num_checks, f'{score}%'])
        # score = 0
        self.uploadCSV(event,csv_buffer,db_instance,"Pass"," ",score,region)
        
        return {
            'message' : f"Success"
        }
    def email_success_func(self,event,output_file_name):
        session_client = boto3.session.Session()
        sts_client = session_client.client('sts')
        account_number = sts_client.get_caller_identity()['Account']
        ssm_prmtr_client=boto3.client('ssm',region_name='us-east-1')
        response = ssm_prmtr_client.get_parameter(Name='/Platform-Tag/platform_Custodian')
        custodian=response['Parameter']['Value']
        platform_dl = ssm_prmtr_client.get_parameter(Name='/Platform-Tag/platform_DL')
        platform_dl_response = platform_dl['Parameter']['Value']
        mail_body_value=""
        DNSSESKeyEmail = self.ssm_client.get_parameter(Name='/platform-dns/DNSSESKeyEmail')
        DNSSESKeyEmail = DNSSESKeyEmail['Parameter']['Value']
        DNSSESSecrtEmail = self.ssm_client.get_parameter(Name='/platform-dns/DNSSESSecrtEmail')
        DNSSESSecrtEmail = DNSSESSecrtEmail['Parameter']['Value']
        platform_dl = self.ssm_client.get_parameter(Name='/Platform-Tag/platform_DL')
        platform_dl_response = platform_dl['Parameter']['Value']
        session_client = boto3.session.Session()
        try:
            ses_client = session_client.client('ses', region_name='us-east-1', aws_access_key_id=DNSSESKeyEmail, aws_secret_access_key=DNSSESSecrtEmail)
        except Exception as exception:
            print(exception)
        str_value=""   
        rds_instance_name=event["instance_name"]
        region=event["region"]
        str_value=str_value+rds_instance_name+" in the region "+region
        mail_body_value=str_value
        #file_link="https://eu001-sp.shell.com/:x:/r/sites/AAFAA3444/DBS/OLM%20Scorecard/AWS@Shell_RDS_DB_Scorecards/"+output_file_name
        file_link="https://eu001-sp.shell.com/:x:/r/sites/AAFAA3444/DBS/AWS%20Shell%20RDS%20Scorecards/"+output_file_name
        remidiation_link = "https://eu001-sp.shell.com/:w:/r/sites/AAFAA5187/L3/IB-Cloud%20CoE/AWS%20DA%202.0/QRGs/RDS%20QRGs/Control%20and%20Data%20Plane%20Remediation%20Steps.docx?d=wa633323023884ad28b2aa79d4773abe8&csf=1&web=1&e=VIefhz"
        mail_body="""Hello,
            The DB Controls Compliance Automation has run successfully for"""+mail_body_value+"""\nPlease refer to following the SharePoint link to get your scorecard: """+"""\nRegards,\nCloud Services Team"""
        mail_subject= "DB Compliance Scorecard is ready for review for account "+account_number
        body_html = """<html>
                <head>
                </head>
                <body>
                <p style="font-family:'Futura Medium'">Hello Team,</p>
                <p style="font-family:'Futura Medium'"> The DB Controls Compliance Automation has run successfully for</p>
                <p style="font-family:'Futura Medium'"><strong>"""+mail_body_value+"""</strong></p>
                <p style="font-family:'Futura Medium'">Please review the scorecard and take proper remediation actions for checks that have a Compliance Status of FAIL.</p>
                <p style="font-family:'Futura Medium'">Scorecard Link:</p>
                <href>"""+file_link+"""</href>
                <p>For any remidiation steps, please refer the below ORG</p>
                <href>"""+remidiation_link+"""</href>
                <p>For any access issues, please contact –'SITI ET SOM Database Engineering SITI-ITV/EF'</p>
                <href>SITI-ET-SOM-Database-Engineering@shell.com</href>
                <p style="font-family:'Futura Medium'">Best Regards,</p>
                <p style="font-family:'Futura Medium'">AWS@Shell Team</p>
                
                </body>
                </html>
                """
        try:
            # LOGGER.info("Inside custom Send Mail")
            char_set = "utf-8"
         
            response = ses_client.send_email(
                Destination={
                    "ToAddresses": [
                            custodian,
                            ],
                        },
                Message={
                        "Subject": {
                            "Data": mail_subject,
                                    },
                        "Body": {
                            "Text": {
                                "Data": mail_body,
                            },
                            "Html":{
                                "Data":body_html
                            }
                                },
                               },
                Source="SITI-CLOUD-SERVICES@shell.com",
                        )
            # LOGGER.info("Email sent!")
        except Exception as exception:
            # LOGGER.error("Lambda failed with the error:'{0}'".format(exception))
            return "FAILED" 
            
    def getAccountId(self,region):
        sts_client = boto3.client('sts',region_name=region,endpoint_url=f"https://sts.{region}.amazonaws.com")
        response = sts_client.get_caller_identity()
        account_id = response['Account']
        return account_id
    
    def uploadCSV(self,event,csv_buffer,db_instance,status,result,score,region):
        # S3 bucket and key
        bucket_name = os.environ['SCORECARD_BUCKET_NAME']
        
        # Create S3 resource
        #s3 = boto3.resource('s3')
        # Get current year and month
        current_year = datetime.datetime.now().strftime('%Y')
        current_month = datetime.datetime.now().strftime('%m')
    
        # Create folder path in S3
        folder_path = f'{current_year}-{current_month}/'
    
        # Check if folder exists, and create it if it doesn't
        self.s3_resource.Bucket(bucket_name).put_object(Key=(folder_path))

        # Upload the CSV buffer to the S3 bucket
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        db_engine = db_instance["Engine"]
        db_name = db_instance["DBInstanceIdentifier"]
        account_id = self.getAccountId(region)
        current_region = region
        output_file_name = f"{account_id}_{db_name}_{current_region}_{db_engine}_RDS_{timestamp}.csv"

        self.s3_resource.Object(bucket_name, folder_path + output_file_name).put(Body=csv_buffer.getvalue())
    
        db_name = db_instance["DBInstanceIdentifier"]

    
        s3URI = f's3://{bucket_name}/{folder_path}{output_file_name}'
        
        self.email_success_func(event,output_file_name)
    
        self.write_to_dynamodb(db_name,db_engine,status,result,region,s3URI = s3URI,score=score)
    
    def any_checks_pass(self,checks, result):
        """
        Returns True if any of the checks pass, False otherwise.
        Args:
        checks (list[dict]): A list of dictionaries representing the checks to be performed.
        result: The result of the operation being checked.
        Returns:
        True if any of the checks pass, False otherwise.
        """
        for check in checks:
            expected_value_type = check.get("value_type")
            operand = check.get("operator")
            expected_output = check.get("value")
            if operand != "isnone" and operand != "notnone":
                expected_output = self.convert_to_primitive(expected_value_type, expected_output)
                result = self.convert_to_primitive(expected_value_type, result)
            try:
                if self.check_values(
                    operand,
                    expected_output,
                    result,
                ):
                    return True
            except ValueError as e:
                pass
        return False
    
    def all_checks_pass(self,checks, result):
        """
        Returns True if all of the checks pass, False otherwise.
        Args:
        checks (list[dict]): A list of dictionaries representing the checks to be performed.
        result: The result of the operation being checked.
        Returns:
        True if all of the checks pass, False otherwise.
        """
        for check in checks:
            expected_value_type = check.get("value_type")
            operand = check.get("operator")
            expected_output = check.get("value")
            if operand != "isnone" and operand != "notnone":
                expected_output = self.convert_to_primitive(expected_value_type, expected_output)
                result = self.convert_to_primitive(expected_value_type, result)
            if not self.check_values(
                operand,
                expected_output,
                result,
            ):
                return False
        return True
    
    def convert_to_primitive(self,type_str, value):
        """
        Converts the given value to the specified primitive type.
        Args:
        type_str (str): A string representing a primitive type.
        value: The value to be converted to the primitive type.
        Returns:
        The value converted to the specified primitive type.
        """
        # Convert the value to the specified primitive type
        type_str = type_str.lower()
        if type_str == "int":
            return int(value)
        elif type_str == "float":
            return float(value)
        elif type_str == "bool":
            if value.lower() == "true":
                return True
            elif value.lower() == "false":
                return False
            else:
                raise ValueError("Invalid boolean value: " + value)
        elif type_str == "str":
            return str(value)
        else:
            raise ValueError("Invalid primitive type: " + type_str)
        
    def check_values(self,operand, expected, actual):
        if operand == "==":
            return actual == expected
        elif operand == "!=":
            return actual != expected
        elif operand == ">":
            return float(actual) > float(expected)
        elif operand == "<":
            return float(actual) < float(expected)
        elif operand == ">=":
            return float(actual) >= float(expected)
        elif operand == "<=":
            return float(actual) <= float(expected)
        elif operand == "startswith":
            return actual.startswith(expected)
        elif operand == "notnone":
            return actual is not None
        elif operand == "isnone":
            return actual is None
        elif operand == "contains":
            return expected in actual
        else:
            raise ValueError("No operand matched")
    
    def get_db_boto_object(self,rds_db_name):
        response = self.rds_client.describe_db_instances()
        for db_instance in response['DBInstances']:
            if db_instance['DBInstanceIdentifier'] == rds_db_name:
                return db_instance
        raise Exception(f"Database '{rds_db_name}' not found.")
        
    def check_rds_status(self,db_instance):
        db_instance_status = db_instance['DBInstanceStatus']
        if db_instance_status == 'available':
            return True
        else:
            db_name = db_instance['DBInstanceIdentifier']
            raise Exception(f"{db_name} current status is {db_instance_status}. {db_name} must be available to continue. Try again once available.")
    
    def get_secret_arn(self,db_instance):
        db_engine = db_instance['Engine']
        
        if db_engine.startswith('oracle') and db_engine.endswith('cdb'):
            db_name = db_instance['DBInstanceIdentifier']
            
            filter = [{'Key': 'name', 'Values': [f'MASTER_USER_SECRET_{db_name}']}]
            results = []
            response = self.secretsmanager_client.list_secrets(Filters=filter)
            results += response['SecretList']
            while 'NextToken' in response:
                response = self.secretsmanager_client.list_secrets(Filters=filter, NextToken=response['NextToken'])
                results += response['SecretList']

            for secret in results:
                if secret['Name'] == f'MASTER_USER_SECRET_{db_name}':
                    return secret['ARN']
            raise SecretNotFoundError(f'No secret found in secrets manager for db {db_name} - {db_engine}')

        else:
            try:
                if self.is_database_part_of_cluster(db_instance):
                    db_cluster_identifier = db_instance['DBClusterIdentifier']
                    response = (self.rds_client.get_paginator('describe_db_clusters').paginate(DBClusterIdentifier=db_cluster_identifier).build_full_result())

                    if response['DBClusters'][0]['MasterUserSecret']:
                        secret = response['DBClusters'][0]['MasterUserSecret']
                    else:
                        raise MasterUserSecretNotFoundError(f'Master user secret not found in cluster.')
                else:
                    secret = db_instance['MasterUserSecret']
            except KeyError as e :
                raise MasterUserSecretNotFoundError(f'Master user secret not found')
                
            # master_username = db_instance['MasterUsername']
            return secret['SecretArn']
            # master_user_password = secret_value['password']
            # return master_username, master_user_password
        raise ValueError("Unsupported engine type: {}. No platform level compliance check available, please perform self-assessment of database security against best practices".format(db_engine))
    
    def decrypt_secret(self,secret_arn):
        session = boto3.session.Session()
        client = session.client(service_name='secretsmanager')
        get_secret_value_response = client.get_secret_value(SecretId=secret_arn)
        if 'SecretString' in get_secret_value_response:
            return json.loads(get_secret_value_response['SecretString'])
            
        raise ValueError(f"Error getting secret value for {secret_arn}: {e}")
    
    # def check_rds_connection(self,db_instance):
    #     endpoint = db_instance['Endpoint']['Address']
    #     port = db_instance['Endpoint']['Port']
    #     # Check whether a Lambda function can ping the RDS instance using the socket module
    #     try:
    #         s = socket.create_connection((endpoint, port), timeout=3)
    #         return True
    #     except socket.error:
    #         raise PreCheckError(f'Could not connect to RDS instance {db_instance["DBInstanceIdentifier"]} via Socket, The lambda is likely not in the same vpc as the RDS instance.')
        
    def get_db_endpoint(self,db_instance):
        endpoint = db_instance['Endpoint']['Address']
        port = db_instance['Endpoint']['Port']
        return endpoint, port
    
    def get_data_plane_checks_filenames(self,db_instance):
        engine_type = db_instance['Engine']
        print(engine_type)
        res = []
        if 'oracle' in engine_type.lower():
            res.append('oracle_data_plane_checks.json')
        elif 'mysql' in engine_type.lower():
            res.append('mysql_common_data_plane_checks.json')
            if 'mysql' == engine_type.lower():
                #This is an RDS MYSQL
                res.append('mysql_rds_data_plane_checks.json')
        elif 'sqlserver' in engine_type.lower():
            res.append('sqlserver_data_plane_checks.json')
        elif 'postgres' in engine_type.lower():
            res.append('postgres_data_plane_checks.json')
        else:
            raise ValueError("Unsupported engine type: {}. No platform level compliance check available, please perform self-assessment of database security against best practices".format(engine_type))
            
        return res

    def write_to_dynamodb(self,db_name,db_engine,status,failure_reason,region,s3URI = None, score = None):
        session_client = boto3.Session()
        sts_client = session_client.client('sts')
        account_number=os.environ['ACCOUNT_ID']
        secondaryRoleArn = "arn:aws:iam::{}:role/platform_dynamodb_dbcontrols".format(account_number)
        secondarySessionName = "SecondarySession-" + str(random.randint(1, 100000))
        # Logging to child account.
        # LOGGER.info("Logging to Child Account")
        secondaryRoleCreds = sts_client.assume_role(RoleArn=secondaryRoleArn,
                                        RoleSessionName=secondarySessionName)
        credentials = secondaryRoleCreds.get('Credentials')
        accessKeyID = credentials.get('AccessKeyId')
        secretAccessKey = credentials.get('SecretAccessKey')
        sessionToken = credentials.get('SessionToken')
        assumeRoleSession = boto3.session.Session(accessKeyID, secretAccessKey, sessionToken)
        dynamodb_client = assumeRoleSession.client('dynamodb',region_name='us-east-1')
        #dynamodb_client = boto3.client('dynamodb',region_name='us-east-1')
        table_name = os.environ['DYNAMODB_NAME']
        #dynamodb_client = boto3.client('dynamodb',region_name='us-east-1')
        #table_name = 'ComplianceRuns'
        datestr = datetime.datetime.now().strftime("%Y-%m-%d")
        timestr = datetime.datetime.now().strftime("%H:%M:%S")

        unix = time.time() * 1000
        unix = int(unix)
        account = self.getAccountId(region)
        region = region  
    
        item={
            'unix_timestamp': {'N': str(unix)},
            'date': {'S' : datestr},
            'time': {'S' : timestr},
            'account': {'S' : account},
            'region' : {'S' : region},
            'db_name' : {'S' :db_name},
            'db_engine' : {'S' : db_engine},
            'status' : {'S' : status},
            'failure_reason' : {'S': failure_reason}          
        } 
    
        if s3URI is not None:
            item['s3URI'] = {'S': s3URI}
            
        if score is not None:
            item['score'] = {'N': str(score)}
    
        dynamodb_client.put_item(
            TableName=table_name,
            Item=item
            )
        print("write_to_dynamodb")

    def run_test_query(self,db_name,username,password):
        # check if connection is successful
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT 1 FROM DUAL')
            cursor.close()
            return True
        except:
            raise Exception("Could not connect to the database.")
        return False
        
    def email_func(self,str_value, rds_instance_name, region):
        session_client = boto3.session.Session()
        sts_client = session_client.client('sts')
        account_number = sts_client.get_caller_identity()['Account']
        ssm_prmtr_client=boto3.client('ssm',region_name='us-east-1')
        response = ssm_prmtr_client.get_parameter(Name='/Platform-Tag/platform_Custodian')
        custodian=response['Parameter']['Value']
        platform_dl = ssm_prmtr_client.get_parameter(Name='/Platform-Tag/platform_DL')
        platform_dl_response = platform_dl['Parameter']['Value']
        mail_body_value=str_value
        DNSSESKeyEmail = self.ssm_client.get_parameter(Name='/platform-dns/DNSSESKeyEmail')
        DNSSESKeyEmail = DNSSESKeyEmail['Parameter']['Value']
        DNSSESSecrtEmail = self.ssm_client.get_parameter(Name='/platform-dns/DNSSESSecrtEmail')
        DNSSESSecrtEmail = DNSSESSecrtEmail['Parameter']['Value']
        platform_dl = self.ssm_client.get_parameter(Name='/Platform-Tag/platform_DL')
        platform_dl_response = platform_dl['Parameter']['Value']
        session_client = boto3.session.Session()
        try:
            ses_client = session_client.client('ses', region_name='us-east-1', aws_access_key_id=DNSSESKeyEmail, aws_secret_access_key=DNSSESSecrtEmail)
        except Exception as exception:
            print(exception)
            
        str_value=str_value+" for "+rds_instance_name+" in the region "+region
        mail_body_value=str_value
        mail_body="""Hello,
            We could identify that the following issue has occured while triggering the DB compliance lambda. Please take necessary actions for it: +"""+mail_body_value+"""\nPlease refer to the RDS QRG for remediation instructions: """+"""\nRegards,\nCloud Services Team"""
        mail_subject= "DB Compliance pre-checks failed for the following account number: "+account_number
        body_html = """<html>
                <head>
                </head>
                <body>
                <p style="font-family:'Futura Medium'">Hello Team,</p>
                <p style="font-family:'Futura Medium'"> We could identify that the following issue has occured while triggering the DB compliance lambda. Please take necessary actions for it:</p>
                <p style="font-family:'Futura Medium'"><strong>"""+mail_body_value+"""</strong></p>
                <p style="font-family:'Futura Medium'">Please refer to the RDS QRG for remediation instructions:</p>
                <href>https://eu001-sp.shell.com/:w:/r/sites/AAFAA5187/L3/IB-Cloud%20CoE/AWS%20DA%202.0/QRGs/RDS%20QRGs/Master%20RDS%20QRG.docx?d=w07488d700ebc4b059ed4fa966eb52577&csf=1&web=1&e=D9tFnZ</href>
                <p style="font-family:'Futura Medium'">Best Regards,</p>
                <p style="font-family:'Futura Medium'">AWS@Shell Team</p>
                
                </body>
                </html>
                """
        try:
            # LOGGER.info("Inside custom Send Mail")
            char_set = "utf-8"
            #LOGGER.info("Hello\r\nWe could see the below instances are not having SSM agent installed and this would make the instances SSM non-compliant in our platform. Request you to install the SSM agent ASAP and  update us. \r\nAccount Number:" +self.account_number+mail_body+"\r\nRegards,\r\nCloud Services Team")
            response = ses_client.send_email(
                Destination={
                    "ToAddresses": [
                            custodian,
                            ],
                        },
                Message={
                        "Subject": {
                            "Data": mail_subject,
                                    },
                        "Body": {
                            "Text": {
                                "Data": mail_body,
                            },
                            "Html":{
                                "Data":body_html
                            }
                                },
                               },
                Source="SITI-CLOUD-SERVICES@shell.com",
                        )
            # LOGGER.info("Email sent!")
        except Exception as exception:
            # LOGGER.error("Lambda failed with the error:'{0}'".format(exception))
            return "FAILED" 
    
def lambda_handler(event, context):
    rds_instance_name = event["instance_name"]
    region = event["region"]
    endpoint_ip = event["endpoint_ip"]
    db_engine = ""
    # try:
    obj=db_controls(event,context,region,endpoint_ip)
    str_value = "Test Pass"
    # obj.email_func(str_value, rds_instance_name, region)

    # db_engine = obj.getEngineFromName(rds_instance_name)
    return obj.prechecks(event,rds_instance_name,region)
    # except Exception as e:
        
    #     try:
            
    #         #Write error to dynamo
    #         db_engine = boto3.client('rds').describe_db_instances(DBInstanceIdentifier=rds_instance_name)['DBInstances'][0]['Engine']
    #         obj.write_to_dynamodb(rds_instance_name,db_engine,"Fail",str(e),region)
    #         str_value=str(e)
    #         # obj.email_func(str_value, rds_instance_name, region)
    #     except Exception as f:
    #         #Problem writing to dynamo
    #         raise f
    #     #Raise original error
    #     raise e