"""
This module is used to remediate the unrestricted access in
the security groups
"""

import logging
import boto3
import json
import botocore
import ipaddress

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
LOGGER.addHandler(CH)


class RevokeIngressRules:
    """
    # Class: Revoke Unrestricted Access
    # Description: Includes method to remove the Ingress Rules in Security Group
      allowing the unrestricted access
    """

    def __init__(self, event, context):
        self.event = event
        self.context = context
        LOGGER.info("Event: %s" % self.event)
        LOGGER.info("Context: %s" % self.context)
        try:
            # get relevant input params from event

            self.reason_data = ""
            session_client = boto3.Session()

            self.res_dict = {}
            self.event_data = event
            self.account_id = self.event_data['account']
            self.region = self.event_data['region']
            self.resources = self.event_data['detail']['findings'][0]['Resources']
            self.sns_topic_arn = 'arn:aws:sns:' + self.region + ':' + self.account_id + \
                                 ':platform_Compliance_Security_Notification'
            self.sg_id = self.resources[0]['Details']['AwsEc2SecurityGroup']['GroupId']
            self.ip_all = '0.0.0.0/0'
            # self.ssh = 22
            # self.rdp = 3389
            self.https = 443
            self.http = 80
            self.smtp = 25
            self.allow_all = '-1'
            # self.rdgs_1 = '52.166.34.55'
            # self.rdgs_2 = '52.224.237.139'
            self.rdgs = ['52.166.34.55/32', '52.224.237.139/32']
            self.exp_ports = [443, 25, 80, 53]
            # self.deviation_ports = [20, 21, 139, 445]
            self.db_ports = [1433, 1434, 3306]
            self.mgmt_ports = [22, 3389]

            self.ec2_client = session_client.client('ec2', region_name=self.region)
            self.sns_client = session_client.client('sns', region_name=self.region)
            self.ssm_client = session_client.client('ssm', region_name=self.region)

            self.res_dict['sec_grp_id'] = self.sg_id
            # get account type from ssm
            ssm_response = self.ssm_client.get_parameter(Name='/Platform-Tag/platform_AccountType')
            self.account_type = ssm_response['Parameter']['Value']
            print("Account type is:",self.account_type)
            '''Exception for security group'''
            response = self.ec2_client.describe_security_groups(GroupIds=[self.sg_id])
            self.value = 'yes'
            if 'Tags' in response['SecurityGroups'][0].keys():
                tags = response['SecurityGroups'][0]['Tags']
                for item in tags:
                    if item['Key'] == 'platform_monitored':
                        self.value = item['Value']
                        print("is platform monitored:", self.value)
            else:
                print('No tags attached to security group-', self.sg_id)
        except Exception as exception:
            self.reason_data = "Missing required property %s" % exception
            LOGGER.error(self.reason_data)

    def check_rule(self):
        try:
            print('Inside Revoke Rules')
            print("Platform monitored tag status:", self.value)
            if self.value != 'no':
                if 'IpPermissions' in self.resources[0]['Details']['AwsEc2SecurityGroup']:
                    rules = self.resources[0]['Details']['AwsEc2SecurityGroup']['IpPermissions']
                    print(len(rules))
                    for rule in rules:
                        print(rule)
                        if 'UserIdGroupPairs' in rule.keys() and 'IpRanges' not in rule.keys():
                            print('Allowing all traffic from SGs')
                        else:
                            
                            '''for supporting multiple Ips like  this {'IpProtocol': '-1', 'IpRanges': [{'CidrIp': '10.0.0.0/8'}, {'CidrIp': '0.0.0.0/0'}]}'''
                            for cip in range(0,(len(rule['IpRanges']))):
                                if rule['IpRanges'][cip]['CidrIp'] == self.ip_all:
                                    if rule['IpProtocol'] == self.allow_all:
                                        print('Remediate for All TCP')
                                        rule_list = self.create_rule_list(rule,rule['IpRanges'][cip]['CidrIp'])
                                        self.revoke_rule(rule_list)
                                    elif rule['FromPort'] != rule['ToPort']:
                                        # checking for custom ports range
                                        print('All Custom port ranges are not allowed with source as all traffic')
                                        rule_list = self.create_rule_list(rule,rule['IpRanges'][cip]['CidrIp'])
                                        self.revoke_rule(rule_list)
                                    elif rule['ToPort'] == self.http or rule['ToPort'] == self.https or rule[
                                        'ToPort'] == self.smtp:
                                        print(
                                            'As per IRM and Trusted Advisor, port 80, 443 and 25 can be used with all traffic')
                                    else:
                                        print('Remediate all other ports apart from https, http and smtp')
                                        rule_list = self.create_rule_list(rule,rule['IpRanges'][cip]['CidrIp'])
                                        self.revoke_rule(rule_list)

                                elif self.account_type == 'public':
                                    if rule['IpRanges'][cip]['CidrIp'] not in self.rdgs:
                                        if rule['IpProtocol'] == self.allow_all:
                                            print('Allowing all traffic from specific IP in public account')
                                        elif rule['FromPort'] in self.mgmt_ports:
                                            print('Ports 22 and 3389 are allowed only from rdgs ips in public account')
                                            rule_list = self.create_rule_list(rule,rule['IpRanges'][cip]['CidrIp'])
                                            self.revoke_rule(rule_list)
                                        elif rule['FromPort'] in self.exp_ports:
                                            print('As per IRM and Trusted Advisor, port 80, 443 and 25 can be used with all '
                                                'traffic')
                                        elif rule['FromPort'] in self.db_ports:
                                            print('Notify when DB ports are opened')
                                            #self.send_notification()
                                        else:
                                            print('no security group to remediate')

                                    elif rule['IpRanges'][cip]['CidrIp'] in self.rdgs:
                                        if rule['IpProtocol'] == self.allow_all:
                                            print('Allowing all traffic from rdgs IP in public account')
                                        elif rule['FromPort'] in self.exp_ports:
                                            print('As per IRM and Trusted Advisor, port 80, 443 and 25 can be used with all '
                                            'traffic')
                                        elif rule['FromPort'] in self.db_ports:
                                            print('Notify when DB ports are opened')
                                            #self.send_notification()
                                        elif rule['FromPort'] not in self.mgmt_ports:
                                            print('Ports 22 and 3389 are allowed only from rdgs ips in public account')
                                            rule_list = self.create_rule_list(rule,rule['IpRanges'][cip]['CidrIp'])
                                            self.revoke_rule(rule_list)
                                        else:
                                            print('No Security group to remediate')
                                    else:
                                        print('No Security group Rule to remediate')

                                elif self.account_type == 'private':
                                    private_network = ipaddress.IPv4Network('10.0.0.0/8')
                                    ip = ipaddress.ip_network(rule['IpRanges'][cip]['CidrIp'])
                                    if not (ip.subnet_of(private_network)):
                                    #if rule['IpRanges'][cip]['CidrIp'] not in '10.0.0.0/8' and rule['IpRanges'][cip]['CidrIp'] not in '10.0.0.0/16':
                                        if rule['IpProtocol'] == self.allow_all:
                                            print('Allowing all traffic from specific IP in private account')
                                        elif rule['FromPort'] in [22, 3389]:
                                            print('ports 22 and 3389 are allowed only from 10.0.0.0/8 in private accounts')
                                            rule_list = self.create_rule_list(rule,rule['IpRanges'][cip]['CidrIp'])
                                            self.revoke_rule(rule_list)
                                        elif rule['FromPort'] in self.exp_ports:
                                            print('As per IRM and Trusted Advisor, port 80, 443 and 25 can be used with all '
                                                'traffic')
                                        elif rule['FromPort'] in self.db_ports:
                                            print('Notify when DB ports are opened')
                                            #self.send_notification()
                                        else:
                                            print('No Security Group to remediate')
                                    else:
                                        print('No Security Group Rule to remediate')
                                else:
                                    print('Not a business account')
            else:
                print('the security group', self.sg_id, 'is exception from remediation')

        except Exception as exception:
            print("ERROR Send Notification", exception)
            self.reason_data = "Send Notification Lambda - %s" % exception
            LOGGER.error(self.reason_data)
            self.res_dict['Port Remediation'] = 'FAILED'
            return self.res_dict
        return self.res_dict
        
    
    def create_rule_list(self, rule, cidr):
        ''' Copying rule data to another variable rule list'''
        try:
            rule_list = rule.copy()
            if 'UserIdGroupPairs' in rule_list.keys():
                rule_list.pop('UserIdGroupPairs')
            for ip in rule_list['IpRanges']:
                if ip['CidrIp'] == cidr:
                    rule_list.pop('IpRanges')
                    rule_list['IpRanges'] = [{'CidrIp': cidr}]
        except Exception as exception:
            print("ERROR creating rulelist", exception)
        return rule_list
                    
    def revoke_rule(self, rule):
        try:
            print("Revoking rule - ", rule)
            print("the id is:", self.sg_id)
            revoke_response = self.ec2_client.revoke_security_group_ingress(
                GroupId=self.sg_id,
                IpPermissions=[rule]
            )
            print("Revoked a rule:",revoke_response)
            self.res_dict['Port Remediation'] = 'PASSED'
            self.send_notification()
        except botocore.exceptions.ClientError as error:
            if error.response['Error']['Code'] == "InvalidPermission.NotFound":
                self.res_dict['Port Remediation'] = 'PASSED'
                print("The rule does not exist")
            else:
                self.reason_data = "Revoke rule function - %s" % exception
                LOGGER.error(self.reason_data)
                self.res_dict['Port Remediation'] = 'FAILED'
                return self.res_dict
        return self.res_dict

    def send_notification(self):
        try:
            sns_subject = 'Security Threat - Unrestricted access in Security group'
            sns_message = 'Hello User, \n' \
                          'You have configured a security group with id - "' + self.sg_id + '" in the ' \
                          + self.region + ' region with rules allowing unrestricted access and the ' \
                                          'unrestricted access rules are deleted in the account - ' \
                          + self.account_id + ' . \nAs per Shell IRM Compliance,' \
                                              'Security Groups should not allow unrestricted access.\n' \
                                              'Please refer the ' \
                                              '"QRG_Best Practices for Whitelisted Services" ' \
                                              'to follow best practices for Security Group. \n' \
                                              'If you have any queries, Please raise a ServiceNow case to the queue - ' \
                                              'Cloud Hosting Services. \n'
            send_response = self.sns_client.publish(TopicArn=self.sns_topic_arn,
                                                    Message=sns_message,
                                                    Subject=sns_subject)
            self.res_dict['Message ID'] = send_response['MessageId']
            self.res_dict['Port Remediation'] = 'PASSED'

        except Exception as exception:
            print("ERROR Send Notification", exception)
            self.reason_data = "Send Notification Lambda - %s" % exception
            LOGGER.error(self.reason_data)
            self.res_dict['Port Remediation'] = 'FAILED'
            return self.res_dict
        return self.res_dict


def lambda_handler(event, context):
    """
    Lambda handler that calls the function to revoke the ingress rules
    returns: the status of the operation
    ref: fixed the bug - ADO Item Number : 411159
    """
    result_value = {}
    try:
        print(json.dumps(event))
        sec_hub_obj = RevokeIngressRules(event, context)
        #output_value = sec_hub_obj.create_rule_list()
        output_value = sec_hub_obj.check_rule()
        print("Output of the function : " + str(output_value))
        result_value.update(output_value)
        return result_value

    except Exception as exception:
        print("Error in Lambda Handler", exception)
        result_value['Handler Exception'] = str(exception)
        return exception