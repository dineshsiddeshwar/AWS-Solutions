import json, boto3
import sys


class DeleteDefaultVPC(object):
  """
  # Class: Delete Default VPC
  # Description: Deletes default VPCs from Control Tower non-governed and non-supported AWS regions in newly created AWS account
  """
  def __init__(self, event):
    try:
      self.account_id = str(event['ProvisionedProduct']['AccountNumber'])
      print("Creating Session and AWS Service Clients")
      session = boto3.session.Session()
      sts_client = session.client('sts')
      child_account_role_arn = "arn:aws:iam::" + self.account_id + ":role/AWSControlTowerExecution"
      child_account_role_creds = sts_client.assume_role(RoleArn=child_account_role_arn,
                                                        RoleSessionName='DefaultVPCLambdaRoleSession',
                                                        DurationSeconds=900)
      credentials = child_account_role_creds.get('Credentials')
      accessKeyID = credentials.get('AccessKeyId')
      secretAccessKey = credentials.get('SecretAccessKey')
      sessionToken = credentials.get('SessionToken')
      self.assumeRoleSession = boto3.session.Session(accessKeyID, secretAccessKey, sessionToken)
      self.ec2_client = self.assumeRoleSession.client('ec2', region_name='us-west-2')

    except Exception as error:
      print(error)
      return error


  def delete_igw(self, ec2, vpc_id):
    """
    Detach and delete the internet gateway.
    """

    args = {
      'Filters' : [
        {
          'Name' : 'attachment.vpc-id',
          'Values' : [ vpc_id ]
        }
      ]
    }

    try:
      igw = ec2.describe_internet_gateways(**args)['InternetGateways']
    except Exception as e:
      print(e.response['Error']['Message'])

    igw_deleted = True
    if igw:
      igw_id = igw[0]['InternetGatewayId']

      igw_detached = False
      igw_deleted = False
      try:
        result = ec2.detach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)
        print('Detached IGW {} successfully'.format(igw_id))
        igw_detached = True
      except Exception as e:
        print(e.response['Error']['Message'])
      if igw_detached:
        try:
          result = ec2.delete_internet_gateway(InternetGatewayId=igw_id)
          print('Deleted IGW {} successfully'.format(igw_id))
          igw_deleted = True
        except Exception as e:
          print(e.response['Error']['Message'])
          print('IGW {} deletion failed, please troubleshoot further'.format(igw_id))
      else:
        print('IGW {} is not detached successfully'.format(igw_id))
    else:
      print("No IGW found in the VPC")

    return igw_deleted


  def delete_subs(self, ec2, args):
    """
    Delete the subnets.
    """

    try:
      subs = ec2.describe_subnets(**args)['Subnets']
    except Exception as e:
      print(e.response['Error']['Message'])

    sub_deleted = True
    if subs:
      for sub in subs:
        sub_id = sub['SubnetId']

        sub_deleted = False

        try:
          result = ec2.delete_subnet(SubnetId=sub_id)
          print('Deleted Subnet {} successfully'.format(sub_id))
          sub_deleted = True
        except Exception as e:
          print(e.response['Error']['Message'])
          print('Subnet {} deletion failed, please troubleshoot further'.format(sub_id))
    else:
      print("No Subnet found in the VPC")

    return sub_deleted


  def delete_rtbs(self, ec2, args):
    """
    Delete the route tables.
    """

    try:
      rtbs = ec2.describe_route_tables(**args)['RouteTables']
    except Exception as e:
      print(e.response['Error']['Message'])

    rtb_deleted = True
    if rtbs:
      for rtb in rtbs:
        main = 'false'
        for assoc in rtb['Associations']:
          main = assoc['Main']
        if main == True:
          continue
        rtb_id = rtb['RouteTableId']

        rtb_deleted = False

        try:
          result = ec2.delete_route_table(RouteTableId=rtb_id)
          print('Deleted Main Route Table {} successfully'.format(rtb_id))
          rtb_deleted = True
        except Exception as e:
          print(e.response['Error']['Message'])
          print('Route Table {} deletion failed, please troubleshoot further'.format(rtb_id))
    else:
      print("No Route Tables found in the VPC")

    return rtb_deleted


  def delete_acls(self, ec2, args):
    """
    Delete the network access lists (NACLs).
    """

    try:
      acls = ec2.describe_network_acls(**args)['NetworkAcls']
    except Exception as e:
      print(e.response['Error']['Message'])

    acl_deleted = True
    if acls:
      for acl in acls:
        default = acl['IsDefault']
        if default == True:
          continue
        acl_id = acl['NetworkAclId']

        acl_deleted = False

        try:
          result = ec2.delete_network_acl(NetworkAclId=acl_id)
          print('Default NACL {} has been deleted successfully'.format(acl_id))
          acl_deleted = True
        except Exception as e:
          print(e.response['Error']['Message'])
          print('NACL {} deletion failed, please troubleshoot further'.format(acl_id))
    else:
      print("No NACLs found in the VPC")

    return acl_deleted


  def delete_sgps(self, ec2, args):
    """
    Delete any security groups.
    """

    try:
      sgps = ec2.describe_security_groups(**args)['SecurityGroups']
    except Exception as e:
      print(e.response['Error']['Message'])

    sg_deleted = True
    if sgps:
      for sgp in sgps:
        default = sgp['GroupName']
        if default == 'default':
          continue
        sg_id = sgp['GroupId']

        sg_deleted = False

        try:
          result = ec2.delete_security_group(GroupId=sg_id)
          print('Default Security Group {} has been deleted successfully'.format(sg_id))
          sg_deleted = True
        except Exception as e:
          print(e.response['Error']['Message'])
          print('Security Group {} deletion failed, please troubleshoot further'.format(sg_id))
    else:
      print("No Security Groups found in the VPC")

    return sg_deleted


  def delete_vpc(self, ec2, vpc_id, region):
    """
    Delete the VPC.
    """

    vpc_deleted = False
    try:
      result = ec2.delete_vpc(VpcId=vpc_id)
      print('VPC {} has been deleted from the {} region.'.format(vpc_id, region))
      vpc_deleted = True
    except Exception as e:
      print(e.response['Error']['Message'])
      print('VPC {} deletion failed from the {} region, please troubleshoot further'.format(vpc_id, region))
      

    return vpc_deleted


  def get_regions(self, ec2):
    """
    Return all AWS regions.
    """

    regions = []

    try:
      aws_regions = ec2.describe_regions()['Regions']
    except Exception as e:
      print(e.response['Error']['Message'])

    else:
      for region in aws_regions:
        regions.append(region['RegionName'])

    return regions


  def delete_vpcs(self, event):
    """

    Order of operation:

    1.) Delete the internet gateway
    2.) Delete Subnets
    3.) Delete route tables
    4.) Delete network access lists
    5.) Delete security groups
    6.) Delete the VPC
    """

    regions = self.get_regions(self.ec2_client)

    for region in regions:

      ec2 = self.assumeRoleSession.client('ec2', region_name=region)

      try:
        attribs = ec2.describe_account_attributes(AttributeNames=[ 'default-vpc' ])['AccountAttributes']
      except Exception as e:
        print(e.response['Error']['Message'])
        return

      else:
        vpc_id = attribs[0]['AttributeValues'][0]['AttributeValue']

      if vpc_id == 'none':
        print('VPC (default) was not found in the {} region.'.format(region))
        continue

      # Are there any existing resources?  Since most resources attach an ENI, this is a check up.

      args = {
        'Filters' : [
          {
            'Name' : 'vpc-id',
            'Values' : [ vpc_id ]
          }
        ]
      }

      try:
        eni = ec2.describe_network_interfaces(**args)['NetworkInterfaces']
      except Exception as e:
        print(e.response['Error']['Message'])
        return

      if eni:
        print('VPC {} has existing resources in the {} region.'.format(vpc_id, region))
        continue

      result = self.delete_igw(ec2, vpc_id)
      if result:
        result = self.delete_subs(ec2, args)
        if result:
          result = self.delete_rtbs(ec2, args)
          if result:
            result = self.delete_acls(ec2, args)
            if result:
              result = self.delete_sgps(ec2, args)
              if result:
                result = self.delete_vpc(ec2, vpc_id, region)


    return

try:
    local_file_path = str(sys.argv[1])+"parameters.json"
    print("Parameters local file path: ", local_file_path)
    with open(local_file_path) as json_data:
        parameters_data = json.load(json_data)
    print(parameters_data)
    if parameters_data['RequestType'] == "Create": 
        delete_default_vpc = DeleteDefaultVPC(parameters_data)
        if parameters_data['ProvisionedProduct']['StatusAfterCreate'] == 'AVAILABLE':
            print('Deletion of default vpc resources are in progress..')
            answer = delete_default_vpc.delete_vpcs(parameters_data)
            print(answer)
except Exception as ex:
    print(str(ex))