def aws_check_if_resolver_endpoint_exists(resolver_client):
    try:
        response = resolver_client.list_resolver_endpoints()
        endpoint_list = response['ResolverEndpoints']
        if len(endpoint_list) > 0:
            for endpoint in endpoint_list:
                if endpoint['Name']=="platform_Shell_Domain_Resolver":
                    print("Resolver Endpoint found, id is {}".format(endpoint_list[0]['Id']))
                    return True
                   
            print("Resolver Endpoint with platform_Shell_Domain_Resolver not found")
            return False
    except Exception as e:
        print("Error occurred while aws_check_if_resolver_endpoint_exists and error is {}".format(e))
        return False

def aws_check_if_resolver_rule_exists(resolver_client):
    try:
        response = resolver_client.list_resolver_rules()
        if len(response['ResolverRules']) > 0:
            for rule in response['ResolverRules']:
                if 'Domain_Forwarder' in rule['Name']:
                    print("Resolver Rule found, id is {}".format(rule['Id']))
                    return True
            print("Resolver Rule with platform_Shell_Domain_Forwarder_Outbound_Rule not found")
            return False
    except Exception as e:
        print("Error occurred while aws_check_if_resolver_rule_exists and error is {}".format(e))
        return False

def aws_check_if_resolver_rule_associations_exists(resolver_client):
    try:
        response = resolver_client.list_resolver_rule_associations()
        if len(response['ResolverRuleAssociations']) > 0:
            for a in response['ResolverRuleAssociations']:
                if 'Domain_Forwarder' in a['Name']:
                    print("Resolver Rule Association found, id is {}".format(a['Id']))
                    return True
            print("Resolver Rule Association for Rule platform_Shell_Domain_Forwarder_Outbound_Rule not found")
            return False
    except Exception as e:
        print("Error occurred while aws_check_if_resolver_rule_associations_exists and error is {}".format(e))
        return False