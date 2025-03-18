import boto3
import os
import json
import logging

# setup script logging
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class TriggerBackupPlan:
    def __init__(self, event, context):

        self.backup_client = client = boto3.client('backup')
        self.report_plan = os.environ["REPORT_PLAN"]


    def trigger_backup_plan(self):
        
        try: 
            response = self.backup_client.start_report_job(
                    ReportPlanName=self.report_plan
            )
            log.info("Backup report has been generated successfully.")
        except Exception as error:
            log.error(f"Found issues while generating backup report. Please check the logs. {error}")



# main Python Function, parses events sent to lambda
def lambda_handler(event, context):

    trigger_backup_plan = TriggerBackupPlan(event, context)
    trigger_backup_plan.trigger_backup_plan()
    


