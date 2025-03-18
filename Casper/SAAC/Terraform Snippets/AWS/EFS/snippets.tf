/*
 * # AWS EFS deployment
 * 
 * Requirements: 
 *  Ensure EFS utilizes VPC Endpoints for Private Inter-Service Communication
 *  Ensure EFS Users and Roles defined following least privileged model
 *  Ensure EFS is Encrypted at rest using organization Managed KMS Keys
 *  Ensure EFS connections are Encrypted in transit with TLS 1.2
 *  Ensure EFS access points created following least privileged model
 *  Ensure EFS root access is disabled by default
 *  Ensure EFS public access denied by default
 *  Ensure EFS resources are tagged according to organization standards
 *  Ensure EFS is created using organization managed VPC
 *  Ensure Automatic backup is enabled far EFS
 *  Ensure EFS has a Resource Based Policy attached restricting source principles to Organization only
 *
 */
locals {
  account_id = data.aws_caller_identity.current.account_id
}

#  Ensure EFS Users and Roles defined following least privileged model
resource "aws_iam_role" "efs_iam_role" {
  name               = var.efs_iam_role_name
  assume_role_policy = data.template_file.efs_iam_role_file.rendered
}
###

resource "aws_efs_file_system" "efs_file_system" {
  availability_zone_name = var.efs_availability_zone_name
  creation_token = var.efs_creation_token
  #  Ensure EFS is Encrypted at rest using Organization Managed KMS Keys
  encrypted = true
  kms_key_id = data.aws_kms_alias.cg_cmk_key_alias
  ###
  lifecycle_policy {
    transition_to_ia=var.efs_data_lifecycle_to_ia
    transition_to_primary_storage_class=var.efs_data_lifecycle_to_primary_sc
  }
  performance_mode = var.efs_performance_mode
  throughput_mode = var.efs_throughput_mode
  provisioned_throughput_in_mibps = var.efs_provisioned_throughput
  tags = var.efs_specific_tags
}

#  Ensure Automatic backup is enabled far EFS
resource "aws_efs_backup_policy" "policy" {
  file_system_id = aws_efs_file_system.efs_file_system.id
  backup_policy {
    status = "ENABLED"
  }
}
###


#  Ensure EFS utilizes VPC Endpoints for Private Inter-Service Communication
resource "aws_vpc_endpoint" "efs_vpc_endpoint" {
  vpc_id              = data.aws_vpc.aws_vpc_id.id
  # 9. Ensure EFS is created using CG managed VPC
  # Select VPC Id for VPC managed by CG
  service_name        = var.efs_vpc_endpoint_service_name
  vpc_endpoint_type   = var.efs_vpc_endpoint_type
  security_group_ids  = var.efs_vpc_endpoint_sg_ids
  private_dns_enabled = true
  tags = var.efs_vpc_endpoint_tags
}
###



#  Ensure EFS connections are Encrypted in transit with TLS 1.2
### Blocked using explicit deny rule present in policy file


#  Ensure EFS access points created following least privileged model
### Limit EFS access to data read and write from vpc endpoint

#  Ensure EFS root access is disabled by default
### Blocked using explicit deny rule present in policy file

#  Ensure EFS public access denied by default
### Blocked using explicit deny rule present in policy file that limits access to EFS through EFS endpoint

resource "aws_efs_file_system_policy" "efs_file_system_policy" {
  file_system_id = aws_efs_file_system.efs_file_system.id
  policy = data.template_file.efs_access_policy_file.rendered
}
###
