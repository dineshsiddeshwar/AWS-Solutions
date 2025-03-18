def aws_lambda_check_if_function_exist(lambda_client, function_name):
    try:
        response = lambda_client.get_function(
            FunctionName=function_name
        )
        print(response['Configuration'])
    except Exception as e:
        print("error occured while aws_iam_check_if_role_exist and error is {}".format(e))
        return False
    else:
         return True

def aws_lambda_check_if_lambda_permission_added(lambda_client, function_name):
    try:
        response = lambda_client.get_policy(
            FunctionName=function_name
        )
        print(response)
    except Exception as e:
        print("error occured while aws_lambda_check_if_lambda_permission_added and error is {}".format(e))
        return False
    else:
         return True
    
def aws_lambda_check_if_lambda_layer_is_created(lambda_client, layer_name):
    try:
        response = lambda_client.list_layers()
        layers = response.get('Layers', [])
        next_marker = response.get('NextMarker', None)
        
        while next_marker:
            response = lambda_client.list_layers(Marker=next_marker)
            layers.extend(response.get('Layers', []))
            next_marker = response.get('NextMarker', None)

        if len(layers) > 0:
            for item in layers:
                if item['LayerName'] == layer_name:
                    print(item)
                    return True
        else:
            return False
    except Exception as e:
        print("error occured while aws_lambda_check_if_lambda_layer_is_created and error is {}".format(e))
        return False
    
    
def aws_lambda_check_if_event_source_mapping_is_created(lambda_client, function_name):
    try:
        response = lambda_client.list_event_source_mappings(
            FunctionName=function_name
        )
        if len(response['EventSourceMappings']) > 0:
            print(response['EventSourceMappings'])
            return True
        else:
            return False
    except Exception as e:
        print("error occured while aws_lambda_check_if_event_source_mapping_is_created and error is {}".format(e))
        return False

