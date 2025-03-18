def aws_kms_check_if_alias_exist(kms_client, alias):
    try:
        response = kms_client.list_aliases()
        if len(response['Aliases']) > 0:
            for item in response['Aliases']:
                if item['AliasName'] == alias:
                    print(item)
                    return True
        else:
            False
               
    except Exception as e:
        print("error occured while aws_kms_check_if_alias_exist and error is {}".format(e))
        return False

def aws_kms_check_if_key_exist(kms_client, alias):
    key_id = ""
    try:
        kms_alias_response = kms_client.list_aliases()
        if len(kms_alias_response['Aliases']) > 0:
            for item in kms_alias_response['Aliases']:
                if item['AliasName'] == alias:
                    key_id = item['TargetKeyId']

        kms_key_response = kms_client.list_keys()
        if len(kms_key_response['Keys']) > 0 and key_id:
            for item in kms_key_response['Keys']:            
                if item['KeyId'] == key_id:
                    print(item)
                    return True 
        else:
            return False

    except Exception as e:
        print("error occured while aws_kms_check_if_key_exist and error is {}".format(e))
        return False
    
def aws_kms_check_if_key_policy_created(kms_client, alias):
    key_id = ""
    try:
        kms_alias_response = kms_client.list_aliases()
        if len(kms_alias_response['Aliases']) > 0:
            for item in kms_alias_response['Aliases']:
                if item['AliasName'] == alias:
                    key_id = item['TargetKeyId']
                    
        if key_id:
            key_policy_response = kms_client.list_key_policies(
                KeyId=key_id
            )
        else:
            False
        if len(key_policy_response) > 0:
            print(key_policy_response)
            return True
        else:
            return False       
    except Exception as e:
        print("error occured while aws_kms_check_if_key_policy_created and error is {}".format(e))
        return False

          

