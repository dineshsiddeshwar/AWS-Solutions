def aws_backup_check_if_report_plan_exist(backup_client, plan):
    try:
        response = backup_client.list_report_plans()
        if len(response['ReportPlans']) > 0:
            for i in response['ReportPlans']:
                if i['ReportPlanName'] == plan:
                    print(i['ReportPlanName'])
                    return True
    except Exception as e:
        print("error occured while aws_backup_check_if_report_plan_exist and error is {}".format(e))
        return False
    else:
        return True