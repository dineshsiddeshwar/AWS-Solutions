// add the provider block as "aws"

resource "aws_db_instance" "mysqldb" {
  allocated_storage    = 20
  storage_type        = "gp2"
  engine              = "mysql"
  engine_version      = "5.7"
  instance_class      = "db.t2.micro"
  username            = "sentinel_trainer" //add someone name for the username
  password            = "aws_rds_password"
  parameter_group_name = "default.mysql5.7"
  backup_retention_period = 10

  tags = {
    Name = "Sentinel trainer RDS"
  }
}
