resource "aws_route53_resolver_endpoint" "shell_domain_resolver" {
  direction = "OUTBOUND"
  name      = "platform_Shell_Domain_Resolver"

  ip_address {
    ip=var.endpoint_ips_subnet1a[0]
    subnet_id = var.sharedsubnet1a[0]
  }
  ip_address {
    ip=var.endpoint_ips_subnet1a[1]
    subnet_id = var.sharedsubnet1a[0]
  }
  ip_address {
    ip=var.endpoint_ips_subnet1a[2]
    subnet_id = var.sharedsubnet1a[0]
  }
  ip_address {
    ip=var.endpoint_ips_subnet1b[0]
    subnet_id = var.sharedsubnet1b[0]
  }
  ip_address {
    ip=var.endpoint_ips_subnet1b[1]
    subnet_id = var.sharedsubnet1b[0]
  }
  ip_address {
    ip=var.endpoint_ips_subnet1b[2]
    subnet_id = var.sharedsubnet1b[0]
  }

  security_group_ids = var.security_group_ids
}


resource "aws_route53_resolver_rule" "shell_domain_forwarder_rule" {
  domain_name         = "shell.com"
  name                = "platform_Shell_Domain_Forwarder_Outbound_Rule"
  resolver_endpoint_id = aws_route53_resolver_endpoint.shell_domain_resolver.id
  rule_type           = "FORWARD"
  tags = {
    "platform_donotdelete" = "yes"
  }
  
  target_ip {
    ip = "134.162.23.1"
    port = "53"
  }

  target_ip {
    ip = "134.162.23.2"
    port = "53"
  }

  dynamic "target_ip" {
    for_each = var.region!="ap-southeast-1" ? [3, 4] : []
    content {
      ip   = target_ip.value == 3 ? var.Infoblox1 : var.Infoblox2
      port = "53"
    }
  }
}

resource "aws_route53_resolver_rule" "shell_domain_forwarder_rule_shell" {
  domain_name         = "shell"
  name                = "platform_Shell_shell_Domain_Forwarder_Outbound_Rule"
  resolver_endpoint_id = aws_route53_resolver_endpoint.shell_domain_resolver.id
  rule_type           = "FORWARD"
  tags = {
    "platform_donotdelete" = "yes"
  }
  
  target_ip {
    ip = "134.162.23.1"
    port = "53"
  }

  target_ip {
    ip = "134.162.23.2"
    port = "53"
  }

  dynamic "target_ip" {
    for_each = var.region!="ap-southeast-1" ? [3, 4] : []
    content {
      ip   = target_ip.value == 3 ? var.Infoblox1 : var.Infoblox2
      port = "53"
    }
  }
}

resource "aws_route53_resolver_rule" "shell_domain_forwarder_rule_io" {
  domain_name         = "ops.aws.shell.io"
  name                = "platform_Shell_io_Domain_Forwarder_Outbound_Rule"
  resolver_endpoint_id = aws_route53_resolver_endpoint.shell_domain_resolver.id
  rule_type           = "FORWARD"
  tags = {
    "platform_donotdelete" = "yes"
  }
  
  target_ip {
    ip = "10.223.68.119"
    port = "53"
  }

  target_ip {
    ip = "10.223.73.204"
    port = "53"
  }

  target_ip {
    ip = "10.223.65.193"
    port = "53"
  }
}

resource "aws_route53_resolver_rule" "sga_res_domain_forwarder_rule" {
  domain_name         = "sga-res.com"
  name                = "platform_Sga_Res_Azure_Domain_Forwarder_Outbound_Rule"
  resolver_endpoint_id = aws_route53_resolver_endpoint.shell_domain_resolver.id
  rule_type           = "FORWARD"
  tags = {
    "platform_donotdelete" = "yes"
  }
  
  target_ip {
    ip = "134.162.23.1"
    port = "53"
  }

  target_ip {
    ip = "134.162.23.2"
    port = "53"
  }

  dynamic "target_ip" {
    for_each = var.region!="ap-southeast-1" ? [3, 4] : []
    content {
      ip   = target_ip.value == 3 ? var.Infoblox1 : var.Infoblox2
      port = "53"
    }
  }
}


