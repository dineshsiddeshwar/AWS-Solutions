def aws_check_if_securityhub_insights_enabled(securityhub):
    try:
        get_existing_Insights = securityhub.get_insights()
        if len(get_existing_Insights['Insights']) > 0:
            print('Insights available...Hence retruning True')
            return True
        else:
            print('No insights available...Hence retruning false')
            return False
    except Exception as e:
        print("error occured while aws_check_if_securityhub_insights_enabled and error is {}".format(e))
        return False
    
def aws_check_if_securityhub_CIS_standards_control_Refined(securityhub,region, child_account_number, CIS_Controls):
    try:
        StandardsSubscriptionArn = "arn:aws:securityhub:{}:{}:subscription/cis-aws-foundations-benchmark/v/1.2.0".format(region, child_account_number)
        DynamicStandardsControlArn ="arn:aws:securityhub:{}:{}:control/cis-aws-foundations-benchmark/v/1.2.0/{}".format(region, child_account_number, CIS_Controls)
        securityhub_standards_control = securityhub.describe_standards_controls(StandardsSubscriptionArn=StandardsSubscriptionArn)
        CIS_standards_control_List = securityhub_standards_control['Controls']
        while "NextToken" in securityhub_standards_control :
            securityhub_standards_control = securityhub.describe_standards_controls(StandardsSubscriptionArn=StandardsSubscriptionArn, NextToken=securityhub_standards_control['NextToken'])
            CIS_standards_control_List.extend(securityhub_standards_control['Controls'])
        Flag =  0
        for CIS_standards_control in CIS_standards_control_List:
            if CIS_standards_control['StandardsControlArn'] == DynamicStandardsControlArn and CIS_standards_control['ControlStatus'] == "DISABLED":
                Flag +=1
        if Flag > 0:
            return True
        else:
            return False
    except Exception as e:
        print("error occured while aws_check_if_securityhub_CIS_standards_control_Refined and error is {}".format(e))
        return False

def aws_check_if_securityhub_AWS_standards_control_Refined(securityhub,region, child_account_number, AWS_Controls):
    try:
        StandardsSubscriptionArn = "arn:aws:securityhub:{}:{}:subscription/aws-foundational-security-best-practices/v/1.0.0".format(region, child_account_number)
        DynamicStandardsControlArn ="arn:aws:securityhub:{}:{}:control/aws-foundational-security-best-practices/v/1.0.0/{}".format(region, child_account_number, AWS_Controls)
        securityhub_standards_control = securityhub.describe_standards_controls(StandardsSubscriptionArn=StandardsSubscriptionArn)
        AWS_standards_control_List = securityhub_standards_control['Controls']
        while "NextToken" in securityhub_standards_control :
            securityhub_standards_control = securityhub.describe_standards_controls(StandardsSubscriptionArn=StandardsSubscriptionArn, NextToken=securityhub_standards_control['NextToken'])
            AWS_standards_control_List.extend(securityhub_standards_control['Controls'])
        Flag =  0
        if AWS_Controls == "SSM.1" :
            ControlStatus = "ENABLED"
        else:
            ControlStatus = "DISABLED"
        for AWS_standards_control in AWS_standards_control_List:
            if AWS_standards_control['StandardsControlArn'] == DynamicStandardsControlArn and AWS_standards_control['ControlStatus'] == ControlStatus:
                Flag +=1
        if Flag > 0:
            return True
        else:
            return False
    except Exception as e:
        print("error occured while aws_check_if_securityhub_AWS_standards_control_Refined and error is {}".format(e))
        return False