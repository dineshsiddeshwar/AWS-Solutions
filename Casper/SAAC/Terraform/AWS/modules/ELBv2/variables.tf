variable "elbv2_region" {
    type = string
    description = "The region where elbv2 should be deployed"
    default = "us-west-1"
}


variable "elbv2_subnet_region" {
    type = map
    default = {
        "us-west-1": ["us-west-1b", "us-west-1c"],
        "us-west-2": ["us-west-2a","us-west-2b","us-west-2c","us-west-2d"],
        "us-east-1": ["us-east-1a","us-east-1b","us-east-1c","us-east-1d","us-east-1e","us-east-1f"],
        "us-east-2": ["us-east-2b","us-east-2c","us-east-2d"]
    }
}

variable "elbv2_s3_bucket" {
    type = string
    description = "This is the S3 bucket to log the applicaiton load balancer values"
    default = "my-casper-logs"
}

variable "elbv2_security_group_values" {
    type = list(object({
      from_port = number
      to_port = number
      protocol = string
      cidr_block = list(string)
    }))
    description = "Security groups for the application load balancer"
    default = [
        {
      from_port = 3306
      to_port = 3306
      protocol = "tcp"
      cidr_block = [ "10.0.0.0/16" ]
        },
        {
      from_port = 3306
      to_port = 3306
      protocol = "tcp"
      cidr_block = [ "10.0.0.0/16" ]
        }
    ]
}