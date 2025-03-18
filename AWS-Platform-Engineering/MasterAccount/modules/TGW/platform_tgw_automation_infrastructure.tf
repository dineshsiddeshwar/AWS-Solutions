# TGW Table SSM
resource "aws_ssm_parameter" "tgw_table_parameter" {
  name  = "tgw_table_name"
  type  = "String"
  value = var.tgw_table
}

# TGW VPC Creation
resource "aws_vpc" "create_tgw_vpc_in_master_account" {
  cidr_block       = var.tgw_vpc_cidr
  instance_tenancy = "default"
  enable_dns_support = true
  enable_dns_hostnames = true

  tags = {
    Name = "DA-TGW-VPC",
    "platform_donotdelete" = "yes"
  }
}

# TGW Private Subnet 1 Creation
resource "aws_subnet" "create_tgw_pvt_subnet_1" {
  vpc_id     = aws_vpc.create_tgw_vpc_in_master_account.id
  cidr_block = var.tgw_pvt_sub_cidr_1
  availability_zone = "us-east-1a"

  tags = {
    Name = "TGW-Prv-Subnet-1"
  }
}

# TGW Private Subnet 2 Creation
resource "aws_subnet" "create_tgw_pvt_subnet_2" {
  vpc_id     = aws_vpc.create_tgw_vpc_in_master_account.id
  cidr_block = var.tgw_pvt_sub_cidr_2
  availability_zone = "us-east-1b"

  tags = {
    Name = "TGW-Prv-Subnet-2"
  }
}

# TGW Public Subnet 1 Creation
resource "aws_subnet" "create_tgw_pub_subnet_1" {
  vpc_id     = aws_vpc.create_tgw_vpc_in_master_account.id
  cidr_block = var.tgw_pub_sub_cidr_1
  availability_zone = "us-east-1a"

  tags = {
    Name = "TGW-Pub-Subnet-1"
  }
}

# TGW Public Subnet 2 Creation
resource "aws_subnet" "create_tgw_pub_subnet_2" {
  vpc_id     = aws_vpc.create_tgw_vpc_in_master_account.id
  cidr_block = var.tgw_pub_sub_cidr_2
  availability_zone = "us-east-1b"

  tags = {
    Name = "TGW-Pub-Subnet-2"
  }
}

#TGW Internet Gateway Creation
resource "aws_internet_gateway" "tgw_vpc_igw" {
  vpc_id = aws_vpc.create_tgw_vpc_in_master_account.id

  tags = {
    Name = "TGW-igw"
  }
}

#TGW Internet Gateway Attachment Creation
resource "aws_internet_gateway_attachment" "tgw_vpc_igw_attachment" {
  internet_gateway_id = aws_internet_gateway.tgw_vpc_igw.id
  vpc_id              = aws_vpc.create_tgw_vpc_in_master_account.id
}

#TGW Elastic IP Creation
resource "aws_eip" "tgw_eip_1" {
  vpc                       = true
  tags = {
    Name = "TGW-eip-us-east-1a"
  }
}

resource "aws_eip" "tgw_eip_2" {
  vpc                       = true
  tags = {
    Name = "TGW-eip-us-east-1b"
  }
}

#TGW NatGateway Creation
resource "aws_nat_gateway" "tgw_vpc_nat_gw_1" {
  allocation_id = aws_eip.tgw_eip_1.id
  subnet_id     = aws_subnet.create_tgw_pub_subnet_1.id

  tags = {
    Name = "TGW-nat-us-east-1a"
  }

  # To ensure proper ordering, it is recommended to add an explicit dependency
  # on the Internet Gateway for the VPC.
  depends_on = [aws_internet_gateway.tgw_vpc_igw]
}

resource "aws_nat_gateway" "tgw_vpc_nat_gw_2" {
  allocation_id = aws_eip.tgw_eip_2.id
  subnet_id     = aws_subnet.create_tgw_pub_subnet_2.id

  tags = {
    Name = "TGW-nat-us-east-1b"
  }

  # To ensure proper ordering, it is recommended to add an explicit dependency
  # on the Internet Gateway for the VPC.
  depends_on = [aws_internet_gateway.tgw_vpc_igw]
}

