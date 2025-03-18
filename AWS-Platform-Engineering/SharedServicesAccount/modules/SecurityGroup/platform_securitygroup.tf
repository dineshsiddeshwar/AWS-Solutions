##################################
# Get ID of created Security Group
##################################
locals {
  create = var.create
  
}

##########################
# Security group with name
##########################
resource "aws_security_group" "sharedvpcsecgroup" {
  count = local.create ? 1 : 0

  name                   = var.name
  description            = "Shared VPC Security Group"
  vpc_id                 = var.vpc_id
  revoke_rules_on_delete = var.revoke_rules_on_delete

  ingress {
    from_port = 0
    to_port = 0
    protocol = -1
    cidr_blocks = var.ingress_cidr_blocks
  }
}

# ###################################
# # Ingress - List of rules (simple)
# ###################################
# # Security group rules with "cidr_blocks" and it uses list of rules names
# resource "aws_security_group_rule" "ingress_rules" {
#   count = local.create ? length(var.ingress_rules) : 0

#   security_group_id = aws_security_group.sharedvpcsecgroup[0].id
#   type              = "ingress"

#   cidr_blocks      = var.ingress_cidr_blocks
#   description      = var.rules[var.ingress_rules[count.index]][3]

#   from_port = var.rules[var.ingress_rules[count.index]][0]
#   to_port   = var.rules[var.ingress_rules[count.index]][1]
#   protocol  = var.rules[var.ingress_rules[count.index]][2]
# }
