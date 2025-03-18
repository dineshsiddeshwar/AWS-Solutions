import boto3
import logging

#CLouwatch logger variables
logger = logging.getLogger()
logger.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
logger.addHandler(CH)


SUCCESS = "SUCCESS"
FAILED = "FAILED"



def get_vpc_cidrs(vpcid, session):
    """
    Desription: This function return cidrs associated with vpc
    """
    try:
        logger.info("Inside describe vpc")
        cidrs = []
        vpc_res = session.describe_vpcs(VpcIds=[vpcid])
        for association in vpc_res["Vpcs"][0]["CidrBlockAssociationSet"]:
            cidrs.append(association["CidrBlock"])
        return cidrs

    except Exception as ex:
        logger.error("There is something wrong in describing cidr. {0}".format(ex))
        return False


def modify_rule(sec_id, rule_id, cidrs, session, protocol, fromport, toport, cidrip, ipvsix):
    """
    Desription: This function modifys the sec rule to vpc cidr
    """
    try:
        logger.info("Inside modify rule")
        rule_dict = {}
        logger.info("Checking {0} from port and {1} ToPort and IPV4 CIDR attached is {2}".format(fromport,toport,cidrip))
        if not ipvsix:
            try:
                temp_rule = {
                            'SecurityGroupRuleId': rule_id,
                            'SecurityGroupRule': {
                            'IpProtocol': protocol,
                            'FromPort': fromport,
                            'ToPort': toport,
                            'CidrIpv4': cidrs[0],
                            'Description': 'VPC CIDR'
                        }
                        }
                sg_rule_res = session.modify_security_group_rules(
                                                    GroupId=sec_id,
                                                    SecurityGroupRules=[
                                                        temp_rule])
            except Exception as ex:
                print(ex)
                if "InvalidPermission.Duplicate" in str(ex):
                    print("There is already sg rule exists")
                    sg_res = session.revoke_security_group_ingress(
                                                        GroupId=sec_id,
                                                        IpPermissions=[
                                                            {
                                                                'FromPort': fromport,
                                                                'IpProtocol': protocol,
                                                                'IpRanges': [
                                                                    {
                                                                        'CidrIp': cidrip
                                                                    }
                                                                ],
                                                                'ToPort': toport,
                                                            }
                                                        ]
                                                    )
                    sg_rule_res = True
                elif "InvalidPermission.NotFound" in str(ex):
                    print("Seems like rule is already revoked.")
                    sg_rule_res = True

            if sg_rule_res:
                print("There were more than one CIDR attached to the VPC")
                if len(cidrs) > 1:
                    for i in range(1,len(cidrs)):
                        try:
                            sg_status = session.authorize_security_group_ingress(
                                                        GroupId=sec_id,
                                                        IpPermissions=[
                                                            {
                                                                'FromPort': fromport,
                                                                'IpProtocol': protocol,
                                                                'IpRanges': [
                                                                    {
                                                                        'CidrIp': cidrs[i],
                                                                        'Description': 'VPC CIDR'
                                                                    }
                                                                ],
                                                                'ToPort': toport,
                                                            }
                                                        ]
                                                    )
                        except Exception as ex:
                            if "InvalidPermission.Duplicate" in str(ex):
                                print("Rule already exists. Hence skipping")
                                sg_status = True
                        if sg_status:
                            print("Ingress rule added ")
                else:
                    logger.info("Nothing to update")
        else:
            logger.info("Recieved the IPv6 internet CIDR. Hence Completely removing it.")
            sg_res = session.revoke_security_group_ingress(
                                                        GroupId=sec_id,
                                                        IpPermissions=[
                                                            {
                                                                'FromPort': fromport,
                                                                'IpProtocol': protocol,
                                                                'Ipv6Ranges': [
                                                                    {
                                                                        'CidrIpv6': cidrip
                                                                    }
                                                                ],
                                                                'ToPort': toport,
                                                            }
                                                        ]
                                                    )
            
        return True
    except Exception as ex:
        logger.error("There is something wrong in Mdifying the rule. {0}".format(ex))
        return False


