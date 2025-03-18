def aws_apigateway_check_if_rest_api_exist(apigateway_client, rest_api_name):
    try:
        response = apigateway_client.get_rest_apis()
        if len(response['items']) > 0:
            for item in response['items']:
                if item['name'] == rest_api_name:
                    print(item)
                    return True
        else:
            return False
    except Exception as e:
        print("error occured while aws_apigateway_check_if_rest_api_exist and error is {}".format(e))
        return False

def aws_apigateway_check_if_rest_api_key_exist(apigateway_client, api_key_name):
    try:
        response = apigateway_client.get_api_keys()
        if len(response['items']) > 0:
            for item in response['items']:
                if item['name'] == api_key_name:
                    print(item)
                    return True
        else:
            return False
    except Exception as e:
        print("error occured while aws_apigateway_check_if_rest_api_key_exist and error is {}".format(e))
        return False
    
def aws_apigateway_check_if_usage_plan_exist(apigateway_client, plan_name):
    try:
        plan_response = apigateway_client.get_usage_plans()
        if len(plan_response['items']) > 0:
            for item in plan_response['items']:
                if item['name'] == plan_name:
                    return True
        else:
            return False
    except Exception as e:
        print("error occured while aws_apigateway_check_if_usage_plan_exist and error is {}".format(e))
        return False

def aws_apigateway_check_if_usage_plan_key_exist(apigateway_client, plan_name):
    try:
        usage_plan_id = ""
        plan_response = apigateway_client.get_usage_plans()
        if len(plan_response['items']) > 0:
            for item in plan_response['items']:
                if item['name'] == plan_name:
                    usage_plan_id = item['id']
        else:
            return False 
        if usage_plan_id:
            plan_key_response = apigateway_client.get_usage_plan_keys(
                usagePlanId=usage_plan_id
            )              
            if len(plan_key_response['items']) > 0:
                return True
            else:
                return False
        else:
            return False
    except Exception as e:
        print("error occured while aws_apigateway_check_if_usage_plan_key_exist and error is {}".format(e))
        return False
    
def aws_apigateway_check_if_deployment_exist(apigateway_client, rest_api_name):
    try:
        rest_api_id = ""
        api_response = apigateway_client.get_rest_apis()
        if len(api_response['items']) > 0:
            for item in api_response['items']:
                if item['name'] == rest_api_name:
                    rest_api_id = item['id']
        if rest_api_id:
            deployment_response = apigateway_client.get_deployments(
                restApiId=rest_api_id
            )   
            if len(deployment_response['items']) > 0:
                print(deployment_response['items'])
                return True
            else:
                return False
        else:
            return False
        
    except Exception as e:
        print("error occured while aws_apigateway_check_if_deployment_exist and error is {}".format(e))
        return False

def aws_apigateway_check_if_stage_exist(apigateway_client, rest_api_name):
    try:
        rest_api_id = ""
        api_response = apigateway_client.get_rest_apis()
        if len(api_response['items']) > 0:
            for item in api_response['items']:
                if item['name'] == rest_api_name:
                    rest_api_id = item['id']
        if rest_api_id:
            stage_response = apigateway_client.get_stages(
                restApiId=rest_api_id
            )   
            if len(stage_response['item']) > 0:
                print(stage_response['item'])
                return True
            else:
                return False
        else:
            return False
        
    except Exception as e:
        print("error occured while aws_apigateway_check_if_stage_exist and error is {}".format(e))
        return False
    
def aws_apigateway_check_if_resource_exist(apigateway_client, rest_api_name):
    try:
        rest_api_id = ""
        api_response = apigateway_client.get_rest_apis()
        if len(api_response['items']) > 0:
            for item in api_response['items']:
                if item['name'] == rest_api_name:
                    rest_api_id = item['id']
        if rest_api_id:
            resource_response = apigateway_client.get_resources(
                restApiId=rest_api_id
            )   
            if len(resource_response['items']) > 0:
                print(resource_response['items'])
                return True
            else:
                return False
        else:
            return False
        
    except Exception as e:
        print("error occured while aws_apigateway_check_if_resource_exist and error is {}".format(e))
        return False
    
