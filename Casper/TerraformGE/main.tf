module "asg" {
  source                   = "./modules/asg"
  desired_capacity         = var.desired_capacity
  min_size                 = var.min_size
  max_size                 = var.max_size
  instance_template        = module.instance_template.launch_template_id
  subnet_ids               = var.subnet_ids
  target_group_arn         = module.target_group.target_group_arn
  tag_key                  = var.tag_key
  tag_value                = var.tag_value
}

module "iam_role" {
  source                   = "./modules/iam_role"
  managed_policy_arns      = var.managed_policy_arns
  tags                     = var.tags
}

module "instance" {
  source                   = "./modules/instance"
  ami_id                   = var.ami_id
  admin_instance_type      = var.admin_instance_type
  subnet_id                = var.subnet_id
  instance_template        = module.instance_template.launch_template_id
}

module "instance_template" {
  source                   = "./modules/instance_template"
  role_name                = module.iam_role.role_name
  ami_id                   = var.ami_id
  engine_node_instance_type = var.engine_node_instance_type
  security_groups          = [module.security_group.instance_security_group_id]
  subnet_id                = var.subnet_id
  volume_size              = var.volume_size
  volume_type              = var.volume_type
  kms_key_arn              = var.kms_key_arn
  instance_tags            = var.instance_tags
  volume_tags              = var.volume_tags
  tags                     = var.tags
}

module "nlb" {
  source                   = "./modules/nlb"
  subnet_ids               = var.subnet_ids
  security_groups          = [module.security_group.nlb_security_group_id]
  tags                     = var.tags
  target_group_arn         = module.target_group.target_group_arn
}

module "security_group" {
  source                   = "./modules/security_group"
  vpc_id                   = var.vpc_id
  tags                     = var.tags
}

module "target_group" {
  source                   = "./modules/target_group"
  vpc_id                   = var.vpc_id
  tags                     = var.tags
}

module "vpc_endpoint" {
  source                   = "./modules/vpc_endpoint"
  vpc_id                   = var.vpc_id
  aws_region               = var.aws_region
  subnet_ids               = var.subnet_ids
  security_group_ids       = [module.security_group.endpoint_security_group_id]
  tags                     = var.tags
}
