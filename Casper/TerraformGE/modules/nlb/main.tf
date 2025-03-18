resource "aws_lb" "nlb" {
  name               = "network-lb"
  internal           = true
  load_balancer_type = "network"
  subnets            = var.subnet_ids
  security_groups    = var.security_groups
  tags               = var.tags
}

resource "aws_lb_listener" "nlb_listener" {
  load_balancer_arn = aws_lb.nlb.arn
  port              = "443"
  protocol          = "TLS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = "arn:aws:acm:us-east-1:463470952406:certificate/84a3ad2c-dc41-4492-bdce-5cfaff86ce2c"

  default_action {
    type             = "forward"
    target_group_arn = var.target_group_arn
  }
}


