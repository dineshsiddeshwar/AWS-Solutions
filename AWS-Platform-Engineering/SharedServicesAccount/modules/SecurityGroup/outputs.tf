output "security_group_id" {
    value = try(aws_security_group.sharedvpcsecgroup[0].id,null)
  
}