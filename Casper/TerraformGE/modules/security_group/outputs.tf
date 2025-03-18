output "instance_security_group_id" {
  value = aws_security_group.instance_sg.id
}

output "nlb_security_group_id" {
  value = aws_security_group.nlb_sg.id
}

output "endpoint_security_group_id" {
  value = aws_security_group.endpoint_sg.id
}