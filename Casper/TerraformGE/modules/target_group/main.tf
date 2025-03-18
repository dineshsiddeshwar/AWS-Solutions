resource "aws_lb_target_group" "tg" {
  name        = "target-group"
  port        = 80
  protocol    = "TCP"
  vpc_id      = var.vpc_id
  tags        = var.tags
}