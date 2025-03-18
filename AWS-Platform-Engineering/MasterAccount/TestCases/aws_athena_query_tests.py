def aws_athena_check_if_named_query_exist(athena_client, query_name):
    try:
        response = athena_client.get_named_query(
            NamedQueryId=query_name
        )
        print(response)
    except Exception as e:
        print("error occured while aws_athena_check_if_named_query_exist and error is {}".format(e))
        return False
    else:
         return True

