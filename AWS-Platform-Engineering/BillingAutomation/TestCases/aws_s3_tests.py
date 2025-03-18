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
    
