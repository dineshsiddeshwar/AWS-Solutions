import boto3
import logging
import random
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)
child_account_role_session_name = "ChildAccountSession-" + str(random.randint(1, 100000))


class CreateCustomInsights(object):
    """
       # Class: CreateCustomInsights
       # Description: Creates custom insights in Security hub
       #  after the Child account is created.
    """
    ''' insight for showing Managed Instance vs Non-Managed instance count '''
    ssm_managed_instance_count = {
        'Type': [
            {
                'Value': 'Software and Configuration Checks/Industry and Regulatory Standards/AWS-Foundational-Security-Best-Practices',
                'Comparison': 'EQUALS'
            }
        ],
        'RecordState': [
            {
                'Value': 'ACTIVE',
                'Comparison': 'EQUALS'
            }
        ],
        'WorkflowStatus': [
            {
                'Value': 'SUPPRESSED',
                'Comparison': 'NOT_EQUALS'
            },
        ],
        'Title': [
            {
                'Value': 'SSM.1',
                'Comparison': 'PREFIX'
            }
        ],
        'ResourceType': [
            {
                'Value': 'AwsEc2Instance',
                'Comparison': 'EQUALS'
            }
        ]
    }
    aws_foundational_security_best_practices = {
        'Type': [
            {
                'Value': 'Software and Configuration Checks/Industry and Regulatory Standards/AWS-Foundational-Security-Best-Practices',
                'Comparison': 'EQUALS'
            }
        ],
        'RecordState': [
            {
                'Value': 'ACTIVE',
                'Comparison': 'EQUALS'

            }
        ],
        'WorkflowStatus': [
            {
                'Value': 'SUPPRESSED',
                'Comparison': 'NOT_EQUALS'
            },
        ],
        'ComplianceStatus': [
            {
                'Value': 'FAILED',
                'Comparison': 'EQUALS'
            }
        ]
    }
    cis_foundational_security_best_practices = {
        'Type': [
            {
                'Value': 'Software and Configuration Checks/Industry and Regulatory Standards/CIS AWS Foundations Benchmark',
                'Comparison': 'EQUALS'
            }
        ],
        'RecordState': [
            {
                'Value': 'ACTIVE',
                'Comparison': 'EQUALS'

            }
        ],
        'WorkflowStatus': [
            {
                'Value': 'SUPPRESSED',
                'Comparison': 'NOT_EQUALS'
            },
        ],
        'ComplianceStatus': [
            {
                'Value': 'FAILED',
                'Comparison': 'EQUALS'
            }
        ]

    }
    # ssm_patch_manager_findings = {
    #     'ProductName': [
    #         {
    #             'Value': 'Systems Manager Patch Manager',
    #             'Comparison': 'EQUALS'
    #         }
    #     ],
    #     'WorkflowStatus': [
    #         {
    #             'Value': 'SUPPRESSED',
    #             'Comparison': 'NOT_EQUALS'
    #         },
    #     ],
    #     'RecordState': [
    #         {
    #             'Value': 'ACTIVE',
    #             'Comparison': 'EQUALS'
    #         }
    #     ],
    # }
    amazon_guardDuty_findings = {
        'ProductName': [
            {
                'Value': 'GuardDuty',
                'Comparison': 'EQUALS'
            }
        ],
        'WorkflowStatus': [
            {
                'Value': 'SUPPRESSED',
                'Comparison': 'NOT_EQUALS'
            },
        ],
        'RecordState': [
            {
                'Value': 'ACTIVE',
                'Comparison': 'EQUALS'
            }
        ],
    }
    iam_Access_Analyzer_findings = {
        'ProductName': [
            {
                'Value': 'IAM Access Analyzer',
                'Comparison': 'EQUALS'
            }
        ],
        'WorkflowStatus': [
            {
                'Value': 'SUPPRESSED',
                'Comparison': 'NOT_EQUALS'
            },
        ],
        'RecordState': [
            {
                'Value': 'ACTIVE',
                'Comparison': 'EQUALS'
            }
        ],
    }
    unresolved_findings = {
        'WorkflowStatus': [
            {
                'Value': 'SUPPRESSED',
                'Comparison': 'NOT_EQUALS'
            },
            {
                'Value': 'RESOLVED',
                'Comparison': 'NOT_EQUALS'
            }
        ],
    }

    custom_insights = [
        {'AWS-FOUNDATIONAL-SECURITY-BEST-PRACTICES': aws_foundational_security_best_practices},
        {'CIS-FOUNDATIONAL-SECURITY-BEST-PRACTICES': cis_foundational_security_best_practices},
        # {'SSM-PATCH-MANAGER-FINDINGS': ssm_patch_manager_findings},
        {'AMAZON-GUARDDUTY-FINDINGS': amazon_guardDuty_findings},
        {'IAM-ACCESS-ANALYSER-FINDINGS': iam_Access_Analyzer_findings},
        {'UNRESOLVED-FINDINGS': unresolved_findings},
        {'SSM-MANAGED-INSTANCE-COUNT': ssm_managed_instance_count}

    ]

    def __init__(self, event, context):
        try:
            self.event = event
            self.context = context
            logger.info("Event: %s" % self.event)
            logger.info("Context: %s" % self.context)
            self.request_type = event['RequestType']
            self.account_id = event['accountNumber']
            logger.info(self.request_type)
            logger.info(self.account_id)
            print("Creating Session and AWS Service Clients")
            session = boto3.session.Session()
            sts_client = session.client('sts')
            child_account_role_arn = "arn:aws:iam::" + self.account_id + ":role/AWSControlTowerExecution"
            child_account_role_creds = sts_client.assume_role(RoleArn=child_account_role_arn,
                                                              RoleSessionName=child_account_role_session_name)
            credentials = child_account_role_creds.get('Credentials')
            accessKeyID = credentials.get('AccessKeyId')
            secretAccessKey = credentials.get('SecretAccessKey')
            sessionToken = credentials.get('SessionToken')
            self.assumeRoleSession = boto3.session.Session(accessKeyID, secretAccessKey, sessionToken)
            print(self.assumeRoleSession)
        except Exception as exception:
            print(str(exception))
            logger.error(str(exception))

    """method for creating custom insights"""

    def create_custom_insights(self, name, filters):
        try:
            if self.request_type == 'Create' or self.request_type == 'Update':
                client = self.assumeRoleSession.client('securityhub')
                get_existing_Insights = client.get_insights()
                insight_names = []
                if len(get_existing_Insights['Insights']) > 0:
                    for insight_name in get_existing_Insights['Insights']:
                        insight_names.append(insight_name['Name'])
                else:
                    print('No insights available...Creating new custom insights')
                if name not in insight_names:
                    print('creating new custom insight', name)
                    if name != 'SSM_MANAGED_INSTANCE_COUNT':
                        response = client.create_insight(Name=name, Filters=filters, GroupByAttribute='SeverityLabel')
                    else:
                        response = client.create_insight(Name=name, Filters=filters,
                                                         GroupByAttribute='ComplianceStatus')
                    print(response['InsightArn'])
                return insight_names
        except Exception as exception:
            print('failed to create insight:{}'.format(str(exception)))


def lambda_handler(event, context):
    """
    This is the entry point of the module
    :param event:
    :param context:
    :return:
    """
    result_value = {}
    try:
        result_value.update(event)
        create_insights = CreateCustomInsights(event, context)
        insight_names = ''
        for insight in create_insights.custom_insights:
            for i in insight:
                insight_names = create_insights.create_custom_insights(i, insight.get(i))
        print('BELOW ARE CUSTOM INSIGHTS AVAILABLE IN AWS@Shell ACCOUNT')
        print(insight_names)
        print("final response", json.dumps(result_value))
        return result_value
    except Exception as e:
        print(e)
        print(result_value)
        return result_value
