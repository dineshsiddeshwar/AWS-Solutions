# (c) 2021 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.
# This AWS Content is provided subject to the terms of the AWS Customer Agreement available at
# https://aws.amazon.com/agreement/ or other written agreement between Customer
# and Amazon Web Services, Inc.

"""Key Action Handler.

This module provides the functions to log IAM Keys actions to CloudWatch.
"""

import json
import logging


# setup script logging
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def log_actions(action_queue, dryrun=False):
    if not action_queue:
        log.info("No actions to be taken on this account.")
        return

    for action_spec in action_queue:
        action = action_spec['action']
        key_metadata = action_spec['key']
        access_key_id = key_metadata["AccessKeyId"]
        reason = action_spec['reason'].value

        if action == 'WARN':
            log.info(
                    f"Expiring Key. Please rotate {access_key_id} before {action_spec['action_date']}"
                    f" -- {reason}")
        elif action == 'ROTATE':
            log.info(
                    f" Key {access_key_id} has been Expired. Please rotate immediately"
                    f" -- {reason}")
        elif action == 'ROTATE_AND_DELETE':
            log.info(
                f"Key {access_key_id} has been Expired and never been used. Please rotate and delete immediately"
                f" -- {reason}")