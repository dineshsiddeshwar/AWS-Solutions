output "load_balancer_type" {
    value = "The Load Balancer type: ${aws_lb.casper.load_balancer_type}"
}

output "load_balancer_name"{
    value = "The load balancer name: ${aws_lb.casper.name}"
}

output "load_balancer_bucket" {
    value ="Bucket name to store the access logs: ${aws_s3_bucket.lb_logs.tags.Name}"
}