output "aws_instance_name_created" {
    value = aws_instance.casper_instance.tags.Name
}

output "security_group_for_EC2" {
    value = aws_security_group.casper_sg
}

output "VPC_created" {
    value = aws_vpc.casper_vpc.tags.Name
}

output "public_ip" {
    value = aws_instance.casper_instance.public_ip
}
