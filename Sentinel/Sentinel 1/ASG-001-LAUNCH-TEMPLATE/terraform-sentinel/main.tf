resource "aws_launch_template" "Template" {
  name = "Template"
  
   cpu_options {
    core_count       = 4
    threads_per_core = 2
  }

  image_id = "ami-test"
  
  instance_type = "t2.micro"

  network_interfaces {
    associate_public_ip_address = true
  }
 
}