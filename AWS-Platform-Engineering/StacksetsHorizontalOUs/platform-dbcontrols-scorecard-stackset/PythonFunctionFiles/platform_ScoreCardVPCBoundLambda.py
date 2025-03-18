import json
import socket
import boto3
import psycopg2
import oracledb
import pymysql
import pymssql
import datetime
import os
import random
import time
import datetime

def lambda_handler(event, context):
    # TODO implement
    invocationType = event['invocationType']
    
    if invocationType == "precheck_sockets":
        connectable = []
        unreachable = []
        
        rds_list = event['rds_list']
        # rds_info = rds_list
        for rds_info in rds_list:
        # instance_name = rds_info[0]
        # endpoint = rds_info[1]
        # port = rds_info[2]
            (instance_name, endpoint, port) = rds_info
            try:
                check_rds_socket_connection(endpoint,port)
                connectable.append(instance_name)
            except socket.error:
                unreachable.append(instance_name)
                
            
    
        return {
            "reachable" : connectable,
            "unreachable" : unreachable
        }
    elif invocationType == "execute_checks":
        rds_db_name = event["rds_db_name"]
        endpoint_ip = event["endpoint_ip"]
        rds_instance_name = event["rds_instance_name"]
        secretARN = event["secret_arn"]
        rds_endpoint = event["rds_endpoint"]
        rds_port = event["rds_port"]
        rds_engine = event["rds_engine"]
        db_engine_version = event["db_engine_version"]
        checks = event["checks"]
        account_id = event["account_id"]
        region = event["region"]


        
        if endpoint_ip == "None":
            secretsmanager_client = boto3.client('secretsmanager', region_name=region)
        else:
            secretsmanager_client = boto3.client('secretsmanager', region_name=region,endpoint_url = f"https://{endpoint_ip}")

        secret_value = secretsmanager_client.get_secret_value(SecretId=secretARN)
        print(secret_value)
        # return json.dumps(secret_value["SecretString"],default=str)
        # return json.loads(secret_value["SecretString"])
        jsonSecret = json.loads(secret_value["SecretString"])
        username = jsonSecret["username"]
        password = jsonSecret["password"]
        
        
        # return password

        
        return run_checks(checks,rds_instance_name,rds_engine,db_engine_version,rds_endpoint,rds_port,rds_db_name,username,password,account_id,region)
        #return run_checks(checks,rds_instance_name,rds_engine,db_engine_version,rds_endpoint,rds_port,username,password,account_id,region)



        
        
        # secret_value = secretsmanager_client.get_secret_value(SecretId="arn:aws:secretsmanager:us-east-1:526353399916:secret:rds!cluster-c4bf2147-fc3d-4507-aed6-5c35114fdd68-aFnqat")
        # print(secret_value)
    elif invocationType == "check_sm_connectivity":
        # Create a Boto3 client for AWS Secrets Manager with a timeout
        secrets_manager_client = boto3.client('secretsmanager', config=Config(connect_timeout=2, read_timeout=2, retries={'max_attempts': 0}))
        # check connection to Secrets Manager
        try:
            # Make a request to Secrets Manager to check the connection
            secrets_manager_client.list_secrets()
            print("Connection to Secrets Manager successful!")
            return {"secretsmanager_public_api_reachable":"True"}
        except Exception as e:
            print("An error occurred:", str(e))
            return {"secretsmanager_public_api_reachable":"False"}

def run_checks(checks,rds_instance_name,db_engine,db_engine_version,rds_endpoint,rds_port,rds_db_name,username,password,account_id,region):
#def run_checks(checks,rds_instance_name,db_engine,db_engine_version,rds_endpoint,rds_port,username,password,account_id,region):
    conn = connect_to_db(rds_instance_name,db_engine,rds_endpoint,rds_port,rds_db_name,username,password)
    #conn = connect_to_db(rds_instance_name,db_engine,rds_endpoint,rds_port,username,password)
    res = []
    num_checks = 0
    num_passed_checks = 0
    num_checks += len(checks)

    for check_data in checks:
        check_name = check_data["checkname"]
        check_type = check_data.get("check_type", "all")
        query = check_data["query"]
        checks = check_data["checks"]
        check_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            # Execute the SQL query and fetch the results
            with conn.cursor() as cur:
                cur.execute(query)
                fetched_result = cur.fetchone()
                if fetched_result is None:
                    result = fetched_result
                else:
                    result = fetched_result[0]
        # Check the expected output values against the actual result
            if check_type == "all":
                if all_checks_pass(checks, result):
                    status = "Pass"
                    num_passed_checks += 1
                else:
                    status = "Fail"
            elif check_type == "any":
                if any_checks_pass(checks, result):
                    status = "Pass"
                    num_passed_checks += 1
                else:
                    status = "Fail"
            else:
                raise ValueError("Invalid check type: " + check_type)
            # Write the results to the CSV buffer
        
            if status == "Pass":
                result = ''
        
            res.append([check_timestamp,rds_instance_name,account_id,region,db_engine,db_engine_version,check_name, status, result])

        except Exception as e:
            conn = connect_to_db(rds_instance_name,db_engine,rds_endpoint,rds_port,rds_db_name,username,password)
            res.append([check_timestamp,rds_instance_name,account_id,region,db_engine,db_engine_version,check_name, "Error", str(e).strip('\n')])
            
    return {
        "results":res,
        "num_checks":num_checks,
        "num_passed_checks":num_passed_checks
    }

