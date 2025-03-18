def aws_check_if_backup_vault_created(Backup, BackupVaultName):
    try:
        response = Backup.describe_backup_vault(
                                BackupVaultName=BackupVaultName
                            )
        print(response['BackupVaultArn'])
    except Exception as e:
        print("error occured while aws_check_if_backup_vault_created and error is {}".format(e))
        return False
    else:
         return True
    
def aws_check_if_backup_sns_topic_created(SNS,Region,AccountNumber, SNSTopicName):
    try:
        SNSName = "arn:aws:sns:"+Region+":"+AccountNumber+":"+SNSTopicName
        response = SNS.get_topic_attributes(
                        TopicArn=SNSName
                    )
        print(response['Attributes'])
    except Exception as e:
        print("error occured while aws_check_if_backup_sns_topic_created and error is {}".format(e))
        return False
    else:
         return True
    
def aws_check_if_backup_vault_notifications_created(Backup,BackupVaultName):
    try:
        response = Backup.get_backup_vault_notifications(
                        BackupVaultName=BackupVaultName
                    )
        print(response['BackupVaultEvents'])
    except Exception as e:
        print("error occured while aws_check_if_backup_vault_notifications_created and error is {}".format(e))
        return False
    else:
         return True