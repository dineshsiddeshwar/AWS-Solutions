def aws_sqs_check_if_queue_exist(sqs_client, queue_name):
    try:
        response = sqs_client.get_queue_url(QueueName=queue_name,)
        if 'QueueUrl' in response:
            return True
        else:
            return False
    except Exception as e:
        print("error occured when calling the get_queue_url api and error is {}".format(e))
        return False