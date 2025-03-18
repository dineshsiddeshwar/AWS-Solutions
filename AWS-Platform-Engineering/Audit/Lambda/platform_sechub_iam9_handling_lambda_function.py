# Description: This lambda function will suppress the IAM.9 finding for accounts that are less than 10 days old.
import boto3
import datetime
import json
import logging

# Initialize logger
# logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Set up AWS clients for Security Hub and Organizations
securityhub_client = boto3.client('securityhub', region_name='us-east-1')
organizations_client = boto3.client('organizations', region_name='us-east-1')
account_age_cache = {}


def account_age(account_id):
    try:
        if not account_id:
            logger.warning("Skipping finding due to missing account ID.")
            return None

        if account_id in account_age_cache:
            logger.debug(f"Using cached age for account {account_id}: {account_age_cache[account_id]} days old.")
            return account_age_cache[account_id]

        response = organizations_client.describe_account(AccountId=account_id)
        creation_date = response.get('Account', {}).get('JoinedTimestamp')

        if not creation_date:
            logger.warning(f"Skipping finding for account {account_id} due to missing creation date.")
            return None

        current_date = datetime.datetime.now(creation_date.tzinfo)
        age = (current_date - creation_date).days
        account_age_cache[account_id] = age

        return age
    except Exception as e:
        logger.error(f"Error getting account age for account {account_id}: {str(e)}")
        return None


def process_findings(findings):
    logger.info(f"Received {len(findings)} findings.")
    suppressed_findings = 0

    for finding in findings:
        try:
            if finding.get('Compliance', {}).get('SecurityControlId') != 'IAM.9':
                logger.debug(f"Skipping finding {finding.get('Id')}.")
                continue

            account_id = finding.get('AwsAccountId')
            age = account_age(account_id)
            if not age or age > 10:
                logger.debug(f"Account {account_id} is older than 10 days or invalid age {age}. Skipping resolution.")
                continue

            securityhub_client.batch_update_findings(
                FindingIdentifiers=[
                    {
                        'Id': finding.get('Id'),
                        'ProductArn': finding.get('ProductArn'),
                    }
                ],
                Note={
                    'Text': 'The account is less than 10 days old. Suppressing the IAM.9 finding.',
                    'UpdatedBy': 'Automated Remediation'
                },
                Workflow={
                    'Status': 'SUPPRESSED'
                },
                VerificationState='FALSE_POSITIVE',
                Confidence=0,
                Criticality=0,
                Severity={
                    'Label': 'INFORMATIONAL',
                    'Normalized': 0,
                    'Product': 0,
                },
            )
            logger.info(
                f"SUPPRESSED finding {finding.get('Id')} for account {account_id} in {finding.get('ProductArn')}."
                f" The account is less than 10 days old.")
            suppressed_findings += 1

        except Exception as e:
            logger.error(f"Error processing finding for account {account_id}: {str(e)}")

    return suppressed_findings


def lambda_handler(_event, _context):
    findings = get_findings({
        'ComplianceSecurityControlId': [{
            'Value': 'IAM.9',
            'Comparison': 'EQUALS'
        }],
        'ComplianceStatus': [{
            'Value': 'FAILED',
            'Comparison': 'EQUALS'
        }],
        'WorkflowStatus': [{
            'Value': 'NEW',
            'Comparison': 'EQUALS',
        }, {
            'Value': 'NOTIFIED',
            'Comparison': 'EQUALS',
        }]
    })

    logger.info(f"Found {len(findings)} active findings to suppress.")
    suppressed_findings = process_findings(findings)
    logger.info(f"Suppressed {suppressed_findings} findings out of {len(findings)} total findings.")

    return {
        'total_findings': len(findings),
        'suppressed_findings': suppressed_findings,
        'skipped_findings': len(findings) - suppressed_findings,
        'reactivated_findings': reactivate_iam9_findings(),
    }


def get_findings(filters):
    paginator = securityhub_client.get_paginator('get_findings')

    pagination_config = {
        'MaxItems': 10000,
        'PageSize': 100
    }

    findings = []

    while True:
        response = paginator.paginate(
            Filters=filters,
            PaginationConfig=pagination_config,
        )

        for page in response:
            findings.extend(page['Findings'])

        if 'NextToken' in response and response['NextToken']:
            pagination_config['StartingToken'] = response['NextToken']
        else:
            break

    return findings


def reactivate_iam9_findings():
    reactivated_findings = 0
    findings = get_findings({
        'ComplianceSecurityControlId': [{
            'Value': 'IAM.9',
            'Comparison': 'EQUALS'
        }],
        'ComplianceStatus': [{
            'Value': 'FAILED',
            'Comparison': 'EQUALS'
        }],
        'WorkflowStatus': [{
            'Value': 'SUPPRESSED',
            'Comparison': 'EQUALS',
        }]
    })

    try:
        logger.info(f"Found {len(findings)} suppressed findings to reactivate.")
        for finding in findings:
            account_id = finding.get('AwsAccountId')
            age = account_age(account_id)
            if not age:
                continue
            if not age or age < 10:
                logger.debug(f"Account {account_id} is less than 10 days or invalid age {age}. Skipping resolution.")
                continue

            securityhub_client.batch_update_findings(
                FindingIdentifiers=[
                    {
                        'Id': finding.get('Id'),
                        'ProductArn': finding.get('ProductArn'),
                    }
                ],
                Note={
                    'Text': 'The account is more than 10 days old. Reactivating the IAM.9 finding.',
                    'UpdatedBy': 'Automated Remediation'
                },
                Workflow={
                    'Status': 'NEW'
                },
                VerificationState='UNKNOWN',
                Confidence=100,
                Criticality=100,
                Severity={
                    'Label': 'CRITICAL',
                    'Normalized': 90,
                    'Product': 90,
                },
            )
            logger.info(
                f"REACTIVATED finding {finding.get('Id')} for account {account_id} in {finding.get('ProductArn')}."
                f" The account is more than 10 days old.")
            reactivated_findings += 1
    except Exception as e:
        logger.error(f"Error reactivating finding for account {account_id}: {str(e)}")

    return reactivated_findings
