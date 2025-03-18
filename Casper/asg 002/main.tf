provider "aws" {
  region = "us-west-2"
  
}

resource "aws_vpc" "main" {
  cidr_block       = "10.0.0.0/16"
  instance_tenancy = "default"

  tags = {
    Name = "main"
  }
}

resource "aws_subnet" "my_subnet1" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.13.0/24"
  availability_zone = "us-west-2a"

  tags = {
    Name = "tf-subnet1"
  }
}

resource "aws_subnet" "my_subnet2" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.0.0/24"
  availability_zone = "us-west-2b"

  tags = {
    Name = "tf-subnet2"
  }
}

resource "aws_launch_configuration" "as_conf" {
  
  image_id      = "ami-098e42ae54c764c35"
  instance_type = "t2.micro"
  associate_public_ip_address = false
  
}
 

resource "aws_autoscaling_group" "asgasg1" {
  name   = "terraform-asg-example"
  vpc_zone_identifier = [aws_subnet.my_subnet1.id, aws_subnet.my_subnet2.id]
  max_size = 5
  min_size = 2
  launch_configuration = aws_launch_configuration.as_conf.name
}
