def aws_cft_check_if_stackset_exist(cft, stackset_name):
    try:
        response = cft.describe_stack_set(
            StackSetName=stackset_name,
        )
        print(response['StackSet']['StackSetName'])
    except Exception as e:
        print("error occured while aws_cft_check_if_stackset_exist and error is {}".format(e))
        return False
    else:
         return True


def aws_cft_check_stackset_status(cft, stackset_name):
    try:
        response = cft.list_stack_set_operations(
            StackSetName=stackset_name,
        )
        print(response['Summaries'][0]['Status'])
    except Exception as e:
        print("error occured while aws_cft_check_stackset_status and error is {}".format(e))
        return False
    else:
         if response['Summaries'][0]['Status'] == 'Failed':
            return False
         else:
            return True 