data "aws_route53_resolver_rule" "list_resolver_rules" {
  for_each = var.RegionIpDictionary

  domain_name         = "shell.com"
  rule_type           = "FORWARD"
}

resource "aws_route53_resolver_rule_association" "associate_resolver_rule" {
  for_each = var.RegionIpDictionary
  
  resolver_rule_id = data.aws_route53_resolver_rule.list_resolver_rules[each.key].id
  vpc_id           = aws_vpc.create_vpc_in_child_account[each.key].id
  name             = "platform_ResolverRuleAssociation"
}

data "aws_route53_resolver_rule" "list_resolver_rule_Shell_io" {
  for_each = var.RegionIpDictionary

  domain_name         = "ops.aws.shell.io"
  rule_type           = "FORWARD"
}

resource "aws_route53_resolver_rule_association" "associate_resolver_rule_shell_io" {
  for_each = var.RegionIpDictionary
  
  resolver_rule_id = data.aws_route53_resolver_rule.list_resolver_rule_Shell_io[each.key].id
  vpc_id           = aws_vpc.create_vpc_in_child_account[each.key].id
  name             = "platform_ResolverRuleAssociation_Shell_io"
}

data "aws_route53_resolver_rule" "list_resolver_rule_Shell" {
  for_each = var.RegionIpDictionary

  domain_name         = "shell"
  rule_type           = "FORWARD"
}

resource "aws_route53_resolver_rule_association" "associate_resolver_rule_shell" {
  for_each = var.RegionIpDictionary
  
  resolver_rule_id = data.aws_route53_resolver_rule.list_resolver_rule_Shell[each.key].id
  vpc_id           = aws_vpc.create_vpc_in_child_account[each.key].id
  name             = "platform_ResolverRuleAssociation_Shell"
}