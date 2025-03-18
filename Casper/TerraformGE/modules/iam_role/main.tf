resource "aws_iam_role" "instance_role" {
  name                = "instance-role"
  managed_policy_arns = var.managed_policy_arns
  tags                = var.tags
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      },
    ]
  })
}

resource "aws_iam_role_policy" "role_policy_1" {
  name = "DescribeInstancesPolicy"
  role = aws_iam_role.instance_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "ec2:DescribeInstances",
        ]
        Effect   = "Allow"
        Resource = "*"
      },
    ]
  })
}

resource "aws_iam_role_policy" "role_policy_2" {
  name = "SSMPutParamAllow"
  role = aws_iam_role.instance_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "ssm:PutParameter"
        ]
        Effect   = "Allow"
        Resource = "*"
      },
    ]
  })
}
