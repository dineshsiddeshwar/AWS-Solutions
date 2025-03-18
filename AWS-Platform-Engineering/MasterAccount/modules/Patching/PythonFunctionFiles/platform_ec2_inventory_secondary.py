import random
import boto3
import logging
import json
import csv
import os
import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3')
organizations_client = boto3.client('organizations')

year = str(datetime.datetime.today().year)
month = str(datetime.datetime.today().month)
day = str(datetime.datetime.today().day)

class CheckProfileEC2(object):
    def __init__(self, event):
        global session
        session = boto3.session.Session()
        # get approved regions
        try:
            inventory_bucket_ssm_name = os.environ['INVENTORY_BUCKET_SSM_NAME']            
            self.account_type = str(event['AccountType'])
            self.ssm_client = session.client('ssm')
            if 'private' in self.account_type:
                private_regions = self.ssm_client.get_parameter(Name='whitelisted_regions_private')
                self.approved_regions = (private_regions['Parameter']['Value']).split(',')
            else:
                public_regions = self.ssm_client.get_parameter(Name='whitelisted_regions_public')
                self.approved_regions = (public_regions['Parameter']['Value']).split(',')
            ssm_response = self.ssm_client.get_parameter(Name=inventory_bucket_ssm_name)
            self.consolidated_compliance_bucket_name = ssm_response['Parameter']['Value']                                         
        except Exception as exception:
            print("unable to init")
            raise Exception(str(exception))

        # assume role in child account
        try:
            self.account_number = str(event['accountNumber'])
            self.account_name = organizations_client.describe_account(AccountId=self.account_number)['Account']['Name']
            secondary_rolearn = "arn:aws:iam::{}:role/AWSControlTowerExecution".format(self.account_number)
            secondary_session_name = "SecondarySession-" + str(random.randint(1, 100000))
            self.sts_client = session.client('sts')
            # Logging to child account.
            secondaryRoleCreds = self.sts_client.assume_role(RoleArn=secondary_rolearn,
                                                             RoleSessionName=secondary_session_name)
            credentials = secondaryRoleCreds.get('Credentials')
            accessKeyID = credentials.get('AccessKeyId')
            secretAccessKey = credentials.get('SecretAccessKey')
            sessionToken = credentials.get('SessionToken')
            self.assumeRoleSession = boto3.session.Session(accessKeyID, secretAccessKey, sessionToken)
            logger.info('Assumed in role in child account {}'.format(self.account_number))
        except Exception as exception:
            print("failed to assume role in child account {}".format(self.account_number))
            raise Exception(str(exception))

    def describe_ec2(self): 
        # decribe ec2 list
        instance_id = []
        ImageId= []
        InstanceType = []
        SubnetId = []
        VpcId = []
        LaunchTime = []
        State = []
        PrivateIpAddress = []
        PublicIpAddress = []
        SecurityGroups =[]
        key = []        
        response = self.ec2_client.describe_instances(
                        DryRun=False,
                        MaxResults=1000
                    )        
        while True:
            instance_list_tmp = [r['Instances'] for r in response['Reservations']]
            instance_list = [val for sublist in instance_list_tmp for val in sublist]            
            for i in instance_list:
                instance_id.append(i['InstanceId'])
                ImageId.append(i['ImageId'])
                InstanceType.append(i['InstanceType'])
                try:
                    SubnetId.append(i['SubnetId'])
                    VpcId.append(i['VpcId'])
                    PrivateIpAddress.append(i['PrivateIpAddress'])
                    SecurityGroups.append(i['SecurityGroups'])                    
                except:
                    SubnetId.append('no subnet')
                    VpcId.append('no vpc')
                    PrivateIpAddress.append('no ip address')
                    SecurityGroups.append(' no security group')
                LaunchTime.append(i['LaunchTime'].date())
                State.append(i['State'])
                try:
                    key.append(i['Tags'])
                except:
                    key.append('no tags')
            if 'NextToken' in response:
                NextToken = response['NextToken']
                response = self.ec2_client.describe_instances(
                    DryRun=False,
                    MaxResults=1000,
                    NextToken=NextToken
                )
            else:
                break

        return instance_id,ImageId,InstanceType,SubnetId,VpcId,LaunchTime,State,PrivateIpAddress,SecurityGroups,key

    def describe_ec2_instances(self):
        instance_ids= []
        ImageIds= []
        InstanceTypes = []
        SubnetIds = []
        VpcIds = []
        LaunchTimes = []
        States = []
        PrivateIpAddresss = []
        SecurityGroups =[]
        key = []
        for region in self.approved_regions:
            self.iam_client = self.assumeRoleSession.client('iam',region_name=region)
            self.ec2_client = self.assumeRoleSession.client('ec2',region_name=region)
            instance_id_tmp,ImageIds_tmp,InstanceType_tmp,SubnetId_tmp,VpcId_tmp,LaunchTime_tmp,State_tmp,PrivateIpAddress_tmp,SecurityGroups_tmp,key_tmp= self.describe_ec2()
            if len(instance_id_tmp) !=0 :
                instance_ids.append(instance_id_tmp)
                ImageIds.append(ImageIds_tmp)
                InstanceTypes.append(InstanceType_tmp)
                SubnetIds.append(SubnetId_tmp)
                VpcIds.append(VpcId_tmp)
                LaunchTimes.append(LaunchTime_tmp)
                States.append(State_tmp)
                PrivateIpAddresss.append(PrivateIpAddress_tmp)
                SecurityGroups.append(SecurityGroups_tmp)
                key.append(key_tmp)

        return instance_ids,ImageIds,InstanceTypes,SubnetIds,VpcIds,LaunchTimes,States,PrivateIpAddresss,SecurityGroups,key

    def upload_consolidated_file(self,payload):
        try:
            data = []
            data1 = []
            for i in range (0,len(payload["instance_id"])):                
                data.append([self.account_name,self.account_number,self.account_type,payload["instance_id"][i],payload["ImageId"][i],payload["InstanceType"][i],payload["SubnetId"][i],payload["VpcId"][i],payload["LaunchTime"][i],payload["State"][i],payload["PrivateIpAddress"][i],payload["SecurityGroups"][i],payload["Tags"][i]])
            for i in data:
                for j in range (len(i[3])):
                    data1.append([i[0],i[1],i[2],i[3][j],i[4][j],i[5][j],i[6][j],i[7][j],i[8][j],i[9][j]['Name'],i[10][j],i[11][j],i[12][j]])
            consolidated_file_name = "AWS_at_shell_" + self.account_number + ".csv"
            file_path = "/tmp/" + consolidated_file_name
            key = '/'.join([year,month,day,consolidated_file_name])
            fields = ['account_name','account_id','ouname', 'instance_id','ImageId','InstanceType','SubnetId','VpcId','LastLaunchedDate','State','PrivateIpAddress','SecurityGroups','Tags']
            with open(file_path, 'w', newline='\n') as f:
                # using csv.writer method from CSV package
                write = csv.writer(f,delimiter="|")
                write.writerow(fields)
                write.writerows(data1)
                f.close()
                print("Trying to upload consolidated file")
                response = s3_client.upload_file(file_path, self.consolidated_compliance_bucket_name, key)
                print("Consolidated file uploaded successfully")
        except Exception as e:
            logger.info('File uploaded failed {}'.format(str(e)))
            raise Exception(str(e))

def lambda_handler(event,context):
    profile_ec2_object = CheckProfileEC2(event)
    instance_ids,ImageIds,InstanceTypes,SubnetIds,VpcIds,LaunchTimes,States,PrivateIpAddresss,SecurityGroups,key = profile_ec2_object.describe_ec2_instances()
    if len(instance_ids) != 0:
        d = {'instance_id':instance_ids , 'ImageId':ImageIds,'InstanceType': InstanceTypes,'SubnetId': SubnetIds, 'VpcId':VpcIds,'LaunchTime': LaunchTimes,'State':States,'PrivateIpAddress':PrivateIpAddresss,'SecurityGroups':SecurityGroups,'Tags':key}
        profile_ec2_object.upload_consolidated_file(d)
        return {
            'statusCode': 200,
            'body': json.dumps('File uploaded successfully')
        }
    else:
        return {
            'statusCode': 200,
            'body': json.dumps('No instances found in the account')
        }

