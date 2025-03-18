def aws_check_if_platform_vpc_and_flowlog_created(ec2_client):
    try:
        vpc_response = ec2_client.describe_vpcs(
                    Filters=[
                        {
                            'Name': 'tag:Name',
                            'Values': ['platform-VPC']
                        }
                    ]
                )
        if len(vpc_response['Vpcs']) > 0:
            vpc_id = vpc_response['Vpcs'][0]['VpcId']
            vpc_fl_response = ec2_client.describe_flow_logs(
                Filters=[
                    {
                        'Name': 'resource-id',
                        'Values': [vpc_id]
                    },
                ],
            )
            if len(vpc_fl_response['FlowLogs']) > 0:
                return True
            else:
                return False
        else:
            return False
    except Exception as e:
        print("error occured while aws_check_if_platform_vpc_and_flowlog_created and error is {}".format(e))
        return False
