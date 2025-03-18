provider "aws" {
  region = "us-east-1"  # Replace with your desired region
}

resource "aws_vpc" "my_vpc" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "my_subnet" {
  vpc_id     = aws_vpc.my_vpc.id
  cidr_block = "10.0.0.0/24"
  availability_zone = "us-east-1a"  # Replace with your desired AZ
}

resource "aws_instance" "my_instance" {
  ami           = "ami-08a52ddb321b32a8c"  # Replace with a valid AMI ID
  instance_type = "t2.micro"
  subnet_id     = aws_subnet.my_subnet.id
  associate_public_ip_address = false  # Prevent public IP assignment

  # Other instance configuration, like key_name, security_groups, etc.
}
