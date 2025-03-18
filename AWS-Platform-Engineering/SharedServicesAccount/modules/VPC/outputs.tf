output "vpc_id" {
  description = "The ID of the VPC"
  value       = try(aws_vpc.shared_vpc[0].id, null)
}

output "vpc_arn" {
  description = "The ARN of the VPC"
  value       = try(aws_vpc.shared_vpc[0].arn, null)
}

output "vpc_cidr_block" {
  description = "The CIDR block of the VPC"
  value       = try(aws_vpc.shared_vpc[0].cidr_block, null)
}

# Access the specific subnet's attributes using the data resource

# output "sharedsubnet1a" {
#   value = [for subnet in data.aws_subnet.platform-shared-subnet-1A : subnet.id]
# }

# output "sharedsubnet1b" {
#   value = [for subnet in data.aws_subnet.platform-shared-subnet-1B : subnet.id]
# }


output "sharedsubnet1a" {
  value = [aws_subnet.subnet1a[0].id]
  
}

output "sharedsubnet1b" {
  value = [aws_subnet.subnet1b[0].id]
  
}

output "sharedsubnet2a" {
  value = var.isproduction == false ? [aws_subnet.subnet2a[0].id] : null
  
}

output "sharedsubnet2b" {
  value = var.isproduction == false ? [aws_subnet.subnet2b[0].id] : null
  
}


