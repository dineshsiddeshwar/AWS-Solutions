output "network_address_type" {
    value = "This the VPC using ${var.network_address_type} IP Address"
}

output "VPC_deployment_region" {
    value = "This VPC is being deployed in ${var.vpc_deployment_region}."
}

output "VPC_security_group" {
    value = "Security group employed in this VPC is as follows ${aws_security_group.vpc_sg.name}"
}