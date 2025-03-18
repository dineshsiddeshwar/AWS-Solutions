# (c) 2021 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.
# This AWS Content is provided subject to the terms of the AWS Customer Agreement available at
# https://aws.amazon.com/agreement/ or other written agreement between Customer
# and Amazon Web Services, Inc.

"""Key Actions - Mapping of Action Reasons.

This class provides the mappings to different key
rotation logic actions.
"""

import datetime,os
import dateutil.tz
import logging
from botocore.exceptions import ClientError

from enum import Enum


# setup script logging
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class ActionReasons(Enum):
    UNUSED_EXPIRED_KEY = 'Expired key has never been used.'
    EXPIRED_ACTIVE_KEY = 'Active key has expired.'
    KEY_PENDING_ROTATION = 'Key is about to expire and should be rotated soon.'
    UNUSED_KEY_PENDING_DELETION = 'key is about to expire and has never been used. '


def get_actions_for_keys(access_key_metadata, account_session):
    action_queue = []
    keys = []

    # The number of days after which a key should be rotated
    # Default = 90 days
    rotationPeriod = int(os.getenv('RotationPeriod', 90))

    # how many days ahead of time to warn users of pending actions
    pending_action_warn_period = int(os.getenv('WarnPeriod', 10))

    iam_client = account_session.client('iam')

    # Cache current time to avoid race conditions
    now = datetime.datetime.now(tz=dateutil.tz.gettz('US/Eastern'))
    warn_period = datetime.timedelta(days=pending_action_warn_period)

    print("------------------------------printing----------------------")
    print(access_key_metadata)

    for key in access_key_metadata:
        # Populate lastused and expiration dates
        try:
            key['LastUsedDate'] = iam_client.get_access_key_last_used(
                AccessKeyId=key['AccessKeyId']
            )['AccessKeyLastUsed']['LastUsedDate']
        except:
            log.info("--Key has not been used before.")
            key['LastUsedDate'] = None

        key['ExpireDate'] = key['CreateDate'] + \
                            datetime.timedelta(days=rotationPeriod)


        # if the key is expired and has never been used, just delete it
        if key['LastUsedDate'] is None \
                and key['ExpireDate'] <= now:
            reason = ActionReasons.UNUSED_EXPIRED_KEY
            log.info(
                f'ROTATE_AND_DELETE {key["UserName"]}: {key["AccessKeyId"]} '
                f'-- {reason.value}')
            action_queue.append({
                'action': 'ROTATE_AND_DELETE',
                'key': key,
                'reason': reason
            })
            continue

        # if the key is about to expire and has never been used, warn
        elif key['LastUsedDate'] is None \
                and key['ExpireDate'] <= now + warn_period:
            reason = ActionReasons.UNUSED_KEY_PENDING_DELETION
            log.info(
                f'WARN {key["UserName"]}: {key["AccessKeyId"]} '
                f'-- {reason.value}')
            action_queue.append({
                'action': 'WARN',
                'action_date': key['ExpireDate'],
                'key': key,
                'reason': reason
            })
        elif key['LastUsedDate'] and key['ExpireDate'] <= now:
            reason = ActionReasons.EXPIRED_ACTIVE_KEY
            # key is expired and needs to be rotated
            log.info(
                f'ROTATE {key["UserName"]}: {key["AccessKeyId"]}'
                f'-- {reason.value}')
            action_queue.append({
                'action': 'ROTATE',
                'key': key,
                'reason': reason
            })
        elif key['LastUsedDate'] and key['ExpireDate'] <= now + warn_period:
            reason = ActionReasons.KEY_PENDING_ROTATION
            log.info(
                f'WARN {key["UserName"]}: {key["AccessKeyId"]}'
                f'-- {reason.value}')
            action_queue.append({
                'action': 'WARN',
                'action_date': key['ExpireDate'],
                'key': key,
                'reason': reason
            })

        keys.append(key)

    # Return compiled list of remediation options
    return action_queue


def get_actions_for_account(account_session):

    try:
      iam_client = account_session.client('iam')
    except ClientError as err:
            log.error(
                f'Error while creating session for IAM service '
                f' - {err}'
            )

    action_queue = []

    # Get all Users in AWS Account
    users = iam_client.list_users()['Users']
    if not users:
        log.info('There are no users in this account.')
    else:

        total_users = len(users)

        log.info(
            f'Starting user loop. There are {total_users}'
            f' users to evaluate in this account.')
        log.info('---------------------------')

        for user in users:
            user_name = user['UserName']

            access_key_metadata = iam_client.list_access_keys(
                UserName=user["UserName"])['AccessKeyMetadata']

            user_actions = get_actions_for_keys(
                access_key_metadata, account_session,
                )

            action_queue += user_actions

    return action_queue
