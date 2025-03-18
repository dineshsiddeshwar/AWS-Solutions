aws_region                = "us-east-1"
desired_capacity          = 4
min_size                  = 2
max_size                  = 6
subnet_ids                = ["subnet-026143ad47e006098", "subnet-0e82682cb264b4a42"]
tag_key                   = "environment"
tag_value                 = "stageauthsso"
managed_policy_arns       = ["arn:aws:iam::aws:policy/service-role/AmazonEC2RoleforSSM", "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore", "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy", "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"]
tags                      = {
  environment             = "stageauthsso"
}
ami_id                    = "ami-0368895eb628758f1"
admin_instance_type       = "t2.large"
subnet_id                 = "subnet-026143ad47e006098"
engine_node_instance_type = "t2.medium"
volume_size               = 15
volume_type               = "gp3"
kms_key_arn               = "arn:aws:kms:us-east-1:463470952406:key/f2bf3b47-16ee-4aab-889d-d6cf1ffc14e0"
instance_tags             = {
  environment             = "stageauthsso"
  uai                     = "UAI3046824"
}
volume_tags               = {
  environment             = "stageauthsso"
  uai                     = "UAI3046824"
}
vpc_id                    = "vpc-09ed6a3d438396cac"


