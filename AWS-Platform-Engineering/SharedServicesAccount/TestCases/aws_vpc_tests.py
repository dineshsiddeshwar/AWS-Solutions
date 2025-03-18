def aws_check_if_vpc_exists(ec2_client, vpc_cidr):
    try:
        vpc_response = ec2_client.describe_vpcs(
            Filters=[
                {
                    'Name': 'cidr',
                    'Values': [vpc_cidr]
                }
            ]
        )
        if len(vpc_response['Vpcs']) > 0:
            print("VPC found, id is {}".format(vpc_response['Vpcs'][0]['VpcId']))
            return True
        else:
            print("VPC with cidr <{}> not found".format(vpc_cidr))
            return False
    except Exception as e:
        print("Error occurred while aws_check_if_vpc_exists and error is {}".format(e))
        return False

def aws_check_if_subnet_exists(ec2_client, subnet_cidr):
    try:
        vpc_response = ec2_client.describe_subnets(
            Filters=[
                {
                    'Name': 'cidr-block',
                    'Values': [subnet_cidr]
                }
            ]
        )
        if len(vpc_response['Subnets']) > 0:
            print("Subnet found, id is {}".format(vpc_response['Subnets'][0]['SubnetId']))
            return True
        else:
            print("Subnet with cidr <{}> not found".format(subnet_cidr))
            return False
    except Exception as e:
        print("Error occurred while aws_check_if_subnet_exists and error is {}".format(e))
        return False

def aws_check_if_flowlog_created(ec2_client):
    try:
        fl_response = ec2_client.describe_flow_logs(
            Filters=[
                {
                    'Name': 'tag:Name',
                    'Values': ['platform-shared-flowlog']
                }
            ]
        )
        if len(fl_response['FlowLogs']) > 0:
            print("Flowlog found, id is {}".format(fl_response['FlowLogs'][0]['FlowLogId']))
            return True
        else:
            print("Flowlog not found")
            print("Flowlog response is {}".format(fl_response))
            return False
    except Exception as e:
        print("An error occurred while aws_check_if_platform_vpc_and_flowlog_created, error: {}".format(e))
        return False
