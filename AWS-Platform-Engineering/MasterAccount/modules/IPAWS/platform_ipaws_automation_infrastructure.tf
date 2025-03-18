# SCIM IPAWS DynamoDB Table
resource "aws_dynamodb_table" "scim_ipaws_dynamodb_table" {
  name           = "SCIMIPAWSDetails"
  read_capacity  = 5
  write_capacity = 5
  hash_key       = "AccountNumber"
  point_in_time_recovery { 
    enabled = true 
  }

  attribute {
    name = "AccountNumber"
    type = "S"
  }

  attribute {
    name = "AssociationStatus"
    type = "S"
  }

  global_secondary_index {
    name               = "SCIMStatus"
    hash_key           = "AssociationStatus"
    write_capacity     = 5
    read_capacity      = 5
    projection_type    = "ALL"
  }
}

# IPAWS VPC Creation
resource "aws_vpc" "create_ipaws_vpc_in_master_account" {
  cidr_block       = var.ipaws_vpc_cidr
  instance_tenancy = "default"
  enable_dns_support = true
  enable_dns_hostnames = true

  tags = {
    Name = "AAD-IPAWS-vpc",
    platform_donotdelete = "yes"
  }
}

# IPAWS Private Subnet 1 Creation
resource "aws_subnet" "create_ipaws_pvt_subnet_1" {
  vpc_id     = aws_vpc.create_ipaws_vpc_in_master_account.id
  cidr_block = var.ipaws_pvt_subnet_cidr_1
  availability_zone = "us-east-1a"
  map_public_ip_on_launch = true

  tags = {
    Name = "AAD-IPAWS-subnet-private1-us-east-1a"
  }
}

# IPAWS Private Subnet 2 Creation
resource "aws_subnet" "create_ipaws_pvt_subnet_2" {
  vpc_id     = aws_vpc.create_ipaws_vpc_in_master_account.id
  cidr_block = var.ipaws_pvt_subnet_cidr_2
  availability_zone = "us-east-1b"
  map_public_ip_on_launch = true

  tags = {
    Name = "AAD-IPAWS-subnet-private2-us-east-1b"
  }
}

# IPAWS Public Subnet 1 Creation
resource "aws_subnet" "create_ipaws_pub_subnet_1" {
  vpc_id     = aws_vpc.create_ipaws_vpc_in_master_account.id
  cidr_block = var.ipaws_pub_subnet_cidr_1
  availability_zone = "us-east-1a"
  map_public_ip_on_launch = true

  tags = {
    Name = "AAD-IPAWS-subnet-public1-us-east-1a"
  }
}

# IPAWS Public Subnet 2 Creation
resource "aws_subnet" "create_ipaws_pub_subnet_2" {
  vpc_id     = aws_vpc.create_ipaws_vpc_in_master_account.id
  cidr_block = var.ipaws_pub_subnet_cidr_2
  availability_zone = "us-east-1b"
  map_public_ip_on_launch = true

  tags = {
    Name = "AAD-IPAWS-subnet-public2-us-east-1b"
  }
}

#IPAWS Internet Gateway Creation
resource "aws_internet_gateway" "ipaws_vpc_igw" {
  vpc_id = aws_vpc.create_ipaws_vpc_in_master_account.id

  tags = {
    Name = "AAD-IPAWS-igw"
  }
}

#IPAWS Internet Gateway Attachment Creation
resource "aws_internet_gateway_attachment" "ipaws_vpc_igw_attachment" {
  internet_gateway_id = aws_internet_gateway.ipaws_vpc_igw.id
  vpc_id              = aws_vpc.create_ipaws_vpc_in_master_account.id
}

#IPAWS Elastic IP Creation
resource "aws_eip" "ipaws_eip_1" {
  vpc                       = true
  tags = {
    Name = "AAD-IPAWS-eip-us-east-1a"
  }
}

resource "aws_eip" "ipaws_eip_2" {
  vpc                       = true
  tags = {
    Name = "AAD-IPAWS-eip-us-east-1b"
  }
}

#IPAWS NatGateway Creation
resource "aws_nat_gateway" "ipaws_vpc_nat_gw_1" {
  allocation_id = aws_eip.ipaws_eip_1.id
  subnet_id     = aws_subnet.create_ipaws_pub_subnet_1.id

  tags = {
    Name = "AAD-IPAWS-nat-public1-us-east-1a"
  }

  # To ensure proper ordering, it is recommended to add an explicit dependency
  # on the Internet Gateway for the VPC.
  depends_on = [aws_internet_gateway.ipaws_vpc_igw]
}

