# CIS Pro Tools SSM
resource "aws_ssm_parameter" "cis_pro_tools_parameter" {
  name  = "platform_cis_cat_pro_tools"
  type  = "String"
  value = var.cis_pro_tools
}

# CIS Ami Reports SSM
resource "aws_ssm_parameter" "cis_ami_reports_parameter" {
  name  = "platform_cis_ami_reports"
  type  = "String"
  value = var.cis_ami_reports
}

# CIS Pro tools bucket creation
resource "aws_s3_bucket" "cis_pro_tools_bucket" {
  bucket = "platform-cis-cat-pro-tools-${var.env_type}"
}

resource "aws_s3_bucket_public_access_block" "cis_pro_tools_bucket_block_public_access" {
  bucket = aws_s3_bucket.cis_pro_tools_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# CIS AMI Reports bucket creation
resource "aws_s3_bucket" "cis_ami_reports_bucket" {
  bucket = "platform-cis-ami-reports-${var.env_type}"
}

resource "aws_s3_bucket_public_access_block" "cis_ami_reports_bucket_block_public_access" {
  bucket = aws_s3_bucket.cis_ami_reports_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Platform-CIS VPC Creation
resource "aws_vpc" "create_cis_vpc_in_master_account" {
  cidr_block       = "10.192.0.0/16"
  instance_tenancy = "default"
  enable_dns_support = true
  enable_dns_hostnames = true

  tags = {
    Name = "Platform_VPC_CIS"
  }
}

# CIS Internet Gateway Creation
resource "aws_internet_gateway" "cis_vpc_igw" {
  vpc_id = aws_vpc.create_cis_vpc_in_master_account.id

  #tags = {
   # Name = "igw"
  #}
}

# CIS Internet Gateway Attachment Creation
resource "aws_internet_gateway_attachment" "cis_vpc_igw_attachment" {
  internet_gateway_id = aws_internet_gateway.cis_vpc_igw.id
  vpc_id              = aws_vpc.create_cis_vpc_in_master_account.id
}

# CIS Subnet Creation
resource "aws_subnet" "create_cis_subnet" {
  vpc_id     = aws_vpc.create_cis_vpc_in_master_account.id
  cidr_block = "10.192.10.0/24"
  availability_zone = "us-east-1a"
  map_public_ip_on_launch = true

  #tags = {
  # Name = "Subnet"
  #}
}

# CIS Route Table Creation
resource "aws_route_table" "cis_vpc_rt" {
  vpc_id = aws_vpc.create_cis_vpc_in_master_account.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.cis_vpc_igw.id
  }

  #tags = {
  #  Name = "RouteTable"
  #}
}

# CIS Route Table Association Creation
resource "aws_route_table_association" "cis_vpc_rt_association" {
  subnet_id      = aws_subnet.create_cis_subnet.id
  route_table_id = aws_route_table.cis_vpc_rt.id
}

# Enable CIS VPC Flow logs 
resource "aws_flow_log" "enable_cis_vpc_flowlogs" {
    log_destination      = "arn:aws:s3:::platform-da2-central-vpcflowlogs-${var.vpc_flow_bucket_env_type}/"
    log_destination_type = "s3"
    traffic_type         = "ALL"
    vpc_id               = aws_vpc.create_cis_vpc_in_master_account.id

  tags = {
    Name = "Platform_VPC_CIS_Flowlogs"
  }
}

# CIS Security Group Creation
resource "aws_security_group" "cis_sg" {
  name        = "platform_CIS-Security-Group"
  description = "SSH traffic in, all traffic out."
  vpc_id      = aws_vpc.create_cis_vpc_in_master_account.id

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
  }

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# CIS Score report DynamoDB Table
resource "aws_dynamodb_table" "cis_score_report_dynamodb_table" {
  name           = "CIS-Score-Report"
  read_capacity  = 5
  write_capacity = 5
  hash_key       = "AMI_ID"
  point_in_time_recovery { 
    enabled = true 
  }

  attribute {
    name = "AMI_ID"
    type = "S"
  }
}

# CIS get Latest AMI Lambda
resource "aws_lambda_function" "cis_get_latest_ami_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_CIS_Get_Latest_AMI.zip"
  function_name = "platform_CIS_Get_Latest_AMI"
  role          = var.role_arn
  handler       = "platform_CIS_Get_Latest_AMI.lambda_handler"
  source_code_hash = data.archive_file.cis_score_report_for_latest_ami_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 2176
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# CIS launch EC2 instances Lambda
resource "aws_lambda_function" "cis_launch_ec2_instances_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_CIS_Launch_EC2_Instance.zip"
  function_name = "platform_CIS_Launch_EC2_Instance"
  role          = var.role_arn
  handler       = "platform_CIS_Launch_EC2_Instance.lambda_handler"
  source_code_hash = data.archive_file.cis_launch_ec2_instances_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 2176
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# CIS get EC2 SSM Reporting status Lambda
resource "aws_lambda_function" "cis_get_ec2_ssm_reporting_status_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_CIS_Get_EC2_SSM_Reporting_Status.zip"
  function_name = "platform_CIS_Get_EC2_SSM_Reporting_Status"
  role          = var.role_arn
  handler       = "platform_CIS_Get_EC2_SSM_Reporting_Status.lambda_handler"
  source_code_hash = data.archive_file.cis_get_ec2_ssm_reporting_status_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 2176
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# CIS get CIS report using SSM Lambda
resource "aws_lambda_function" "cis_get_cis_report_using_ssm_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_CIS-Get_CIS_Report_Using_SSM.zip"
  function_name = "platform_CIS-Get_CIS_Report_Using_SSM"
  role          = var.role_arn
  handler       = "platform_CIS-Get_CIS_Report_Using_SSM.lambda_handler"
  source_code_hash = data.archive_file.cis_get_cis_report_using_ssm_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 2176
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# CIS update CIS score dynamodb Lambda
resource "aws_lambda_function" "cis_update_cis_score_dynamodb_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_CIS_Update_CIS_Score_DynamoDB.zip"
  function_name = "platform_CIS_Update_CIS_Score_DynamoDB"
  role          = var.role_arn
  handler       = "platform_CIS_Update_CIS_Score_DynamoDB.lambda_handler"
  source_code_hash = data.archive_file.cis_update_cis_score_dynamodb_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 2176
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# CIS terminate ec2 instance Lambda
resource "aws_lambda_function" "cis_terminate_ec2_instance_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_CIS_Terminate_EC2_Instance.zip"
  function_name = "platform_CIS_Terminate_EC2_Instance"
  role          = var.role_arn
  handler       = "platform_CIS_Terminate_EC2_Instance.lambda_handler"
  source_code_hash = data.archive_file.cis_terminate_ec2_instance_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 2176
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# CIS failure notification Lambda
resource "aws_lambda_function" "cis_failure_notification_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_CIS_Send_notification_on_failure.zip"
  function_name = "platform_CIS_Send_notification_on_failure"
  role          = var.role_arn
  handler       = "platform_CIS_Send_notification_on_failure.lambda_handler"
  source_code_hash = data.archive_file.cis_failure_notification_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 2176
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# CIS AMI Tagging lambda schedule
resource "aws_cloudwatch_event_rule" "csi_ami_tagging_schedule" {
  name        = "platform_CIS-Score-Report-for-Latest-AMI"
  description = "Scheduled Rule for every 20th of the Month"
  schedule_expression = "cron(0 10 20 * ? *)"
  is_enabled = true
}

resource "aws_cloudwatch_event_target" "csi_ami_tagging_target" {
  rule      = aws_cloudwatch_event_rule.csi_ami_tagging_schedule.name
  target_id = "TargetFunctionV1"
  arn       = aws_lambda_function.cis_get_latest_ami_lambda.arn
}

resource "aws_lambda_permission" "csi_ami_tagging_lambda_permission" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.cis_get_latest_ami_lambda.arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.csi_ami_tagging_schedule.arn
}

# CIS Role
resource "aws_iam_role" "platform_cis_role" {
  name                = "platform-cis-score-InstanceRole"
  path                = "/"
  assume_role_policy  = jsonencode({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "ec2.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            })
  managed_policy_arns = ["arn:aws:iam::aws:policy/service-role/AmazonEC2RoleforSSM", "arn:aws:iam::aws:policy/AmazonS3FullAccess", "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore", "arn:aws:iam::aws:policy/AmazonSSMFullAccess", "arn:aws:iam::${var.master_account}:policy/platform_deny_assume_control_tower_role_policy"]
}

resource "aws_iam_instance_profile" "platform_cis_profile" {
  name = "platform-cis-score-InstanceRole"
  role = aws_iam_role.platform_cis_role.name
}

# CIS State Machine
resource "aws_sfn_state_machine" "cis_state_machine" {
  name     = "platform_CISStatemachine"
  role_arn = var.role_arn

  definition = data.template_file.cis_state_machine_template.rendered
}
