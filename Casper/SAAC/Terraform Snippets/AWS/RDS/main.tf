resource "aws_vpc" "rds_main" {
  cidr_block = "10.0.0.0/16"
  
  tags = {
    Name = "main"
  }
}

resource "aws_subnet" "db_subnet_a" {

  cidr_block              = "10.0.1.0/24"
  vpc_id                  = aws_vpc.rds_main.id
  availability_zone       = var.db_subnet_region[0]
  
  tags = {
    Name = "rds-subnet-A"
  }
}

resource "aws_subnet" "db_subnet_b" {

  cidr_block              = "10.0.2.0/24"
  vpc_id                  = aws_vpc.rds_main.id
  availability_zone       = var.db_subnet_region[1]
  

  tags = {
    Name = "rds-subnet-B"
  }
}

resource "aws_security_group" "rds_sg" {
  name        = "rds-security-group"
  description = "Security group for RDS instance"
  vpc_id = aws_vpc.rds_main.id
  // Add inbound and outbound rules as needed
  
  ingress {
    from_port   = tonumber(var.db_instance_ingress_access["from_port"][0])
    to_port     = tonumber(var.db_instance_ingress_access["to_port"][0])
    protocol    = var.db_instance_ingress_access["protocol"][0]
    cidr_blocks = [aws_subnet.db_subnet_a.cidr_block,aws_subnet.db_subnet_b.cidr_block]
  }

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = var.db_instance_ingress_access["protocol"][0]
    cidr_blocks      = ["0.0.0.0/0"]
  }
}

resource "aws_db_subnet_group" "rds_subnet_group" {
  name       = "rds-subnet-group"
  subnet_ids = [aws_subnet.db_subnet_a.id,aws_subnet.db_subnet_b.id]

  tags = {
    Name = "RDS Subnet Group"
  }
}

resource "aws_db_instance" "mysqldb" {
  allocated_storage    = var.db_allocated_storage
  storage_type        = var.db_storage_type
  engine              = var.db_engine
  engine_version      = var.db_engine_version
  instance_class      = var.db_instance_class
  username            = var.db_username
  password            = var.db_password
  parameter_group_name = var.db_parameter_group_name

  skip_final_snapshot = var.db_skip_final_snapshot

  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  db_subnet_group_name   = aws_db_subnet_group.rds_subnet_group.name

  backup_retention_period = var.db_backup_retention_period // Number of days to retain backups

  deletion_protection = var.db_deletion_protection // Enable deletion protection

  tags = {
    Name = "RDS Example"
  }
}