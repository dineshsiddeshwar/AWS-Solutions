def aws_glue_check_if_database_exist(glue_client, db_name):
    try:
        response = glue_client.get_database(
            Name=db_name
        )
        print(response)
    except Exception as e:
        print("error occured while aws_glue_check_if_database_exist and error is {}".format(e))
        return False
    else:
         return True
    
def aws_glue_check_if_crawler_exist(glue_client, crawler_name):
    try:
        response = glue_client.get_crawler(
            Name=crawler_name
        )
        print(response)
    except Exception as e:
        print("error occured while aws_glue_check_if_crawler_exist and error is {}".format(e))
        return False
    else:
         return True

def aws_glue_check_if_classifier_exist(glue_client, classifier_name):
    try:
        response = glue_client.get_classifier(
            Name=classifier_name
        )
        print(response)
    except Exception as e:
        print("error occured while aws_glue_check_if_classifier_exist and error is {}".format(e))
        return False
    else:
         return True
