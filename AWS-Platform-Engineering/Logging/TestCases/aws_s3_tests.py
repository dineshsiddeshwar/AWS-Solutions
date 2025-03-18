
def aws_check_if_s3_block_public_enabled(s3_client, account_id, bucket_name):
    try:
        response = s3_client.get_public_access_block(Bucket=bucket_name,ExpectedBucketOwner = account_id)
        print(response['PublicAccessBlockConfiguration'])
        req_status = {
            'BlockPublicAcls': True,
            'IgnorePublicAcls': True,
            'BlockPublicPolicy': True,
            'RestrictPublicBuckets': True
        }
        if response['PublicAccessBlockConfiguration'] == req_status:
            return True
        else:
            return False
    except Exception as e:
        print("error occured while aws_check_if_s3_block_public_enabled and error is {}".format(e))
        return False