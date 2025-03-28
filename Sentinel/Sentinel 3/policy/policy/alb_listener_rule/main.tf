terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "4.63.0"
    }
  }
}

provider "aws" {
  region = "us-west-2"
  shared_credentials_files = ["/users/DT495QF/.aws/credentials"]
}

resource "aws_lb" "frontend"{}

resource "aws_lb_listener" "front_end" {
  load_balancer_arn = aws_lb.frontend.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type = "redirect"

    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

resource "aws_lb_listener_rule" "redirect_http_to_https" {
  listener_arn = aws_lb_listener.front_end.arn

  action {
    type = "redirect"

    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }

  condition {
    http_header {
      http_header_name = "X-Forwarded-For"
      values           = ["192.168.1.*"]
    }
  }
}