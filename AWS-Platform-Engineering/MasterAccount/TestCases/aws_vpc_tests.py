def aws_check_if_vpc_is_created(ec2_client, vpc_name):
    try:
        response = ec2_client.describe_vpcs(
                    Filters=[
                        {
                            'Name': 'tag:Name',
                            'Values': [vpc_name]
                        }
                    ]
                )
        if len(response['Vpcs']) > 0:
            print(response)
            return True

    except Exception as e:
        print("error occured while aws_check_if_vpc_is_created and error is {}".format(e))
        return False

def aws_check_if_internet_gateway_is_created(ec2_client, vpc_name):
    try:
        vpc_response = ec2_client.describe_vpcs(
                    Filters=[
                        {
                            'Name': 'tag:Name',
                            'Values': [vpc_name]
                        }
                    ]
                )
        if len(vpc_response['Vpcs']) > 0:
            vpc_id = vpc_response['Vpcs'][0]['VpcId']
            igw_response = ec2_client.describe_internet_gateways(
                Filters=[
                    {
                        'Name': 'attachment.vpc-id',
                        'Values': [vpc_id]
                    },
                ],
            )
            if len(igw_response['InternetGateways']) > 0:
                print(igw_response)
                return True
            else:
                return False
        else:
            return False
    except Exception as e:
        print("error occured while aws_check_if_internet_gateway_is_created and error is {}".format(e))
        return False

def aws_check_if_subnets_are_created(ec2_client, vpc_name):
    try:
        vpc_response = ec2_client.describe_vpcs(
                    Filters=[
                        {
                            'Name': 'tag:Name',
                            'Values': [vpc_name]
                        }
                    ]
                )
        if len(vpc_response['Vpcs']) > 0:
            vpc_id = vpc_response['Vpcs'][0]['VpcId']
            subnet_response = ec2_client.describe_subnets(
                Filters=[
                    {
                        'Name': 'vpc-id',
                        'Values': [vpc_id]
                    },
                ],
            )
            if len(subnet_response['Subnets']) > 0:
                print(subnet_response)
                return True
            else:
                return False
        else:
            return False
    except Exception as e:
        print("error occured while aws_check_if_subnets_are_created and error is {}".format(e))
        return False

def aws_check_if_routetable_created(ec2_client, vpc_name):
    try:
        vpc_response = ec2_client.describe_vpcs(
                    Filters=[
                        {
                            'Name': 'tag:Name',
                            'Values': [vpc_name]
                        }
                    ]
                )
        if len(vpc_response['Vpcs']) > 0:
            vpc_id = vpc_response['Vpcs'][0]['VpcId']
            routetable_response = ec2_client.describe_route_tables(
                Filters=[
                    {
                        'Name': 'vpc-id',
                        'Values': [vpc_id]
                    },
                ],
            )
            if len(routetable_response['RouteTables']) > 0:
                print(routetable_response)
                return True
            else:
                return False
        else:
            return False
    except Exception as e:
        print("error occured while aws_check_if_routetable_created and error is {}".format(e))
        return False
    
def aws_check_if_routetable_is_associated(ec2_client, vpc_name):
    try:
        vpc_response = ec2_client.describe_vpcs(
                    Filters=[
                        {
                            'Name': 'tag:Name',
                            'Values': [vpc_name]
                        }
                    ]
                )
        if len(vpc_response['Vpcs']) > 0:
            vpc_id = vpc_response['Vpcs'][0]['VpcId']
            rt_association_response = ec2_client.describe_route_tables(
                Filters=[
                    {
                        'Name': 'vpc-id',
                        'Values': [vpc_id]
                    },
                ],
            )
            if len(rt_association_response['RouteTables'][0]['Associations']) > 0:
                print(rt_association_response)
                return True
            else:
                return False
        else:
            return False
    except Exception as e:
        print("error occured while aws_check_if_routetable_is_associated and error is {}".format(e))
        return False
           
def aws_check_if_flowlogs_is_enabled(ec2_client, vpc_name):
    try:
        vpc_response = ec2_client.describe_vpcs(
                    Filters=[
                        {
                            'Name': 'tag:Name',
                            'Values': [vpc_name]
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
                print(vpc_fl_response)
                return True
            else:
                return False
        else:
            return False
    except Exception as e:
        print("error occured while aws_check_if_flowlogs_is_enabled and error is {}".format(e))
        return False

def aws_check_if_security_group_is_created(ec2_client, sg_name):
    try:
        sg_response = ec2_client.describe_security_groups(
            Filters=[
                {
                    'Name': 'group-name',
                    'Values': [sg_name]
                },
            ],
        )
        if len(sg_response['SecurityGroups']) > 0:
            print(sg_response)
            return True
        else:
            return False
    except Exception as e:
        print("error occured while aws_check_if_security_group_is_createdsss and error is {}".format(e))
        return False

def aws_check_if_elatic_ip_is_associated(ec2_client, elastic_ip_name):
    try:
        response = ec2_client.describe_addresses(
            Filters=[
                {
                    'Name': 'tag:Name',
                    'Values': [
                        elastic_ip_name,
                    ]
                },
                {
                    'Name': 'domain',
                    'Values': [
                        'vpc',
                    ],
                },
            ]
        )
        if len(response['Addresses']) > 0:
            print(response)
            return True
        else:
            return False
    except Exception as e:
        print("error occured while aws_check_if_elatic_ip_is_associated and error is {}".format(e))
        return False

def aws_check_if_nat_gateway_is_created(ec2_client, nat_gateway_name):
    try:
        nat_response = ec2_client.describe_nat_gateways(
            Filters=[
                {
                    'Name': 'tag:Name',
                    'Values': [
                        nat_gateway_name,
                    ]
                }
            ]
        )
        if len(nat_response['NatGateways']) > 0:
            print(nat_response)
            return True
        else:
            return False
    except Exception as e:
        print("error occured while aws_check_if_nat_gateway_is_created and error is {}".format(e))
        return False