def aws_check_if_emr_block_public_enabled(emr_client):
    try:
        response = emr_client.get_block_public_access_configuration()
        if response['BlockPublicAccessConfiguration']['BlockPublicSecurityGroupRules'] is True:
            return True
        else:
            return False
    except Exception as e:
        print("error occured while aws_check_if_emr_block_public_enabled and error is {}".format(e))
        return False