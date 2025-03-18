def aws_check_if_config_rule_created(Config, ConfigRuleName):
    try:
        response = Config.describe_config_rules(
                                ConfigRuleNames=[ConfigRuleName]
                            )
        print(response['ConfigRules'])
    except Exception as e:
        print("error occured while aws_check_if_config_rule_created and error is {}".format(e))
        return False
    else:
         return True
