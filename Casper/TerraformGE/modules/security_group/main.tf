# Security Group attached with all the EC2 instances
resource "aws_security_group" "instance_sg" {
  name        = "instance-sg"
  description = "Security Group attached with all the EC2 instances"
  vpc_id      = var.vpc_id
  tags        = var.tags

  ingress {
    from_port         = 9031
    to_port           = 9031
    protocol          = "tcp"
    security_groups   = [aws_security_group.nlb_sg.id]
  }

  ingress {
    from_port   = 9999
    to_port     = 9999
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 9031
    to_port     = 9031
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 636
    to_port     = 636
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 3894
    to_port     = 3894
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}


# Security Group attached with the Network Load Balancer
resource "aws_security_group" "nlb_sg" {
  name        = "nlb-sg"
  description = "This group is part of AWS NLB on which the traffic will come from internal and external request."
  vpc_id      = var.vpc_id
  tags        = var.tags

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["10.0.0.0/8"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]
  }

  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}


# Security Group attached with the VPC Endpoints
resource "aws_security_group" "endpoint_sg" {
  name        = "endpoint-sg"
  description = "Security Group attached with VPC Endpoints"
  vpc_id      = var.vpc_id
  tags        = var.tags

  # ingress {
  #   from_port         = 0
  #   to_port           = 0
  #   protocol          = "-1"
  #   security_groups   = [aws_security_group.endpoint_sg.id]
  # }

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["10.159.82.0/23", "100.64.2.0/27"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
