def aws_check_if_sg_exists(ec2_client, name):
    try:
        sg_response = ec2_client.describe_security_groups(
            Filters=[
                {
                    'Name': 'group-name',
                    'Values': [name]
                }
            ]
        )
        if len(sg_response['SecurityGroups']) > 0:
            print("SecurityGroup found, id is {}".format(sg_response['SecurityGroups'][0]['GroupId']))
            return True
        else:
            print("SecurityGroup with name <{}> not found".format(name))
            return False
    except Exception as e:
        print("Error occurred while aws_check_if_vpc_exists and error is {}".format(e))
        return False
