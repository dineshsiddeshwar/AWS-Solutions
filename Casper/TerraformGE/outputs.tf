output "autoscaling_group_name" {
  description = "The name of the Auto Scaling Group"
  value       = module.asg.asg_name
}

output "network_load_balancer_dns" {
  description = "DNS name of the Network Load Balancer"
  value       = module.nlb.dns_name
}