#TGW Private Route Table 1 Creation
resource "aws_route_table" "tgw_vpc_pvt_rt_1" {
  vpc_id = aws_vpc.create_tgw_vpc_in_master_account.id

  route {
    cidr_block = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.tgw_vpc_nat_gw_1.id
  }

  route {
    cidr_block = "10.155.94.0/24"
    transit_gateway_id = var.tgw_id
  }

  route {
    cidr_block = "10.167.30.0/24"
    transit_gateway_id = var.tgw_id
  }

  route {
    cidr_block = "10.223.94.0/24"
    transit_gateway_id = var.tgw_id
  }

  tags = {
    Name = "TGW-Prv-RouteTable-1"
  }
}

#TGW Private Route Table 1 Association Creation
resource "aws_route_table_association" "tgw_vpc_pvt_rt_1_association" {
  subnet_id      = aws_subnet.create_tgw_pvt_subnet_1.id
  route_table_id = aws_route_table.tgw_vpc_pvt_rt_1.id
}

#TGW Private Route Table 2 Creation
resource "aws_route_table" "tgw_vpc_pvt_rt_2" {
  vpc_id = aws_vpc.create_tgw_vpc_in_master_account.id

  route {
    cidr_block = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.tgw_vpc_nat_gw_2.id
  }

  route {
    cidr_block = "10.155.94.0/24"
    transit_gateway_id = var.tgw_id
  }

  route {
    cidr_block = "10.167.30.0/24"
    transit_gateway_id = var.tgw_id
  }

  route {
    cidr_block = "10.223.94.0/24"
    transit_gateway_id = var.tgw_id
  }

  tags = {
    Name = "TGW-Prv-RouteTable-2"
  }
}

#TGW Private Route Table 2 Association Creation
resource "aws_route_table_association" "tgw_vpc_pvt_rt_2_association" {
  subnet_id      = aws_subnet.create_tgw_pvt_subnet_2.id
  route_table_id = aws_route_table.tgw_vpc_pvt_rt_2.id
}

#TGW Public Route Table 1 Creation
resource "aws_route_table" "tgw_vpc_pub_rt_1" {
  vpc_id = aws_vpc.create_tgw_vpc_in_master_account.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.tgw_vpc_igw.id
  }

  tags = {
    Name = "TGW-Pub-RouteTable-1"
  }
}

#TGW Public Route Table 1 Association Creation
resource "aws_route_table_association" "tgw_vpc_pub_rt_1_association" {
  subnet_id      = aws_subnet.create_tgw_pub_subnet_1.id
  route_table_id = aws_route_table.tgw_vpc_pub_rt_1.id
}

#TGW Public Route Table 2 Creation
resource "aws_route_table" "tgw_vpc_pub_rt_2" {
  vpc_id = aws_vpc.create_tgw_vpc_in_master_account.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.tgw_vpc_igw.id
  }

  tags = {
    Name = "TGW-Pub-RouteTable-2"
  }
}

#TGW Public Route Table 2 Association Creation
resource "aws_route_table_association" "tgw_vpc_pub_rt_2_association" {
  subnet_id      = aws_subnet.create_tgw_pub_subnet_2.id
  route_table_id = aws_route_table.tgw_vpc_pub_rt_2.id
}

#TGW Security Group Creation
resource "aws_security_group" "tgw_sg" {
  name        = "DA-TGW-VPC-SG"
  description = "Security group for DA VPC to TGW connectivity"
  vpc_id      = aws_vpc.create_tgw_vpc_in_master_account.id
}

