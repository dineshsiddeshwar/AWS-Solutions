def aws_check_if_budget_enabled(budget, accountNumber):
    try:
        response = budget.describe_budget(
                        AccountId=accountNumber,
                        BudgetName='Monthly Budget Limit'
                    )
        print(response['Budget'])
    except Exception as e:
        print("error occured while aws_check_if_budget_enabled and error is {}".format(e))
        return False
    else:
         return True