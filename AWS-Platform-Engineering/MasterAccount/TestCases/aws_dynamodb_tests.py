def aws_dynamodb_check_if_table_exist(dynamodb_client, table_name):
    try:
        response = dynamodb_client.list_tables(
            ExclusiveStartTableName=table_name
        )
        print(response)
    except Exception as e:
        print("error occured while aws_dynamodb_check_if_table_exist and error is {}".format(e))
        return False
    else:
         return True

