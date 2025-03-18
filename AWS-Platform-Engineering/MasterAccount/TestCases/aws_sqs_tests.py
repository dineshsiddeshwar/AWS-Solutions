def aws_sqs_check_if_queue_is_created(sqs_client, queue_name):
    try:
        response = sqs_client.get_queue_url(
            QueueName= queue_name,
        )
        if len(response['QueueUrl']) > 0:
            print(response['QueueUrl'])
            return True
        else:
            return False
    except Exception as e:
        print("error occured while aws_sqs_check_if_queue_is_created and error is {}".format(e))
        return False
 