# Request TGW Resource Share Lambda
resource "aws_lambda_function" "request_tgw_resource_share_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_request_TGW_resource_share.zip"
  function_name = "platform_request_TGW_resource_share"
  role          = var.role_arn
  handler       = "platform_request_TGW_resource_share.lambda_handler"
  source_code_hash = data.archive_file.request_tgw_resource_share_lambda_zip.output_base64sha256

  runtime = "python3.9"
  memory_size = 512
  timeout = 900

  vpc_config {
    subnet_ids         = [aws_subnet.create_tgw_pvt_subnet_1.id, aws_subnet.create_tgw_pvt_subnet_2.id]
    security_group_ids = [aws_security_group.tgw_sg.id]
  }
  layers = [var.requests_layer]

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Request TGW Resource Share Lambda GA
resource "aws_lambda_function" "request_tgw_resource_share_ga_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_request_TGW_resource_share_ga.zip"
  function_name = "platform_request_TGW_resource_share_ga"
  role          = var.role_arn
  handler       = "platform_request_TGW_resource_share_ga.lambda_handler"
  source_code_hash = data.archive_file.platform_request_TGW_resource_share_ga_lambda_zip.output_base64sha256

  runtime = "python3.9"
  memory_size = 512
  timeout = 900

  vpc_config {
    subnet_ids         = [aws_subnet.create_tgw_pvt_subnet_1.id, aws_subnet.create_tgw_pvt_subnet_2.id]
    security_group_ids = [aws_security_group.tgw_sg.id]
  }
  layers = [var.requests_layer]

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Accept TGW Resource Share Lambda
resource "aws_lambda_function" "accept_tgw_resource_share_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_accept_TGW_resource_share.zip"
  function_name = "platform_accept_TGW_resource_share"
  role          = var.role_arn
  handler       = "platform_accept_TGW_resource_share.lambda_handler"
  source_code_hash = data.archive_file.accept_tgw_resource_share_lambda_zip.output_base64sha256

  runtime = "python3.9"
  memory_size = 512
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Accept TGW Resource Share Lambda GA
resource "aws_lambda_function" "accept_tgw_resource_share_ga_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_accept_TGW_resource_share_ga.zip"
  function_name = "platform_accept_TGW_resource_share_ga"
  role          = var.role_arn
  handler       = "platform_accept_TGW_resource_share_ga.lambda_handler"
  source_code_hash = data.archive_file.platform_accept_TGW_resource_share_ga_lambda_zip.output_base64sha256

  runtime = "python3.9"
  memory_size = 128
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Create TGW attachment Lambda
resource "aws_lambda_function" "create_tgw_attachment_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_create_TGW_attachment.zip"
  function_name = "platform_create_TGW_attachment"
  role          = var.role_arn
  handler       = "platform_create_TGW_attachment.lambda_handler"
  source_code_hash = data.archive_file.create_tgw_attachment_lambda_zip.output_base64sha256

  runtime = "python3.9"
  memory_size = 512
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Create TGW attachment Lambda GA
resource "aws_lambda_function" "create_tgw_attachment_ga_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_create_TGW_attachment_ga.zip"
  function_name = "platform_create_TGW_attachment_ga"
  role          = var.role_arn
  handler       = "platform_create_TGW_attachment_ga.lambda_handler"
  source_code_hash = data.archive_file.platform_create_TGW_attachment_ga_lambda_zip.output_base64sha256

  runtime = "python3.9"
  memory_size = 512
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}


