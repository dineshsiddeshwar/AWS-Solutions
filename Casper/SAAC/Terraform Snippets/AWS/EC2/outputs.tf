output "instance_id" {
  description = "Public IP address of the EC2 instance"
  value       = aws_instance.ec2_instance.id
}