def aws_apigateway_check_if_authorizer_exist(apigateway_client, rest_api_name):
    try:
        rest_api_id = ""
        api_response = apigateway_client.get_rest_apis()
        if len(api_response['items']) > 0:
            for item in api_response['items']:
                if item['name'] == rest_api_name:
                    rest_api_id = item['id']
        if rest_api_id:
            authorizer_response = apigateway_client.get_authorizers(
                restApiId=rest_api_id
            )   
            if len(authorizer_response['items']) > 0:
                print(authorizer_response['items'])
                return True
            else:
                return False
        else:
            return False
        
    except Exception as e:
        print("error occured while aws_apigateway_check_if_authorizer_exist and error is {}".format(e))
        return False
    
def aws_apigateway_check_if_method_exist(apigateway_client, rest_api_name, http_name):
    try:
        rest_api_id = ""
        resource_id = ""
        api_response = apigateway_client.get_rest_apis()
        if len(api_response['items']) > 0:
            for item in api_response['items']:
                if item['name'] == rest_api_name:
                    rest_api_id = item['id']
        if rest_api_id:
            resource_response = apigateway_client.get_resources(
                restApiId=rest_api_id
            )   
            if len(resource_response['items']) > 0:
                for i in resource_response['items']:
                    if 'parentId' in i.keys():
                        resource_id = i['id']

            if resource_id:
                method_response = apigateway_client.get_method(
                    restApiId=rest_api_id,
                    resourceId=resource_id,
                    httpMethod=http_name
                ) 
                if method_response:
                    print(method_response)                          
    except Exception as e:
        print("error occured while aws_apigateway_check_if_method_exist and error is {}".format(e))
        return False
    else: 
        return True  

def aws_apigateway_check_if_method_response_exist(apigateway_client, rest_api_name, http_name):
    try:
        rest_api_id = ""
        resource_id = ""
        api_response = apigateway_client.get_rest_apis()
        if len(api_response['items']) > 0:
            for item in api_response['items']:
                if item['name'] == rest_api_name:
                    rest_api_id = item['id']
        if rest_api_id:
            resource_response = apigateway_client.get_resources(
                restApiId=rest_api_id
            )   
            if len(resource_response['items']) > 0:
                for i in resource_response['items']:
                    if 'parentId' in i.keys():
                        resource_id = i['id']

            if resource_id:
                method_response = apigateway_client.get_method_response(
                    restApiId=rest_api_id,
                    resourceId=resource_id,
                    httpMethod=http_name,
                    statusCode="200"
                ) 
                if method_response:
                    print(method_response)         
    except Exception as e:
        print("error occured while aws_apigateway_check_if_method_response_exist and error is {}".format(e))
        return False
    else: 
        return True 
        
def aws_apigateway_check_if_integration_exist(apigateway_client, rest_api_name, http_name):
    try:
        rest_api_id = ""
        resource_id = ""
        api_response = apigateway_client.get_rest_apis()
        if len(api_response['items']) > 0:
            for item in api_response['items']:
                if item['name'] == rest_api_name:
                    rest_api_id = item['id']
        if rest_api_id:
            resource_response = apigateway_client.get_resources(
                restApiId=rest_api_id
            )   
            if len(resource_response['items']) > 0:
                for i in resource_response['items']:
                    if 'parentId' in i.keys():
                        resource_id = i['id']

            if resource_id:
                integartion_response = apigateway_client.get_integration(
                    restApiId=rest_api_id,
                    resourceId=resource_id,
                    httpMethod=http_name
                ) 
                if integartion_response:
                    print(integartion_response)       
    except Exception as e:
        print("error occured while aws_apigateway_check_if_integration_exist and error is {}".format(e))
        return False
    else: 
        return True 
    
def aws_apigateway_check_if_integration_response_exist(apigateway_client, rest_api_name, http_name):
    try:
        rest_api_id = ""
        resource_id = ""
        api_response = apigateway_client.get_rest_apis()
        if len(api_response['items']) > 0:
            for item in api_response['items']:
                if item['name'] == rest_api_name:
                    rest_api_id = item['id']
        if rest_api_id:
            resource_response = apigateway_client.get_resources(
                restApiId=rest_api_id
            )   
            if len(resource_response['items']) > 0:
                for i in resource_response['items']:
                    if 'parentId' in i.keys():
                        resource_id = i['id']

            if resource_id:
                integartion_response = apigateway_client.get_integration_response(
                    restApiId=rest_api_id,
                    resourceId=resource_id,
                    httpMethod=http_name,
                    statusCode="200"
                ) 
                if integartion_response:
                    print(integartion_response)      
    except Exception as e:
        print("error occured while aws_apigateway_check_if_integration_response_exist and error is {}".format(e))
        return False
    else: 
        return True 