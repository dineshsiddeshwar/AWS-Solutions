resource "aws_autoscaling_group" "asg" {
  desired_capacity     = var.desired_capacity
  min_size             = var.min_size
  max_size             = var.max_size
  launch_template {
    id      = var.instance_template
    version = "$Latest"
  }
  vpc_zone_identifier = var.subnet_ids
  target_group_arns   = [var.target_group_arn]
  tag {
    key                 = var.tag_key
    value               = var.tag_value
    propagate_at_launch = false
  }
}
