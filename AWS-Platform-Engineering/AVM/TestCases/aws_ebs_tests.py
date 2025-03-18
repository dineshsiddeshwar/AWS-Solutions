def aws_check_if_ebs_encryp_enabled(ec2_client):
    try:
        response = ec2_client.get_ebs_encryption_by_default()
        if response['EbsEncryptionByDefault'] is False:
            return False
        elif response['EbsEncryptionByDefault'] is True:
            return True
    except Exception as e:
        print("error occured while aws_check_if_ebs_encryp_enabled and error is {}".format(e))
        return False