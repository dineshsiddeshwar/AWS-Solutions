def aws_check_if_cloudformation_stack_exist(cf_client, stackname):
    try:
        response = cf_client.list_stacks()
        result = response['StackSummaries']
        while "NextToken" in response:
            response = cf_client.list_stacks(NextToken=response['NextToken'])
            result.extend(response['StackSummaries'])
        if len(result) > 0:
            for i in result:
                if i['StackName'] == stackname:
                    print(i['StackName'])
                    return True

    except Exception as e:
        print("error occured while aws_check_if_vpc_is_created and error is {}".format(e))
        return False
    else:
        return False
