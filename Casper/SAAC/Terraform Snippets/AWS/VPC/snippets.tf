###############################################################################
#####################       REQUIREMENTS SECTION        #######################
###############################################################################
# Define Local Values in Terraform

# VPC Should not have Internet, NAT or VPN Gateways attached
# TODO: Discuss Sentinel
resource "aws_vpc" "primary_vpc" {
  # arn                              = (known after apply)
  assign_generated_ipv6_cidr_block  = false
  cidr_block                        = var.vpc_cidr_block
  # default_network_acl_id            = (known after apply)
  # default_route_table_id            = (known after apply)

  # VPC does not utilize the Default Security Group
  # security_group_ids                = (known after apply)

  enable_classiclink              = false
  enable_classiclink_dns_support  = false
  enable_dns_support              = true
  instance_tenancy                = "default"

  # Exports
  # dhcp_options_id                   = (known after apply)
  # enable_dns_hostnames              = (known after apply)
  # id                                = (known after apply)
  # main_route_table_id               = (known after apply)
  # owner_id                          = (known after apply)
}

// Private Subnet 1 AZ 1
resource "aws_subnet" "private_subnet1_az1" {
  assign_ipv6_address_on_creation = false
  vpc_id                          = aws_vpc.primary_vpc.id
  cidr_block                      = var.private_subnet1_az1_cidr
  availability_zone               = var.vpc_availability_zone_1
  availability_zone_id            = ""
  # owner_id                        = (known after apply)
  map_public_ip_on_launch         = false # VPC Should not have Public IP Addresses attached
}

// Private Subnet 2 AZ 1
resource "aws_subnet" "private_subnet2_az1" {
  assign_ipv6_address_on_creation = false
  vpc_id                          = aws_vpc.primary_vpc.id
  cidr_block                      = var.private_subnet2_az1_cidr
  availability_zone               = var.vpc_availability_zone_1
  availability_zone_id            = ""
  # owner_id                        = (known after apply)
  map_public_ip_on_launch         = false #  VPC Should not have Public IP Addresses attached
}

# Ensure Access Controls are utilized to enforce Least Privilege
# Ensure VPC Administrative access is reserved for Network Engineering only

resource "aws_iam_policy" "vpc_user_policy" {
  name = "vpc_user_policy"
  policy =  data.template_file.VpcUserPolicy.rendered
}

resource "aws_iam_user_policy_attachment" "vpc_user_attach" {
  user       = var.iam_vpc_user
  policy_arn = aws_iam_policy.vpc_user_policy.arn
}

# Ensure unused Virtual Private Gateways (VGWs) are removed
# TODO: Discuss Wiz, Terraform Scoping issue

# Utilize VPC Flow logs with Amazon CloudWatch

resource "aws_flow_log" "vpc-flow-logs" {
  iam_role_arn    = aws_iam_role.vpc_flow_logs_cloudwatch_role.arn
  log_destination = aws_cloudwatch_log_group.vpc_flow_logs_cloudwatch.arn
  traffic_type    = "ALL"
  vpc_id          = aws_vpc.primary_vpc.id
}

resource "aws_cloudwatch_log_group" "vpc_flow_logs_cloudwatch" {
  name              = var.vpc_flow_logs_cloudwatch
  retention_in_days = var.retention_in_days
  kms_key_id        = var.kms_key_id #  VPC flow log data is encrypted with a organization managed KMS key
}

resource "aws_iam_role" "vpc_flow_logs_cloudwatch_role" {
  name               = "vpc_flow_logs_cloudwatch_role"
  assume_role_policy = data.template_file.VpcFlowLogsCloudwatchRole.rendered
}

resource "aws_iam_role_policy" "vpc_flow_logs_cloudwatch_policy" {
  name   = "vpc_flow_logs_cloudwatch_policy"
  role   = aws_iam_role.vpc_flow_logs_cloudwatch_role.id
  policy = data.template_file.VpcFlowLogsCloudWatchPolicy.rendered
}

# Ensure that no Network ACL (NACL) allows inbound/ingress traffic from all ports
# Ensure that no Network ACL (NACL) allows unrestricted inbound traffic on TCP ports 22 and 3389
# TODO: Discuss Sentinel

