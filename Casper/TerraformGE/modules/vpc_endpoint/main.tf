resource "aws_vpc_endpoint" "ssm" {
  vpc_id              = var.vpc_id
  service_name        = "com.amazonaws.${var.aws_region}.ssm"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = var.subnet_ids
  private_dns_enabled = true
  security_group_ids  = var.security_group_ids
  tags                = var.tags

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        "Action": "*",
        "Effect": "Allow",
        "Principal": "*",
        "Resource": "*"
      }
    ]
  })
}

resource "aws_vpc_endpoint" "ssm_messages" {
  vpc_id              = var.vpc_id
  service_name        = "com.amazonaws.${var.aws_region}.ssmmessages"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = var.subnet_ids
  private_dns_enabled = true
  security_group_ids  = var.security_group_ids
  tags                = var.tags

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        "Action": "*",
        "Effect": "Allow",
        "Principal": "*",
        "Resource": "*"
      }
    ]
  })
}
