def aws_servicecatalog_check_if_product_exist(servicecatalog_client, product_name):
    try:
        response = servicecatalog_client.search_products()
        if len(response['ProductViewSummaries']) > 0:
            for i in response['ProductViewSummaries']:
                if i['Name'] == product_name:
                    print(i['Name'])
        else:
            return False
    except Exception as e:
        print("error occured while aws_servicecatalog_check_if_product_exist and error is {}".format(e))
        return False
    else:
        return True

def aws_servicecatalog_check_if_product_portfolio_exist(servicecatalog_client, portfolio_name):
    try:
        response = servicecatalog_client.list_portfolios()
        if len(response['PortfolioDetails']) > 0:
            for item in response['PortfolioDetails']:
                if item['DisplayName'] == portfolio_name:
                    print(item)
        else:
            return False
    except Exception as e:
        print("error occured while aws_servicecatalog_check_if_product_portfolio_exist and error is {}".format(e))
        return False
    else:
        return True
    
def aws_servicecatalog_check_if_product_portfolio_associated(servicecatalog_client, product_name):
    try:
        product_id = ""
        product_response = servicecatalog_client.search_products()
        if len(product_response['ProductViewSummaries']) > 0:
            for i in product_response['ProductViewSummaries']:
                if i['Name'] == product_name:
                    print(i['Name'])
                    product_id = i['ProductId']

        if product_id:
            associated_response = servicecatalog_client.list_portfolios_for_product(
                ProductId=product_id
            )
            if len(associated_response['PortfolioDetails']) > 0:
                print(associated_response['PortfolioDetails'])
                return True
            else:
                return False
    except Exception as e:
        print("error occured while aws_servicecatalog_check_if_product_portfolio_associated and error is {}".format(e))
        return False   
    else:
        return True     

def aws_servicecatalog_check_if_principal_portfolio_associated(servicecatalog_client, portfolio_name):
    try:
        portfolio_id = ""
        response = servicecatalog_client.list_portfolios()
        if len(response['PortfolioDetails']) > 0:
            for item in response['PortfolioDetails']:
                if item['DisplayName'] == portfolio_name:
                    portfolio_id = item['Id']

        if portfolio_id:
            portfolio_response = servicecatalog_client.list_principals_for_portfolio(
                PortfolioId=portfolio_id
            )  
            if len(portfolio_response['Principals']) > 0:
                print(portfolio_response['Principals'])  
        else:
            return False
    except Exception as e:
        print("error occured while aws_servicecatalog_check_if_principal_portfolio_associated and error is {}".format(e))
        return False
    else:
        return True
