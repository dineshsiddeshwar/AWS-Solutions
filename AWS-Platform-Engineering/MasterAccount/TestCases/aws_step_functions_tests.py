def aws_stepfunctions_check_if_state_machine_exist(stepfunctions_client, sm_name):
    try:
        response = stepfunctions_client.list_state_machines()
        if len(response['stateMachines']) > 0:
            for item in response['stateMachines']:
                if item['name'] == sm_name:
                    print(item)
                    return True
        else:
            return False  
        print(response)
    except Exception as e:
        print("error occured while aws_stepfunctions_check_if_state_machine_exist and error is {}".format(e))
        return False

