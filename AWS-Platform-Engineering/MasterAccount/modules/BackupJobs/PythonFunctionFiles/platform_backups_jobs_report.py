
import boto3
import os
import json
import datetime
import csv

backup_client = boto3.client('backup')
s3_client = boto3.client('s3')
year = str(datetime.datetime.today().year)
month = str(datetime.datetime.today().month)
day = str(datetime.datetime.today().day)

yesterday = datetime.datetime.now() - datetime.timedelta(1)
report_year = yesterday.year
report_month = yesterday.month
report_day = yesterday.day

class BackupJobs(object):

    def __init__(self, event, context):
        try:
            self.bucket_name = os.environ['BACKUP_JOBS_BUCKET_NAME']            
            print("init complete")
        except Exception as exception:
            print("unable to init")
            raise Exception(str(exception))

    def backup_list(self):
        response = backup_client.list_backup_jobs(
            ByCreatedAfter=datetime.datetime(report_year, report_month, report_day),
            ByAccountId='*'
        )
        results = response["BackupJobs"]
        while "NextToken" in response:
            response = backup_client.list_backup_jobs(
                ByCreatedAfter=datetime.datetime(report_year, report_month, report_day),
                ByAccountId='*',
                NextToken=response['NextToken']
            )            
            results.extend(response["BackupJobs"])
        return results
            
    def upload_file(self,data):
        file_name = "backup_jobs.csv"
        file_path = "/tmp/" + file_name
        key = '/'.join([year,month,day,file_name])
        with open(file_path, 'w') as file:
            write = csv.writer(file,delimiter="|")
            write.writerow(["AccountId", "BackupJobId", "BackupVaultName", "BackupVaultArn", "ResourceArn", "State", "PercentDone", "BackupSizeInBytes", "CreatedBy", "CreationDate", "StartBy", "StatusMessage", "ResourceType"])
            for x in data:
                if 'StatusMessage' in x:
                    status_message = x["StatusMessage"]
                else:
                    status_message = 'No status message'
                if 'BackupSizeInBytes' in x:
                    backup_size = str(x["BackupSizeInBytes"])
                else:
                    backup_size = 'No backup size'
                write.writerow([x["AccountId"],
                            x["BackupJobId"],
                            x["BackupVaultName"],
                            x["BackupVaultArn"],
                            x["ResourceArn"],
                            x["State"],
                            x["PercentDone"],
                            backup_size,
                            str(x["CreatedBy"]),
                            str(x["CreationDate"]),
                            str(x["StartBy"]),
                            status_message,
                            x["ResourceType"]])           
            file.close()
        try:
            print("Trying to upload consolidated file")
            response = s3_client.upload_file(file_path, self.bucket_name, key)
            print("Consolidated file uploaded successfully")
        except Exception as e:
            print('File uploaded failed {}'.format(str(e)))
            raise Exception(str(e))

    def get_backups(self):
        results = self.backup_list()
        self.upload_file(results)

def lambda_handler(event, context):
    backup_jobs = BackupJobs(event, context)
    results = backup_jobs.backup_list()
    if results:
        backup_jobs.upload_file(results)
    