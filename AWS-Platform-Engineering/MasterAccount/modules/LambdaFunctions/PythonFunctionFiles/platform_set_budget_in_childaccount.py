"""
This module is used as part of account inflation to set budget in member account
"""
import random
import datetime
import logging
import boto3
import traceback

logger = logging.getLogger()
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


class SetBudgetInChildAccount(object):
    """
    # Class: SetBudgetInChildAccount
    # Description: Includes all the properties and method to Create sets the budget
    # in child account
    """

    def __init__(self, event, context):
        self.event = event
        self.context = context
        logger.info("Event: %s" % self.event)
        logger.info("Context: %s" % self.context)
        self.exception = []
        self.res_dict = {}
        try:
            # get relevant input params from event
            resource_properties = event['ResourceProperties']
            print(resource_properties)
            self.reason_data = ""
            session_client = boto3.Session()
            self.sts_client = session_client.client('sts')
            self.account_number = event['accountNumber']
            self.budget_value = resource_properties['Budget']
            if 'SupportDL' in self.event.keys():
                self.dlForNewAccount = self.event['SupportDL']
            else:
                self.dlForNewAccount = self.event['ResourceProperties']['SupportDL']
        except Exception as exception:
            self.res_dict['reason_data'] = "Missing required property %s" % exception
            logger.error(self.res_dict['reason_data'])
            self.exception.append(str(exception))
            self.res_dict['setBudget'] = "FAILED"
            self.res_dict['exception'] = self.exception
            raise Exception(str(exception))

    def set_budget_limit(self):
        """
        Set the budget limit in the Child account.
        """
        print("Inside Budget Function")
        budget_name = 'Monthly Budget Limit'
        time_format = '%d-%m-%Y'
        self.res_dict['send_budget_email'] = False
        try:
            # Todo : Change the notification threshold values in Prod env
            child_account_role_arn = "arn:aws:iam::{}:role/platform_service_inflation".format(
                self.account_number)
            child_account_session_name = \
                "ChildAccountSession-" + str(random.randint(1, 100000))
            child_account_role_creds = self.sts_client.assume_role(
                RoleArn=child_account_role_arn, RoleSessionName=child_account_session_name)
            child_credentials = child_account_role_creds.get('Credentials')
            child_access_key = child_credentials.get('AccessKeyId')
            child_secret_access_key = child_credentials.get('SecretAccessKey')
            child_session_token = child_credentials.get('SessionToken')
            child_assume_role_session = boto3.Session(
                child_access_key, child_secret_access_key, child_session_token)
            budget_client = child_assume_role_session.client(
                'budgets', region_name="us-east-1")
            describe_budgets_response = budget_client.describe_budgets(
                AccountId=self.account_number)
            print("Response to describe_budgets>>" + str(describe_budgets_response))
            print("Response keys to describe_budgets>>" +
                  str(describe_budgets_response.keys()))

            """Check if budget exists in the child account and the budget value is different then the new value if 
            yes update budget in child account"""
            if 'Budgets' in describe_budgets_response.keys():
                for x in describe_budgets_response['Budgets']:
                    if x['BudgetName'] == budget_name:
                        if float(x['BudgetLimit']['Amount']) != float(self.budget_value):
                            print("NEW BUDGET", self.budget_value)
                            update_budget_response = budget_client.update_budget(
                                AccountId=self.account_number,
                                NewBudget={
                                    'BudgetName': budget_name,
                                    'BudgetLimit': {
                                        'Amount': self.budget_value,
                                        'Unit': 'USD'
                                    },
                                    'CostTypes': {
                                        'IncludeTax': True,
                                        'IncludeSubscription': True,
                                        'UseBlended': True,
                                        'IncludeRefund': True,
                                        'IncludeCredit': True,
                                        'IncludeUpfront': True,
                                        'IncludeRecurring': True,
                                        'IncludeOtherSubscription': True,
                                        'IncludeSupport': True
                                    },
                                    'TimeUnit': 'MONTHLY',
                                    'TimePeriod': {
                                        'Start': datetime.datetime.now().strftime(time_format),
                                        'End': datetime.datetime(2040, 1, 1).strftime(time_format)
                                    },
                                    'BudgetType': 'COST'
                                }
                            )
                            print("Response to update_budget>>" + str(update_budget_response))

                            self.res_dict['send_budget_email'] = True
                            self.res_dict['setBudgetUpdate'] = "PASSED"
                        else:
                            print("No update in budget")
                            self.res_dict['send_budget_email'] = False
                            self.res_dict['setBudgetUpdate'] = "PASSED"

                        # Get current budget details to fetch notifications
                        current_budget_details = budget_client.describe_notifications_for_budget(
                            AccountId=self.account_number,
                            BudgetName=budget_name
                        )

                        # Loop through existing notifications
                        for notification in current_budget_details['Notifications']:
                            notification_type = notification['NotificationType']
                            subscribers = budget_client.describe_subscribers_for_notification(
                                AccountId=self.account_number,
                                Notification=notification,
                                BudgetName=budget_name
                            )
                            current_email = subscribers['Subscribers'][0]['Address']

                            # Update if the email is different
                            if current_email != self.dlForNewAccount:
                                update_subscriber_response = budget_client.update_subscriber(
                                    AccountId=self.account_number,
                                    BudgetName=budget_name,
                                    Notification=notification,
                                    OldSubscriber={
                                        'SubscriptionType': 'EMAIL',
                                        'Address': current_email
                                    },
                                    NewSubscriber={
                                        'SubscriptionType': 'EMAIL',
                                        'Address': self.dlForNewAccount  # Updated email address
                                    }
                                )
                                print(f"Updated {notification_type} subscriber: {update_subscriber_response}")
                                self.res_dict['budget_email_updated'] = True

            else:
                """Create budget ib child account"""
                self.res_dict['send_budget_email'] = False
                create_budget_response = budget_client.create_budget(
                    AccountId=self.account_number,
                    Budget={
                        'BudgetName': 'Monthly Budget Limit',
                        'BudgetLimit': {
                            'Amount': self.budget_value,
                            'Unit': 'USD'
                        },
                        'CostTypes': {
                            'IncludeTax': True,
                            'IncludeSubscription': True,
                            'UseBlended': True,
                            'IncludeRefund': True,
                            'IncludeCredit': True,
                            'IncludeUpfront': True,
                            'IncludeRecurring': True,
                            'IncludeOtherSubscription': True,
                            'IncludeSupport': True
                        },
                        'TimeUnit': 'MONTHLY',
                        'TimePeriod': {
                            'Start': datetime.datetime.now().strftime(time_format),
                            'End': datetime.datetime(2040, 1, 1).strftime(time_format)
                        },
                        'BudgetType': 'COST'
                    },
                    NotificationsWithSubscribers=[
                        {
                            'Notification': {
                                'NotificationType': 'ACTUAL',
                                'ComparisonOperator': 'GREATER_THAN',
                                'Threshold': 70,
                                'ThresholdType': 'PERCENTAGE'
                            },
                            'Subscribers': [
                                {
                                    'SubscriptionType': 'EMAIL',
                                    'Address': self.dlForNewAccount
                                },
                            ]
                        },
                        {
                            'Notification': {
                                'NotificationType': 'FORECASTED',
                                'ComparisonOperator': 'GREATER_THAN',
                                'Threshold': 70,
                                'ThresholdType': 'PERCENTAGE'
                            },
                            'Subscribers': [
                                {
                                    'SubscriptionType': 'EMAIL',
                                    'Address': self.dlForNewAccount
                                }
                            ]
                        }
                    ]
                )
                print("Billing response create_budget", create_budget_response)

                self.res_dict['send_budget_email'] = False
                self.res_dict['setBudgetCreate'] = "PASSED"
            return self.res_dict
        except Exception as exception:
            self.res_dict['reason_data'] = "Error in set budget %s" % exception
            logger.error(self.res_dict['reason_data'])
            logger.error(traceback.format_exc())
            self.exception.append(str(exception))
            self.res_dict['setBudget'] = "FAILED"
            self.res_dict['exception'] = self.exception
            self.res_dict['send_budget_email'] = False
            return self.res_dict


def lambda_handler(event, context):
    """
                This is the entry point of the module
                :param event:
                :param context:
                :return:
    """
    try:

        print("Input Event {}".format(event['RequestType']))
        set_budget_object = SetBudgetInChildAccount(event, context)
        output_value = set_budget_object.set_budget_limit()
        print("Output of the function : " + str(output_value))

        result = {}
        """if budget is updated, budget email has to be sent, if not do not sent the email."""
        if output_value['send_budget_email'] == True:
            if "emailParameter" in event.keys():
                email_parameter = event['emailParameter']
                email_parameter.append('budgetMail')
            else:
                email_parameter = []
                email_parameter.append('budgetMail')
            result['emailParameter'] = email_parameter
        result['setBudget'] = "PASSED"
        result.update(output_value)
        return result
    except Exception as exception:
        reason_data = "Missing required property %s" % exception
        logger.error(reason_data)
        result = {}
        result['setBudget'] = "FAILED"
        result['exception'] = exception
        return result

