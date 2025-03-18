######################################################################################################################################################################
############################################################       SNIPPETS SECTION        #######################################################################
######################################################################################################################################################################

#  Ensure ALB is deployed in Private VPC and set to Internal

# Security Group

resource "aws_security_group" "alb_sg" {
  vpc_id      = var.alb_aws_vpc_id
  name_prefix = var.alb_sg_prefix
  tags        = var.alb_sg_tags
  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_security_group_rule" "allow_port_80_ingress_for_http_to_https_redirect" {
  #enable_http_to_https_redirect = var.alb_enable_http_to_https_redirect
  type              = "ingress"
  from_port         = var.alb_ingress_port
  to_port           = var.alb_ingress_port
  protocol          = "tcp"
  cidr_blocks       = var.alb_cidr_blocks_redirect
  security_group_id = aws_security_group.alb_sg.id
  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_security_group_rule" "allow_port_443_ingress_for_http_to_https_redirect" {
  #enable_http_to_https_redirect = var.alb_enable_http_to_https_redirect
  type              = "ingress"
  from_port         = var.alb_ingress_port
  to_port           = var.alb_ingress_port
  protocol          = "tcp"
  cidr_blocks       = var.alb_cidr_blocks_redirect
  security_group_id = aws_security_group.alb_sg.id
  lifecycle {
    create_before_destroy = true
  }

}

resource "aws_security_group_rule" "egress" {
  security_group_id = aws_security_group.alb_sg.id

  type        = "egress"
  cidr_blocks = ["0.0.0.0/0"]
  protocol    = "-1"
  from_port   = 0
  to_port     = 0

  lifecycle {
    create_before_destroy = true
  }
}

# ALB

resource "aws_lb" "alb_cg" {
  name                       = var.alb_name
  load_balancer_type         = "application" #  Ensure Classic ELBs are not used
  enable_deletion_protection = var.alb_enable_deletion_protection
  internal                   = true #  Ensure ALB is deployed in Private VPC and set to Internal
  subnets                    = var.alb_subnet_id
  security_groups            = [aws_security_group.alb_sg.id]  #  Ensure ALB is Deployed with appropriate Security Groups
  ip_address_type            = var.alb_ip_address_type
  access_logs {
    bucket  = var.alb_bucket
    prefix  = var.alb_sg_prefix
    enabled = true
  }
  tags = var.alb_common_tags #  Ensure Application load balancing resources are tagged according to organization standards 
}

resource "aws_lb_listener" "alb_cg_listener" {
  load_balancer_arn = aws_lb.alb_cg.arn

 
  protocol = "HTTPS"
  port     = var.alb_ingress_port

  #  Ensure HTTPS and TLS 1.2 using cert signed by organization CA
  ssl_policy      = var.alb_ssl_policy
  certificate_arn = var.alb_certificate_arn
  default_action {
    type = "redirect" #  Ensure HTTP requests are forcibly redirected to HTTPS

    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
    target_group_arn = var.alb_target_group
  }
}

#  Ensure CloudTrail logging enabled 
/* Actions are performed and managed by preexisting organisation model */


# Ensure that AWS ELBs use access logging ta analyze traffic patterns and identify and troubleshoot security issues

resource "aws_s3_bucket_server_side_encryption_configuration" "elb_access_logs" {
  bucket = var.alb_bucket
  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = data.aws_kms_alias.cg_cmk_key_alias.arn
      sse_algorithm     = "AWS:kms"
    }
  }
}

resource "aws_s3_bucket_policy" "elb_accesslogs_bucket_policy" {
  bucket = var.alb_bucket
  policy = data.template_file.elb_accesslogs_bucketpolicy.rendered
}

#  Ensure Role Based Access Control (RBAC) is used for IAM instead of security credentials to grant access to organization ELB

resource "aws_iam_role" "elb_rbac_role" {
  name                 = var.alb_role_name
  assume_role_policy   = data.template_file.elb_rbac_role_trust.rendered
  max_session_duration = var.alb_session_duration
}

# security/policy
resource "aws_iam_role_policy_attachment" "elb_rbac_role_attach_policy" {
  policy_arn        = var.alb_policy_arn
  role              = aws_iam_role.elb_rbac_role.name
}

#  Ensure idle Elastic load balancers (ELBs) are terminated in order to optimize cost
# this will be done as part of enterprise site reliability engineering life cycle management. 