resource "aws_nat_gateway" "ipaws_vpc_nat_gw_2" {
  allocation_id = aws_eip.ipaws_eip_2.id
  subnet_id     = aws_subnet.create_ipaws_pub_subnet_2.id

  tags = {
    Name = "AAD-IPAWS-nat-public2-us-east-1b"
  }

  # To ensure proper ordering, it is recommended to add an explicit dependency
  # on the Internet Gateway for the VPC.
  depends_on = [aws_internet_gateway.ipaws_vpc_igw]
}

#IPAWS Private Route Table 1 Creation
resource "aws_route_table" "ipaws_vpc_pvt_rt_1" {
  vpc_id = aws_vpc.create_ipaws_vpc_in_master_account.id

  route {
    cidr_block = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.ipaws_vpc_nat_gw_1.id
  }

  tags = {
    Name = "AAD-IPAWS-rtb-Private1-us-east-1a"
  }
}

#IPAWS Private Route Table 1 Association Creation
resource "aws_route_table_association" "ipaws_vpc_pvt_rt_1_association" {
  subnet_id      = aws_subnet.create_ipaws_pvt_subnet_1.id
  route_table_id = aws_route_table.ipaws_vpc_pvt_rt_1.id
}

#IPAWS Private Route Table 2 Creation
resource "aws_route_table" "ipaws_vpc_pvt_rt_2" {
  vpc_id = aws_vpc.create_ipaws_vpc_in_master_account.id

  route {
    cidr_block = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.ipaws_vpc_nat_gw_2.id
  }

  tags = {
    Name = "AAD-IPAWS-rtb-Private2-us-east-1b"
  }
}

#IPAWS Private Route Table 2 Association Creation
resource "aws_route_table_association" "ipaws_vpc_pvt_rt_2_association" {
  subnet_id      = aws_subnet.create_ipaws_pvt_subnet_2.id
  route_table_id = aws_route_table.ipaws_vpc_pvt_rt_2.id
}

#IPAWS Public Route Table 1 Creation
resource "aws_route_table" "ipaws_vpc_pub_rt_1" {
  vpc_id = aws_vpc.create_ipaws_vpc_in_master_account.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.ipaws_vpc_igw.id
  }

  tags = {
    Name = "AAD-IPAWS-rtb-Public1-us-east-1a"
  }
}

#IPAWS Public Route Table 1 Association Creation
resource "aws_route_table_association" "ipaws_vpc_pub_rt_1_association" {
  subnet_id      = aws_subnet.create_ipaws_pub_subnet_1.id
  route_table_id = aws_route_table.ipaws_vpc_pub_rt_1.id
}

#IPAWS Public Route Table 2 Creation
resource "aws_route_table" "ipaws_vpc_pub_rt_2" {
  vpc_id = aws_vpc.create_ipaws_vpc_in_master_account.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.ipaws_vpc_igw.id
  }

  tags = {
    Name = "AAD-IPAWS-rtb-Public2-us-east-1b"
  }
}

#IPAWS Public Route Table 2 Association Creation
resource "aws_route_table_association" "ipaws_vpc_pub_rt_2_association" {
  subnet_id      = aws_subnet.create_ipaws_pub_subnet_2.id
  route_table_id = aws_route_table.ipaws_vpc_pub_rt_2.id
}

#IPAWS Security Group Creation
resource "aws_security_group" "ipaws_sg" {
  name        = "AAD-IPAWS-sg"
  description = "Security group for AAD-IPAWS integration"
  vpc_id      = aws_vpc.create_ipaws_vpc_in_master_account.id
}

#IPAWS Lambda Definition for VPC Based lambda
resource "aws_lambda_function" "ipaws_integration_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_ipaws_integration.zip"
  function_name = "platform_ipaws_integration"
  role          = var.role_arn
  handler       = "platform_ipaws_integration.lambda_handler"
  source_code_hash = data.archive_file.ipaws_integration_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 128
  timeout = 900

  vpc_config {
    subnet_ids         = [aws_subnet.create_ipaws_pvt_subnet_1.id, aws_subnet.create_ipaws_pvt_subnet_2.id]
    security_group_ids = [aws_security_group.ipaws_sg.id]
  }
  layers = [var.requests_layer, var.cryptography_layer, var.msal_layer, var.pyjwt_layer, var.cffi_layer]

  tags = {
    "platform_donotdelete" = "yes"
  }
}

