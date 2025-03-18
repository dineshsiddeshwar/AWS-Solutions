resource "aws_instance" "instance" {
  ami           = var.ami_id
  instance_type = var.admin_instance_type
  subnet_id     = var.subnet_id

  launch_template {
    id      = var.instance_template
    version = "$Latest"
  }
}