def lambda_handler(event, context):
    """
    Description: This lambda will remove the 0.0.0.0/0 CIDR for all the non web ports
    event example:- {
    "sec_id" : "sec-ikkalsa",
    "region" : "us-east-1",
    "accountid": "1234567"
    }
    """
    try:
        logger.info("Inside lambda handler and Event recieved is :- {0}".format(event))
        secgroup_id = event["sec_id"]
        region = event["region"]
        account_id = event["accountid"]
        sts_client = boto3.client('sts')
        role_arn = "arn:aws:iam::"+account_id+":role/HIS-236-ics-vpcremediation"
        assumed_role_object = sts_client.assume_role(
                            RoleArn=role_arn,
                            RoleSessionName="236_Public_SG_remediation")
        credentials = assumed_role_object['Credentials']
        session_client = boto3.session.Session(
                                        aws_access_key_id=credentials['AccessKeyId'],
                                        aws_secret_access_key=credentials['SecretAccessKey'],
                                        aws_session_token=credentials['SessionToken']
                                    )
        logger.info("Child session established.")
        ec2_child_client = session_client.client('ec2', region_name=region)
        sg_response = ec2_child_client.describe_security_groups(GroupIds=[secgroup_id])
        ip_all = ['0.0.0.0']
        allow_all = '-1'
        web_ports = [80,443]
        ipsix_all = "::/"
        print("Security Group Response:- {}",sg_response)
        if sg_response:
            if "Tags" in sg_response["SecurityGroups"][0].keys():
                for tag in sg_response["SecurityGroups"][0]["Tags"]:
                    if tag["Key"] == "Exception" and tag["Value"] == "yes":
                        logger.info("This security group is an exception . Hence no remediating")
                        return SUCCESS
            
            vpc_id = sg_response["SecurityGroups"][0]["VpcId"]
            cidr_list = get_vpc_cidrs(vpc_id, ec2_child_client)
            if cidr_list:
                rule_res = ec2_child_client.describe_security_group_rules(
                                                                    Filters=[
                                                                        {
                                                                            'Name': 'group-id',
                                                                            'Values': [sg_response["SecurityGroups"][0]["GroupId"]
                                                                            ]}])
                print("Security Group rules:- {}",rule_res)
                for rules in rule_res["SecurityGroupRules"]:
                    if not rules["IsEgress"] and "ReferencedGroupInfo" not in rules.keys() and "CidrIpv4" in rules.keys() and "PrefixListId" not in rules.keys():
                        if (rules["FromPort"] not in web_ports or rules["ToPort"] not in web_ports) and ( rules["CidrIpv4"].split("/")[0] in ip_all):
                            modify_rule_status = modify_rule(sg_response["SecurityGroups"][0]["GroupId"], rules["SecurityGroupRuleId"], cidr_list, ec2_child_client, rules["IpProtocol"],rules["FromPort"],rules["ToPort"], rules["CidrIpv4"], False)
                            if modify_rule_status:
                                logger.info("Security Group id : {0} has modified with the rule {1}".format(sg_response["SecurityGroups"][0]["GroupId"],rules["SecurityGroupRuleId"]))
                        else:
                            logger.info("There is no need to remediate this rule")
                    
                    if not rules["IsEgress"] and not "ReferencedGroupInfo" in rules.keys() and "CidrIpv6" in rules.keys() and "PrefixListId" not in rules.keys():
                        if (rules["FromPort"] not in web_ports or rules["ToPort"] not in web_ports) and ( ipsix_all in rules["CidrIpv6"]):
                            modify_rule_status = modify_rule(sg_response["SecurityGroups"][0]["GroupId"], rules["SecurityGroupRuleId"], cidr_list, ec2_child_client, rules["IpProtocol"],rules["FromPort"],rules["ToPort"], rules["CidrIpv6"], True)
                            if modify_rule_status:
                                logger.info("Security Group id : {0} has modified with the rule {1}".format(sg_response["SecurityGroups"][0]["GroupId"],rules["SecurityGroupRuleId"]))
                        else:
                            logger.info("There is no need to remediate this rule")
        return event
    except Exception as ex:
        logger.error("There is something wrong in lambda handler {0}".format(ex))
        raise ex