# def get_username_and_password(db_instance):
#     db_engine = db_instance['Engine']
    
#     if db_engine.startswith('oracle') and db_engine.endswith('cdb'):
#         db_name = db_instance['DBInstanceIdentifier']
        
#         filter = [{'Key': 'name', 'Values': [f'MASTER_USER_SECRET_{db_name}']}]
#         results = []
#         response = secretsmanager_client.list_secrets(Filters=filter)
#         results += response['SecretList']
#         while 'NextToken' in response:
#             response = client.list_secrets(Filters=filter, NextToken=response['NextToken'])
#             results += response['SecretList']
        
        
#         # secrets_list = secretsmanager_client.list_secrets(Filters=[
#         #     {
#         #         'Key': 'name',
#         #         'Values': [f"MASTER_USER_SECRET_{db_name}"]
#         #     },
#         # ])['SecretList']

#         for secret in results:
#             print(secret)
#             if secret['Name'] == f'MASTER_USER_SECRET_{db_name}':
#                 print(secret['Name'])
#                 secret_value = decrypt_secret(secret['ARN'])
#                 username = secret_value['username']
#                 password = secret_value['password']
#                 return username, password
                
#         raise SecretNotFoundError(f'No secret found in secrets manager for db {db_name} - {db_engine}')
    
#     else:
        
#         try:
#             if is_database_part_of_cluster(db_instance):
                
#                 db_cluster_identifier = db_instance['DBClusterIdentifier']
#                 # response = rds_client.describe_db_clusters(DBClusterIdentifier=db_cluster_identifier)
#                 response = (rds_client.get_paginator('describe_db_clusters').paginate(DBClusterIdentifier=db_cluster_identifier).build_full_result())

#                 if response['DBClusters'][0]['MasterUserSecret']:
#                     secret = response['DBClusters'][0]['MasterUserSecret']
#                 else:
#                     raise MasterUserSecretNotFoundError(f'Master user secret not found in cluster.')
#             else:
                
#                 secret = db_instance['MasterUserSecret']
#         except KeyError as e :
            
#             raise MasterUserSecretNotFoundError(f'Master user secret not found')
            
#         master_username = db_instance['MasterUsername']
#         secret_value = decrypt_secret(secret['SecretArn'])
#         master_user_password = secret_value['password']
#         return master_username, master_user_password
#     raise ValueError("Unsupported engine type: {}".format(db_engine))

def check_rds_socket_connection(endpoint,port):
    # Check whether a Lambda function can ping the RDS instance using the socket module
        s = socket.create_connection((endpoint, port), timeout=10)
        return True
    # except socket.error:
    #     raise PreCheckError(f'Could not connect to RDS instance {db_instance["DBInstanceIdentifier"]} via Socket, The lambda is likely not in the same vpc as the RDS instance.')
def connect_to_db(db_name,engine_type,endpoint,port,rds_db_name,username,password):
#def connect_to_db(db_name,engine_type,endpoint,port,username,password):
    # engine_type = db_instance['Engine']
    # db_name = db_instance['DBInstanceIdentifier']
    # endpoint,port = get_db_endpoint(db_instance)
    if 'oracle' in engine_type.lower():
        # dsn_tns = oracledb.makedsn(endpoint, port, service_name='ORCL')
        #conn = oracledb.connect(user=username, password=password, dsn=f"{endpoint}/orcl", port=port)
        conn = oracledb.connect(user=username, password=password, dsn=f"{endpoint}/{rds_db_name}", port=port)
    elif 'mysql' in engine_type.lower():
        conn = pymysql.connect(host=endpoint, port=port, user=username, password=password, db="sys", ssl={'_signed_cert': True})
    elif 'sqlserver' in engine_type.lower():
        conn = pymssql.connect(server=endpoint, port=port, user=username, password=password, database="master")
    elif 'postgres' in engine_type.lower():
        conn = psycopg2.connect(host=endpoint, port=port, user=username, password=password, database="postgres")
    else:
        raise ValueError("Unsupported engine type: {}. No platform level compliance check available, please perform self-assessment of database security against best practices".format(engine_type))
    return conn
    
def any_checks_pass(checks, result):
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
            expected_output = convert_to_primitive(expected_value_type, expected_output)
            result = convert_to_primitive(expected_value_type, result)
        try:
            if check_values(
                operand,
                expected_output,
                result,
            ):
                return True
        except ValueError as e:
            pass
    return False

def all_checks_pass(checks, result):
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
            expected_output = convert_to_primitive(expected_value_type, expected_output)
            result = convert_to_primitive(expected_value_type, result)
        if not check_values(
            operand,
            expected_output,
            result,
        ):
            return False
    return True

def convert_to_primitive(type_str, value):
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
    
def check_values(operand, expected, actual):
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