# NOTE: Each AWS VPC comes with a Default Network ACL that cannot be deleted. The 
# aws_default_network_acl allows you to manage this Network ACL, but Terraform cannot 
# destroy it. Removing this resource from your configuration will remove it from your 
# statefile and management, but will not destroy the Network ACL. All Subnets associations
# and ingress or egress rules will be left as they are at the time of removal. You can 
# resume managing them via the AWS Console.
# resource "aws_default_network_acl" "vpc_primary_nacl" {
#   default_network_acl_id = "vpc_primary_nacl"

#   ingress {
#     protocol   = -1
#     rule_no    = 100
#     action     = "deny"
#     cidr_block = var.vpc_cidr_block
#     from_port  = 0
#     to_port    = 0
#   }

#   egress {
#     protocol   = -1
#     rule_no    = 100
#     action     = "deny"
#     cidr_block = var.vpc_cidr_block
#     from_port  = 22
#     to_port    = 22
#   }
  
#   egress {
#     protocol   = -1
#     rule_no    = 100
#     action     = "deny"
#     cidr_block = var.vpc_cidr_block
#     from_port  = 3389
#     to_port    = 3389
#   }
# }

#  VPC Peering is only enabled between organization owned AWS Accounts
# This requirement requires a multilayered approach.
# - Org level IaC scans (Sentinel) should enforce list of organization owned accounts
# - Org level policies should enforce the list of organization owned accounts
# - Validation should be in place on the variables, with the list
# - CSPM should detect if any unexpected peering takes place, and alerts triggered

# data "aws_caller_identity" "peer_provider" {
#   provider = aws.peer_provider
# }
# resource "aws_vpc_peering_connection" "vpc_peering_connection" {
  
#   vpc_id      = aws_vpc.primary_vpc.id

#   peer_vpc_id = var.peer_vpc_id
#   peer_owner_id = data.aws_caller_identity.peer_provider.account_id
#   peer_region = var.peer_vpc_region
#   auto_accept = false

#   # hardcoded
#   timeouts {
#     create = var.peer_vpc_timeout_create
#     delete = var.peer_vpc_timeout_delete
#   }
# }

# # VPC peering accepter configuration #
# resource "aws_vpc_peering_connection_accepter" "peer_accepter" {
#   provider = aws.peer_provider
#   vpc_peering_connection_id = aws_vpc_peering_connection.vpc_peering_connection.id
#   auto_accept               = var.auto_accept_peering
# }

# VPC peering options #
# Do not manage options for the same VPC peering connection in both a VPC Peering Connection resource and a VPC 
# Peering Connection Options resource.

#  Ensure that the Amazon VPC peering connection configuration is compliant with the desired routing policy

# This VPC Routes #  Route from THIS route table to PEER cidr

# resource "aws_default_route_table" "vpc_default_route_table" {
#   default_route_table_id = "vpc_default_route_table"

#   # This VPC Routes #  Route from THIS route table to PEER cidr
#   route {
#     cidr_block = var.vpc_cidr_block
#     vpc_peering_connection_id = aws_vpc_peering_connection.vpc_peering_connection.id
#   }

#   # Peer VPC Routes #  Route from PEER route table to THIS cidr
#   route {
#     cidr_block = var.peer_cidr_block
#     vpc_peering_connection_id = aws_vpc_peering_connection.vpc_peering_connection.id
#   }
# }

#  Ensure Amazon VPC endpoints do not allow unknown cross account access
#  Ensure that AWS private link is used to connect AWS Services with default public endpoint

# Creating the EndPoints for both the VPC Serv and VPC Client

resource "aws_vpc_endpoint_service" "vpc_endpoint_service" {
  allowed_principals = var.vpc_endpoint_allowed_principals
  acceptance_required        = true
  // service_type  = "Interface"
  // availability_zones = var.availability_zones
  network_load_balancer_arns = var.vpc_endpoint_lb_arns
}

# Create the EndPoint that will be used on the Client Side
resource "aws_vpc_endpoint" "ec2" {
  vpc_id            = aws_vpc.primary_vpc.id
  service_name      = var.aws_vpc_endpoint_to_service_name
  vpc_endpoint_type = "Interface"

  security_group_ids = var.aws_vpc_endpoint_sg_ids

  private_dns_enabled = true
}

# Ensure VPC data is encrypted in-transit utilizing TLS1.2 or newer
# can Implemented at account level policy and client side implementation not part of VPC
