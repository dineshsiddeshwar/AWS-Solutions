"""
This module is used to Launch EC2 for the Latest AMI
"""
import logging
import boto3


class LaunchEC2(object):
    """
    # Class: LaunchEC2
    # Description: Launches EC2 for the provided ami_id
    """

    def __init__(self, event, context):
        self.event = event
        self.context = context
        try:
            # get relevant input params from event
            self.ami_id = event['ami_id']
            self.ami_name = event['ami_name']
            self.instancetype_t2micro = 't2.micro'

        except Exception as exception:
            self.reason_data = "Missing required property %s" % exception
            print("ERROR Self Launch EC2", exception)

    def launch_ec2_ins(self):
        """
        The following method is used to check type of ami & call launch ec2 instance.
        """
        res_dict = {}
                                 
        try:
            if(self.ami_name == 'RHEL-7.7*'):
                instancetype = self.instancetype_t2micro
                userdata = '''#!/bin/bash
rhel7_SSM()
{
ssm=`rpm -qa|grep -c amazon-ssm-agent`
folderdate=$(date +%Y/%m/%d)
if [ $ssm -eq 0 ]
then
    #Retrieve Region
    curl --noproxy "*" http://169.254.169.254/latest/meta-data/placement/availability-zone -o /root/availability-zone
    REGION=`cat /root/availability-zone|cut -d"-" -f1,2`
    case "$REGION" in
    "us-east")
        curl https://s3.amazonaws.com/ec2-downloads-windows/SSMAgent/latest/linux_amd64/amazon-ssm-agent.rpm -o /root/amazon-ssm-agent.rpm;
    ;;
    esac
    rpm -i /root/amazon-ssm-agent.rpm
    systemctl daemon-reload
    systemctl stop amazon-ssm-agent
    systemctl start amazon-ssm-agent
    logger -t SSM -s 2>/dev/console "[amazon-ssm-agent Installed Successfully]"
    cd /root/
    rm -f amazon-ssm-agent.rpm
    /bin/rm /root/availability-zone
    yum install python3 -y
    pip3 install awscli
else
    systemctl stop amazon-ssm-agent
    systemctl start amazon-ssm-agent
    echo "amazon-ssm-agent already installed"
    logger -t SSM -s 2>/dev/console "[amazon-ssm-agent already installed]"
fi
}
if [ -f /etc/os-release ]
then
    OSTYPE=`cat /etc/os-release |grep  -w ID |awk -F "=" '{print $2}'`
    if [ $OSTYPE == '"rhel"' ]
    then
        rhel7_SSM
    fi
fi
'''
            elif(self.ami_name == 'RHEL-8*'):
                instancetype = self.instancetype_t2micro
                userdata = '''#!/bin/bash
rhel8_SSM()
{
ssm=`rpm -qa|grep -c amazon-ssm-agent`
folderdate=$(date +%Y/%m/%d)
if [ $ssm -eq 0 ]
then
    #Retrieve Region
    curl --noproxy "*" http://169.254.169.254/latest/meta-data/placement/availability-zone -o /root/availability-zone
    REGION=`cat /root/availability-zone|cut -d"-" -f1,2`
    case "$REGION" in
    "us-east")
        curl https://s3.amazonaws.com/ec2-downloads-windows/SSMAgent/latest/linux_amd64/amazon-ssm-agent.rpm -o /root/amazon-ssm-agent.rpm;
    ;;
    esac
    rpm -i /root/amazon-ssm-agent.rpm
    systemctl daemon-reload
    systemctl stop amazon-ssm-agent
    systemctl start amazon-ssm-agent
    logger -t SSM -s 2>/dev/console "[amazon-ssm-agent Installed Successfully]"
    cd /root/
    rm -f amazon-ssm-agent.rpm
    /bin/rm /root/availability-zone
    yum install python3 -y
    pip3 install awscli
else
    systemctl stop amazon-ssm-agent
    systemctl start amazon-ssm-agent
    echo "amazon-ssm-agent already installed"
    logger -t SSM -s 2>/dev/console "[amazon-ssm-agent already installed]"
fi
}
if [ -f /etc/os-release ]
then
    OSTYPE=`cat /etc/os-release |grep  -w ID |awk -F "=" '{print $2}'`
    if [ $OSTYPE == '"rhel"' ]
    then
        rhel8_SSM
    fi
fi
'''
            elif ((self.ami_name == 'amzn2-ami-hvm*') or
                  (self.ami_name == 'amzn2-ami-ecs-hvm-*') or
                  (self.ami_name == 'amazon-eks-node-*')):
                instancetype = self.instancetype_t2micro
                userdata = '''#!/bin/bash

amaz_SSM()
{
ssm=`rpm -qa|grep -c amazon-ssm-agent`
folderdate=$(date +%Y/%m/%d)
if [ $ssm -eq 0 ]
then
    #Retrieve Region
    curl --noproxy "*" http://169.254.169.254/latest/meta-data/placement/availability-zone -o /root/availability-zone
    REGION=`cat /root/availability-zone|cut -d"-" -f1,2`
    case "$REGION" in
    "us-east")
        curl https://s3.amazonaws.com/ec2-downloads-windows/SSMAgent/latest/linux_amd64/amazon-ssm-agent.rpm -o /root/amazon-ssm-agent.rpm;
    ;;
    esac
    rpm -i /root/amazon-ssm-agent.rpm
    systemctl daemon-reload
    systemctl stop amazon-ssm-agent
    systemctl start amazon-ssm-agent
    logger -t SSM -s 2>/dev/console "[amazon-ssm-agent Installed Successfully]"
    cd /root/
    rm -f amazon-ssm-agent.rpm
    /bin/rm /root/availability-zone
    yum install python3 -y
    pip3 install awscli
else
    yum install python3 -y
    yum install unzip -y
    pip3 install awscli
    systemctl stop amazon-ssm-agent
    systemctl start amazon-ssm-agent
    echo "amazon-ssm-agent already installed"
    logger -t SSM -s 2>/dev/console "[amazon-ssm-agent already installed]"
fi
}
if [ -f /etc/os-release ]
then
    OSTYPE=`cat /etc/os-release |grep  -w ID |awk -F "=" '{print $2}'`
    if [ $OSTYPE == '"amzn"' ]
    then
        amaz_SSM
    fi
fi
'''
            elif ((self.ami_name == 'Windows_Server-2016-English-Full-Base*') or (
                self.ami_name == 'Windows_Server-2019-English-Full-Base*') or (
                    self.ami_name == 'Windows_Server-2016-English-Full-ECS_Optimized-*') or (
                    self.ami_name == 'Windows_Server-2019-English-Full-ECS_Optimized-*')):
                userdata = ''
                instancetype = 't3.medium'

            elif (self.ami_name == 'ubuntu/images/hvm-ssd/ubuntu-bionic-*'):
                instancetype = 't2.medium'
                userdata = '''#!/bin/bash
apt-get update
apt install python3 -y
apt install python3-pip -y
pip3 install awscli
'''

            else:
                print('Unknown AMI {}'.format(self.ami_name))

            ec2 = boto3.resource('ec2', region_name='us-east-1')
            ec2_client = boto3.client('ec2', region_name='us-east-1')
            ssm_client = boto3.client('ssm')

            sg = ec2_client.describe_security_groups()
            for each_sg in sg['SecurityGroups']:
                if(each_sg['GroupName'] == 'platform_CIS-Security-Group'):
                    vpc_id = each_sg['VpcId']
                    sg_id = each_sg['GroupId']

            subnet = ec2_client.describe_subnets()
            for each_subnet in subnet['Subnets']:
                if each_subnet['VpcId'] == vpc_id:
                    subnet_id = each_subnet['SubnetId']

            acc_number = ssm_client.get_parameter(Name='master_account')
            acc_number = (acc_number['Parameter']['Value'])
            instance_profile_arn = "arn:aws:iam::{}:instance-profile/platform-cis-score-InstanceRole".format(
                acc_number)

            print(sg_id, vpc_id, subnet_id, instance_profile_arn)

            instance = ec2.create_instances(
                ImageId=self.ami_id,
                UserData=userdata,
                InstanceType=instancetype,
                MinCount=1,
                MaxCount=1,
                KeyName='CIS-Benchmark-EC2instance',
                SubnetId=subnet_id,
                IamInstanceProfile={
                    'Arn': instance_profile_arn
                },
                SecurityGroupIds=[sg_id])

            res_dict['ami_id'] = self.ami_id
            res_dict['ami_name'] = self.ami_name
            res_dict['Instance_ID'] = instance[0].id

            return res_dict

        except Exception as exception:
            self.reason_data = "Launch EC2 %s" % exception
            print("ERROR Launch EC2", exception)
            return exception


def lambda_handler(event, context):
    """
    Lamda handler calls the function that lauches an ec2 instance for each ami
    """
    try:
        result_value = {}
        result_value.update(event)
        print("Received an event {}".format(event))
        launch_ins = LaunchEC2(event, context)
        output_value = launch_ins.launch_ec2_ins()
        print("Output of the function : " + str(output_value))
        result_value.update(output_value)
        return result_value
    except Exception as exception:
        print("Error in Lambda Handler", exception)
        return exception
