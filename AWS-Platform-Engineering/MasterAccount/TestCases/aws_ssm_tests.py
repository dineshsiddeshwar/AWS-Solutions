def aws_ssm_check_if_paraeter_is_created(ssm_client, parameter):
    try:
        response = ssm_client.get_parameter(
            Name=parameter
        )
        if len(response['Parameter']) > 0:
            print(response['Parameter'])
            return True
        else:
            return False
    except Exception as e:
        print("error occured while aws_check_if_ssm_associations_created and error is {}".format(e))
        return False
    
