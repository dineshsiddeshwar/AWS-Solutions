"""
This module is used to Get CIS Report for the latest AMI
"""
import boto3


class GetCISReport(object):
    """
    # Class: GetCISReport
    # Description: Check GetCISReport for the latest AMI
    """

    def __init__(self, event, context):
        self.event = event
        self.context = context
        try:
            # get relevant input params from event
            global session
            self.ami_id = event['ami_id']
            self.ami_name = event['ami_name']
            self.instanceid = event['Instance_ID']
            session = boto3.session.Session()

        except Exception as exception:
            self.reason_data = "Missing required property %s" % exception
            print("ERROR Self GetCISReport", exception)

    def get_cis_report(self):
        """
        The following method is used to get the cis report for the latest AMI.
        """
        res_dict = {}
        try:
            ssm_client = session.client('ssm')
            s3_name = ssm_client.get_parameter(
                Name='platform_cis_cat_pro_tools')
            s3_name = (s3_name['Parameter']['Value'])
            print(s3_name)

            if (self.ami_name == 'Windows_Server-2016-English-Full-Base*'):
                document_name = 'AWS-RunPowerShellScript'
                commands_cmd = [
                    "Copy-S3Object -BucketName {} -Key Windows-2016_CIS_Report_PS.ps1 -LocalFolder C:\\Windows\\Temp\\".format(
                        s3_name),
                    "Powershell.exe -File C:\Windows\Temp\Windows-2016_CIS_Report_PS.ps1"
                ]
                print(commands_cmd)

            elif (self.ami_name == 'Windows_Server-2016-English-Full-ECS_Optimized-*'):
                document_name = 'AWS-RunPowerShellScript'
                commands_cmd = [
                    "Copy-S3Object -BucketName {} -Key Windows-2016_ECS_Optimized_CIS_Report_PS.ps1 -LocalFolder C:\\Windows\\Temp\\".format(
                        s3_name),
                    "Powershell.exe -File C:\Windows\Temp\Windows-2016_ECS_Optimized_CIS_Report_PS.ps1"
                ]
                print(commands_cmd)

            elif (self.ami_name == 'Windows_Server-2019-English-Full-Base*'):
                document_name = 'AWS-RunPowerShellScript'
                commands_cmd = [
                    "Copy-S3Object -BucketName {} -Key Windows-2019_CIS_Report_PS.ps1 -LocalFolder C:\\Windows\\Temp\\".format(
                        s3_name),
                    "Powershell.exe -File C:\Windows\Temp\Windows-2019_CIS_Report_PS.ps1"
                ]
                print(commands_cmd)

            elif (self.ami_name == 'Windows_Server-2019-English-Full-ECS_Optimized-*'):
                document_name = 'AWS-RunPowerShellScript'
                commands_cmd = [
                    "Copy-S3Object -BucketName {} -Key Windows-2019_ECS_Optimized_CIS_Report_PS.ps1 -LocalFolder C:\\Windows\\Temp\\".format(
                        s3_name),
                    "Powershell.exe -File C:\Windows\Temp\Windows-2019_ECS_Optimized_CIS_Report_PS.ps1"
                ]
                print(commands_cmd)

            elif ((self.ami_name == 'RHEL-7.7*') or (self.ami_name == 'RHEL-8*') or (
                    self.ami_name == 'amzn2-ami-hvm*') or (self.ami_name == 'ubuntu/images/hvm-ssd/ubuntu-bionic-*')):
                print("Enternet RHEL-")
                linux_cmd = "cd /var/tmp && aws s3 cp  s3://{}/CIS-installation-script-for-linux.sh . && chmod +x CIS-installation-script-for-linux.sh && ./CIS-installation-script-for-linux.sh && sleep 50s".format(
                    s3_name)
                document_name = 'AWS-RunShellScript'
                commands_cmd = [linux_cmd]
                print(commands_cmd)

            elif (self.ami_name == 'amzn2-ami-ecs-hvm-*'):
                print("Enternet amzn2-ami-ecs-hvm-*")
                linux_cmd_ecs = "cd /var/tmp && aws s3 cp  s3://{}/CIS-installation-script-for-linux-ecs.sh . && chmod +x CIS-installation-script-for-linux-ecs.sh && ./CIS-installation-script-for-linux-ecs.sh && sleep 50s".format(
                    s3_name)
                document_name = 'AWS-RunShellScript'
                commands_cmd = [linux_cmd_ecs]
                print(commands_cmd)

            elif (self.ami_name == 'amazon-eks-node-*'):
                print("Enternet amazon-eks-node-*")
                linux_cmd_eks = "cd /var/tmp && aws s3 cp  s3://{}/CIS-installation-script-for-linux-eks.sh . && chmod +x CIS-installation-script-for-linux-eks.sh && ./CIS-installation-script-for-linux-eks.sh && sleep 50s".format(
                    s3_name)
                document_name = 'AWS-RunShellScript'
                commands_cmd = [linux_cmd_eks]
                print(commands_cmd)

            else:
                print('Unknown AMI found {}'.format(self.ami_name))
            ssm_client.send_command(
                InstanceIds=[self.instanceid],
                DocumentName=document_name,
                Parameters={
                    "commands": commands_cmd
                },
                CloudWatchOutputConfig={
                    'CloudWatchLogGroupName': '/aws/lambda/CIS-Get_CIS_Report_Using_SSM',
                    'CloudWatchOutputEnabled': True
                }
            )
            res_dict['ami_id'] = self.ami_id
            res_dict['ami_name'] = self.ami_name
            res_dict['Instance_ID'] = self.instanceid
            return res_dict

        except Exception as exception:
            self.reason_data = "GetCISReport %s" % exception
            return exception


def lambda_handler(event, context):
    """
    This lambda handler calls the fucntion to get CIS reprot for the latest AMI
    """
    try:
        result_value = {}
        result_value.update(event)
        print("Received an event {}".format(event))
        reporting_status = GetCISReport(event, context)
        output_value = reporting_status.get_cis_report()
        print("Output of the function : " + str(output_value))
        result_value.update(output_value)
        return result_value
    except Exception as exception:
        print("Error in Lambda Handler", exception)
        return exception