# Accept TGW attachment Lambda
resource "aws_lambda_function" "accept_tgw_attachment_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_accept_TGW_attachment.zip"
  function_name = "platform_accept_TGW_attachment"
  role          = var.role_arn
  handler       = "platform_accept_TGW_attachment.lambda_handler"
  source_code_hash = data.archive_file.accept_tgw_attachment_lambda_zip.output_base64sha256

  runtime = "python3.9"
  memory_size = 512
  timeout = 900

  vpc_config {
    subnet_ids         = [aws_subnet.create_tgw_pvt_subnet_1.id, aws_subnet.create_tgw_pvt_subnet_2.id]
    security_group_ids = [aws_security_group.tgw_sg.id]
  }
  layers = [var.requests_layer]

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Accept TGW attachment Lambda GA
resource "aws_lambda_function" "accept_tgw_attachment_ga_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_accept_TGW_attachment_ga.zip"
  function_name = "platform_accept_TGW_attachment_ga"
  role          = var.role_arn
  handler       = "platform_accept_TGW_attachment_ga.lambda_handler"
  source_code_hash = data.archive_file.platform_accept_TGW_attachment_ga_lambda_zip.output_base64sha256

  runtime = "python3.9"
  memory_size = 512
  timeout = 900

  vpc_config {
    subnet_ids         = [aws_subnet.create_tgw_pvt_subnet_1.id, aws_subnet.create_tgw_pvt_subnet_2.id]
    security_group_ids = [aws_security_group.tgw_sg.id]
  }
  layers = [var.requests_layer]

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Create VPC TGW Route Lambda
resource "aws_lambda_function" "configure_vpc_tgw_route_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_configure_vpc_traffic_to_TGW.zip"
  function_name = "platform_configure_vpc_traffic_to_TGW"
  role          = var.role_arn
  handler       = "platform_configure_vpc_traffic_to_TGW.lambda_handler"
  source_code_hash = data.archive_file.configure_vpc_tgw_route_lambda_zip.output_base64sha256

  runtime = "python3.9"
  memory_size = 512
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Create VPC TGW Route Lambda GA
resource "aws_lambda_function" "configure_vpc_tgw_route_ga_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_configure_vpc_traffic_to_TGW_ga.zip"
  function_name = "platform_configure_vpc_traffic_to_TGW_ga"
  role          = var.role_arn
  handler       = "platform_configure_vpc_traffic_to_TGW_ga.lambda_handler"
  source_code_hash = data.archive_file.platform_configure_vpc_traffic_to_TGW_ga_lambda_zip.output_base64sha256

  runtime = "python3.9"
  memory_size = 512
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Verify TGW Association Lambda
resource "aws_lambda_function" "verify_tgw_association_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_verify_TGW_route_association.zip"
  function_name = "platform_verify_TGW_route_association"
  role          = var.role_arn
  handler       = "platform_verify_TGW_route_association.lambda_handler"
  source_code_hash = data.archive_file.verify_tgw_association_lambda_zip.output_base64sha256

  runtime = "python3.9"
  memory_size = 512
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Verify TGW Association Lambda GA
resource "aws_lambda_function" "verify_tgw_association_ga_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_verify_TGW_route_association_ga.zip"
  function_name = "platform_verify_TGW_route_association_ga"
  role          = var.role_arn
  handler       = "platform_verify_TGW_route_association_ga.lambda_handler"
  source_code_hash = data.archive_file.platform_verify_TGW_route_association_ga_lambda_zip.output_base64sha256

  runtime = "python3.9"
  memory_size = 512
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# VPC TGW Extension Lambda
resource "aws_lambda_function" "vpc_tgw_extension_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_vpc_extension_tgw_update.zip"
  function_name = "platform_vpc_extension_tgw_update"
  role          = var.role_arn
  handler       = "platform_vpc_extension_tgw_update.lambda_handler"
  source_code_hash = data.archive_file.vpc_tgw_extension_lambda_zip.output_base64sha256

  runtime = "python3.9"
  memory_size = 512
  timeout = 900

  vpc_config {
    subnet_ids         = [aws_subnet.create_tgw_pvt_subnet_1.id, aws_subnet.create_tgw_pvt_subnet_2.id]
    security_group_ids = [aws_security_group.tgw_sg.id]
  }
  layers = [var.requests_layer]

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# VPC TGW Extension Lambda GA
resource "aws_lambda_function" "vpc_tgw_extension_ga_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_vpc_extension_tgw_update_ga.zip"
  function_name = "platform_vpc_extension_tgw_update_ga"
  role          = var.role_arn
  handler       = "platform_vpc_extension_tgw_update_ga.lambda_handler"
  source_code_hash = data.archive_file.platform_vpc_extension_tgw_update_ga_lambda_zip.output_base64sha256

  runtime = "python3.9"
  memory_size = 512
  timeout = 900

  vpc_config {
    subnet_ids         = [aws_subnet.create_tgw_pvt_subnet_1.id, aws_subnet.create_tgw_pvt_subnet_2.id]
    security_group_ids = [aws_security_group.tgw_sg.id]
  }
  layers = [var.requests_layer]

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Disassociate TGW attchment Lambda
resource "aws_lambda_function" "disassociate_tgw_attachment_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_disassociate_TGW_attachment.zip"
  function_name = "platform_disassociate_TGW_attachment"
  role          = var.role_arn
  handler       = "platform_disassociate_TGW_attachment.lambda_handler"
  source_code_hash = data.archive_file.disassociate_tgw_attachment_lambda_zip.output_base64sha256

  runtime = "python3.9"
  memory_size = 512
  timeout = 900

  vpc_config {
    subnet_ids         = [aws_subnet.create_tgw_pvt_subnet_1.id, aws_subnet.create_tgw_pvt_subnet_2.id]
    security_group_ids = [aws_security_group.tgw_sg.id]
  }
  layers = [var.requests_layer]

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Disassociate TGW attchment Lambda GA
resource "aws_lambda_function" "disassociate_tgw_attachment_ga_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_disassociate_TGW_attachment_ga.zip"
  function_name = "platform_disassociate_TGW_attachment_ga"
  role          = var.role_arn
  handler       = "platform_disassociate_TGW_attachment_ga.lambda_handler"
  source_code_hash = data.archive_file.platform_disassociate_TGW_attachment_ga_lambda_zip.output_base64sha256

  runtime = "python3.9"
  memory_size = 512
  timeout = 900

  vpc_config {
    subnet_ids         = [aws_subnet.create_tgw_pvt_subnet_1.id, aws_subnet.create_tgw_pvt_subnet_2.id]
    security_group_ids = [aws_security_group.tgw_sg.id]
  }
  layers = [var.requests_layer]

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Disassociate TGW resource share Lambda
resource "aws_lambda_function" "disassociate_tgw_resource_share_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_disassociate_TGW_resource_share.zip"
  function_name = "platform_disassociate_TGW_resource_share"
  role          = var.role_arn
  handler       = "platform_disassociate_TGW_resource_share.lambda_handler"
  source_code_hash = data.archive_file.disassociate_tgw_resource_share_lambda_zip.output_base64sha256

  runtime = "python3.9"
  memory_size = 512
  timeout = 900

  vpc_config {
    subnet_ids         = [aws_subnet.create_tgw_pvt_subnet_1.id, aws_subnet.create_tgw_pvt_subnet_2.id]
    security_group_ids = [aws_security_group.tgw_sg.id]
  }
  layers = [var.requests_layer]

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Disassociate TGW resource share Lambda GA
resource "aws_lambda_function" "disassociate_tgw_resource_share_ga_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_disassociate_TGW_resource_share_ga.zip"
  function_name = "platform_disassociate_TGW_resource_share_ga"
  role          = var.role_arn
  handler       = "platform_disassociate_TGW_resource_share_ga.lambda_handler"
  source_code_hash = data.archive_file.disassociate_tgw_resource_share_ga_lambda_zip.output_base64sha256

  runtime = "python3.9"
  memory_size = 512
  timeout = 900

  vpc_config {
    subnet_ids         = [aws_subnet.create_tgw_pvt_subnet_1.id, aws_subnet.create_tgw_pvt_subnet_2.id]
    security_group_ids = [aws_security_group.tgw_sg.id]
  }
  layers = [var.requests_layer]

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# TGW Details DynamoDB Table
resource "aws_dynamodb_table" "tgw_details_dynamodb_table" {
  name           = "TGWDetailsTable"
  read_capacity  = 5
  write_capacity = 5
  hash_key       = "TransitgatewayId"
  point_in_time_recovery { 
    enabled = true 
  }

  attribute {
    name = "TransitgatewayId"
    type = "S"
  }

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# TGW Integration State Machine GA
resource "aws_sfn_state_machine" "tgw_integartion_state_machine_ga" {
  name     = "platform_tgw_attachment_automation_ga"
  role_arn = var.role_arn
  type = "STANDARD"

  definition = data.template_file.tgw_integration_state_machine_template_ga.rendered

  tags = {
    "platform_donotdelete" = "yes"
  }
}