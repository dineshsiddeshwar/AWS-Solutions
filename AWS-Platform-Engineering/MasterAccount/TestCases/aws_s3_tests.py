def aws_s3_check_if_bucket_exist(s3_client, bucket_name):
    try:
        response = s3_client.create_bucket(
            Bucket=bucket_name
        )
        print(response)
    except Exception as e:
        print("error occured while aws_s3_check_if_bucket_exist and error is {}".format(e))
        return False
    else:
         return True

def aws_s3_check_if_bucket_is_encrypted(s3_client, bucket_name):
    try:
        response = s3_client.get_bucket_encryption(
            Bucket=bucket_name
        )
        print(response)
    except Exception as e:
        print("error occured while aws_s3_check_if_bucket_is_encrypted and error is {}".format(e))
        return False
    else:
         return True

def aws_s3_check_if_bucket_is_having_public_access_block(s3_client, bucket_name):
    try:
        response = s3_client.get_public_access_block(
            Bucket=bucket_name
        )
        print(response)
    except Exception as e:
        print("error occured while aws_s3_check_if_bucket_is_having_public_access_block and error is {}".format(e))
        return False
    else:
         return True
    
def aws_s3_check_if_bucket_is_having_versioning_enabled(s3_client, bucket_name):
    try:
        response = s3_client.get_bucket_versioning(
            Bucket=bucket_name
        )
        print(response)
    except Exception as e:
        print("error occured while aws_s3_check_if_bucket_is_having_versioning_enabled and error is {}".format(e))
        return False
    else:
         return True

def aws_s3_check_if_bucket_is_having_lifecycle_configuration(s3_client, bucket_name):
    try:
        response = s3_client.get_bucket_lifecycle_configuration(
            Bucket=bucket_name
        )
        print(response)
    except Exception as e:
        print("error occured while aws_s3_check_if_bucket_is_having_lifecycle_configuration and error is {}".format(e))
        return False
    else:
         return True

def aws_s3_check_if_bucket_is_having_ownership_controls(s3_client, bucket_name):
    try:
        response = s3_client.get_bucket_ownership_controls(
            Bucket=bucket_name
        )
        print(response)
    except Exception as e:
        print("error occured while aws_s3_check_if_bucket_is_having_ownership_controls and error is {}".format(e))
        return False
    else:
         return True
    
def aws_s3_check_if_bucket_is_having_bucket_policy(s3_client, bucket_name):
    try:
        response = s3_client.get_bucket_policy(
            Bucket=bucket_name
        )
        print(response)
    except Exception as e:
        print("error occured while aws_s3_check_if_bucket_is_having_bucket_policy and error is {}".format(e))
        return False
    else:
         return True
       
def aws_s3_check_if_bucket_is_having_notification_configuration(s3_client, bucket_name):
    try:
        response = s3_client.get_bucket_notification_configuration(
            Bucket=bucket_name
        )
        print(response)
    except Exception as e:
        print("error occured while aws_s3_check_if_bucket_is_having_notification_configuration and error is {}".format(e))
        return False
    else:
         return True