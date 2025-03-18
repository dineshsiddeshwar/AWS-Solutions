def aws_events_check_if_rule_exist(events_client, rule):
    try:
        response = events_client.list_rules()
        if len(response['Rules']) > 0:
            for i in response['Rules']:
                if i['Name'] == rule:
                    print(i['Name'])
                    return True
    except Exception as e:
        print("error occured while aws_events_check_if_rule_t_exist and error is {}".format(e))
        return False
    else:
        return True
     
def aws_events_check_if_target_exist(events_client, rule):
    try:
        response = events_client.list_targets_by_rule(
            Rule=rule
        )
        if len(response['Targets']) > 0:
            print(response)
            return True
    except Exception as e:
        print("error occured while aws_events_check_if_target_exist and error is {}".format(e))
        return False
    else:
        return True

def aws_events_check_if_scheduler_exist(scheduler_client, group,schedulename):
    try:
        response = scheduler_client.get_schedule(
            GroupName=group,
            Name=schedulename
        )
        if response:
            print(response)
            return True
    except Exception as e:
        print("error occured while aws_events_check_if_scheduler_exist and error is {}".format(e))
        return False
    else:
        return True

def aws_events_check_if_bus_exist(events_client, bus):
    try:
        response = events_client.list_event_buses()
        if len(response['EventBuses']) > 0:
            for i in response['EventBuses']:
                if i['Name'] == bus:
                    print(i['Name'])
                    return True
    except Exception as e:
        print("error occured while aws_events_check_if_bus_exist and error is {}".format(e))
        return False
    else:
        return True
    
def aws_events_check_if_bus_policy_exist(events_client, bus):
    try:
        response = events_client.list_event_buses()
        if len(response['EventBuses']) > 0:
            for i in response['EventBuses']:
                if i['Name'] == bus:
                    if i['Policy']:
                        return True
    except Exception as e:
        print("error occured while aws_events_check_if_bus_policy_exist and error is {}".format(e))
        return False
    else:
        return True