resource "aws_route53_resolver_rule_association" "shell_domain_forwarder_rule_association" {
  name            = aws_route53_resolver_rule.shell_domain_forwarder_rule.name
  resolver_rule_id = aws_route53_resolver_rule.shell_domain_forwarder_rule.id
  vpc_id          = var.vpc_id
}

resource "aws_route53_resolver_rule_association" "shell_domain_forwarder_rule_association_shell" {
  name            = aws_route53_resolver_rule.shell_domain_forwarder_rule_shell.name
  resolver_rule_id = aws_route53_resolver_rule.shell_domain_forwarder_rule_shell.id
  vpc_id          = var.vpc_id
}

resource "aws_route53_resolver_rule_association" "shell_domain_forwarder_rule_association_io" {
  name            = aws_route53_resolver_rule.shell_domain_forwarder_rule_io.name
  resolver_rule_id = aws_route53_resolver_rule.shell_domain_forwarder_rule_io.id
  vpc_id          = var.vpc_id
}

resource "aws_route53_resolver_rule_association" "sga_res_domain_forwarder_rule_association" {
  name            = aws_route53_resolver_rule.sga_res_domain_forwarder_rule.name
  resolver_rule_id = aws_route53_resolver_rule.sga_res_domain_forwarder_rule.id
  vpc_id          = var.vpc_id
}


resource "aws_ram_resource_share" "shell_domain_resolver_share" {
  name = "platform_Shell_Domain_Resolver_Rule_Share"
  allow_external_principals = true

  tags = {
    "platform_donotdelete" = "yes"
  }
  
}

resource "aws_ram_resource_share" "shell_domain_shell_resolver_share" {
  name = "platform_Shell_shell_Domain_Resolver_Rule_Share"
  allow_external_principals = true

  tags = {
    "platform_donotdelete" = "yes"
  }
  
}

resource "aws_ram_resource_share" "shell_domain_io_resolver_share" {
  name = "platform_Shell_io_Domain_Resolver_Rule_Share"
  allow_external_principals = true

  tags = {
    "platform_donotdelete" = "yes"
  }
  
}

resource "aws_ram_resource_share" "sga_res_domain_resolver_share" {
  name = "platform_Sga_Res_Resolver_Rule_Share"
  allow_external_principals = true

  tags = {
    "platform_donotdelete" = "yes"
  }
  
}


resource "aws_ram_resource_association" "shell_domain_forwarder_rule_ram_association" {
  resource_arn       = aws_route53_resolver_rule.shell_domain_forwarder_rule.arn
  resource_share_arn = aws_ram_resource_share.shell_domain_resolver_share.arn
}

resource "aws_ram_resource_association" "shell_domain_forwarder_rule_shell_ram_association" {
  resource_arn       = aws_route53_resolver_rule.shell_domain_forwarder_rule_shell.arn
  resource_share_arn = aws_ram_resource_share.shell_domain_shell_resolver_share.arn
}

resource "aws_ram_resource_association" "shell_domain_forwarder_rule_io_ram_association" {
  resource_arn       = aws_route53_resolver_rule.shell_domain_forwarder_rule_io.arn
  resource_share_arn = aws_ram_resource_share.shell_domain_io_resolver_share.arn
}

resource "aws_ram_resource_association" "sga_res_domain_forwarder_rule_ram_association" {
  resource_arn       = aws_route53_resolver_rule.sga_res_domain_forwarder_rule.arn
  resource_share_arn = aws_ram_resource_share.sga_res_domain_resolver_share.arn
}


resource "aws_ram_principal_association" "this" {
  for_each = var.ou_principals
  principal          = each.value
  resource_share_arn = aws_ram_resource_share.shell_domain_resolver_share.arn
}

resource "aws_ram_principal_association" "shell_domain_shell_principal_association" {
  for_each = var.ou_principals
  principal          = each.value
  resource_share_arn = aws_ram_resource_share.shell_domain_shell_resolver_share.arn
}

resource "aws_ram_principal_association" "shell_domain_io_principal_association" {
  for_each = var.ou_principals
  principal          = each.value
  resource_share_arn = aws_ram_resource_share.shell_domain_io_resolver_share.arn
}

resource "aws_ram_principal_association" "sga_res_principal_association" {
  for_each = var.ou_principals
  principal          = each.value
  resource_share_arn = aws_ram_resource_share.sga_res_domain_resolver_share.arn
}