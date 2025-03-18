def aws_sns_check_if_topic_is_created(sns_client, topic_name, master_account_id):
    try:
        topic_arn = "arn:aws:sns:us-east-1:"+master_account_id+":"+topic_name
        response = sns_client.list_topics()
        result = response['Topics']
        while 'nextToken' in response:
            response = sns_client.list_topics(nextToken=response['NextToken'])
            result.extend(response['Topics'])
        if result:
            for item in result:
                if item['TopicArn'] == topic_arn:
                    print(item)
                    return True
        else:
            return False
    except Exception as e:
        print("error occured while aws_sns_check_if_topic_is_created and error is {}".format(e))
        return False
    
def aws_sns_check_if_subscription_is_created(sns_client, topic_name, master_account_id):
    try:
        topic_arn = "arn:aws:sns:us-east-1:"+master_account_id+":"+topic_name
        response = sns_client.list_subscriptions_by_topic(
            TopicArn=topic_arn
        )
        if len(response['Subscriptions']) > 0:
            print(response)
            return True
        else:
            return False
        
    except Exception as e:
        print("error occured while aws_sns_check_if_subscription_is_created and error is {}".format(e))
        return False


