variable "ec2_region" {
    type = string
    default = "us-west-1"
    description = "this is the region set for EC2 for linux OS t2.micro"
}

variable "ec2_aws_instance" {
    type = string
    default = "t2.micro"
}

variable "ec2_aws_ami" {
    type = map
    default = {
        "us-west-1": "ami-03f2f5212f24db70a",
        "us-west-2": "ami-002829755fa238bfa",
        "us-east-1": "ami-051f7e7f6c2f40dc1",
        "us-east-2": "ami-0cf0e376c672104d6"
    }
}

variable "ec2_subnet_region" {
    type = map
    default = {
        "us-west-1": ["us-west-1b", "us-west-1c"],
        "us-west-2": ["us-west-2a","us-west-2b","us-west-2c","us-west-2d"],
        "us-east-1": ["us-east-1a","us-east-1b","us-east-1c","us-east-1d","us-east-1e","us-east-1f"],
        "us-east-2": ["us-east-2b","us-east-2c","us-east-2d"]
    }
}