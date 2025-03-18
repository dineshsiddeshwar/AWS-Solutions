################################################################################
# Endpoint(s)
################################################################################

locals {
  endpoints = { for k, v in var.endpoints : k => v if var.create && try(v.create, true) }
}

resource "aws_vpc_endpoint" "this" {
  for_each = local.endpoints

  vpc_id            = var.vpc_id
  service_name      = "com.amazonaws.${var.region}.${each.value.service_name_suffix}"
  vpc_endpoint_type = lookup(each.value, "service_type", "Interface")

  security_group_ids  = var.security_group_ids
  subnet_ids          = var.isproduction && (each.key!="comprehend-Endpoint" && each.key!="dms-Endpoint")? distinct(concat(var.sharedsubnet1a, var.sharedsubnet1b)) : var.sharedsubnet1a
  policy              = lookup(each.value, "policy", null)
  private_dns_enabled = lookup(each.value, "private_dns_enabled", false)

  tags = merge(var.tags, lookup(each.value, "tags", {}))
}

# resource block for newly created endpoints using extended vpc subnets

resource "aws_vpc_endpoint" "this_extended" {
  for_each = var.endpoint_extended

  vpc_id            = var.vpc_id
  service_name      = "com.amazonaws.${var.region}.${each.value.service_name_suffix}"
  vpc_endpoint_type = lookup(each.value, "service_type", "Interface")

  security_group_ids  = var.security_group_ids
  subnet_ids          = var.isproduction ? distinct(concat(var.sharedsubnet1a, var.sharedsubnet1b)) : (each.value.subnet_ids!=null ? each.value.subnet_ids : var.sharedsubnet2b)
  policy              = lookup(each.value, "policy", null)
  private_dns_enabled = lookup(each.value, "private_dns_enabled", false)

  tags = merge(var.tags, lookup(each.value, "tags", {}))
}


resource "aws_route53_zone" "this" {
  for_each = local.endpoints
  name = each.value.hostedzone_suffix != null ? "${each.value.hostedzone_suffix}.${var.region}.amazonaws.com" : "${each.value.service_name_suffix}.${var.region}.amazonaws.com"
  vpc {
    vpc_id     = var.vpc_id
    vpc_region = var.region
  }

  lifecycle {
    ignore_changes = [
      vpc
    ]
  }
  
}

resource "aws_route53_record" "this" {
  for_each = local.endpoints
  zone_id = aws_route53_zone.this[each.key].zone_id
  name    = each.value.hostedzone_suffix != null ? "${each.value.hostedzone_suffix}.${var.region}.amazonaws.com" : "${each.value.service_name_suffix}.${var.region}.amazonaws.com"
  type    = "A"

  alias {
    name                   = each.key == "S3PrivateLink-Endpoint" ? replace(aws_vpc_endpoint.this[each.key].dns_entry[0].dns_name, "*", "\\052") : aws_vpc_endpoint.this[each.key].dns_entry[0].dns_name
    zone_id                = aws_vpc_endpoint.this[each.key].dns_entry[0].hosted_zone_id
    evaluate_target_health = false
  }
}


#ECRDockerWildCard - Hosted Record for Acceptance and Production Env

resource "aws_route53_record" "ECRDockerWildCard-HostedRecord" {

  count = var.env_type!="dev" ? 1 : 0

  zone_id = aws_route53_zone.this["ECRDocker-Endpoint"].zone_id
  name = "*.dkr.ecr.${var.region}.amazonaws.com"
  type    = "A"

  alias {
    name                   = aws_vpc_endpoint.this["ECRDocker-Endpoint"].dns_entry[0].dns_name
    zone_id                = aws_vpc_endpoint.this["ECRDocker-Endpoint"].dns_entry[0].hosted_zone_id
    evaluate_target_health = false
  }
}

# resource block for newly created endpoints using extended vpc subnets

resource "aws_route53_zone" "this_extended" {
  for_each = var.endpoint_extended
  name = each.value.hostedzone_suffix != null ? "${each.value.hostedzone_suffix}.${var.region}.amazonaws.com" : "${each.value.service_name_suffix}.${var.region}.amazonaws.com"
  vpc {
    vpc_id     = var.vpc_id
    vpc_region = var.region
  }

  lifecycle {
    ignore_changes = [
      vpc
    ]
  }
  
}

# resource block for newly created endpoints using extended vpc subnets
resource "aws_route53_record" "this_extended" {
  for_each = var.endpoint_extended
  zone_id = aws_route53_zone.this_extended[each.key].zone_id
  name    = each.value.hostedzone_suffix != null ? "${each.value.hostedzone_suffix}.${var.region}.amazonaws.com" : "${each.value.service_name_suffix}.${var.region}.amazonaws.com"
  type    = "A"

  alias {
    name                   = aws_vpc_endpoint.this_extended[each.key].dns_entry[0].dns_name
    zone_id                = aws_vpc_endpoint.this_extended[each.key].dns_entry[0].hosted_zone_id
    evaluate_target_health = false
  }
}
