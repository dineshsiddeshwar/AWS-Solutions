def aws_lambda_check_if_function_exist(lambda_client, function_name):
    try:
        response = lambda_client.get_function(FunctionName=function_name)
        if response['Configuration']['FunctionName'] == function_name:
            return True
        else:
            return False
    except Exception as e:
        print("error occured when calling the getfunction api and error is {}".format(e))
        return False