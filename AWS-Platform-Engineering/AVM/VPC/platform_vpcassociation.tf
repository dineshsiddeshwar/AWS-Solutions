provider "aws" {
  alias = "sharedaccount"
}


locals {
  vpc_hostedzone_list = flatten([
    for RegionIpDictionary_key, RegionIpDictionary_value in var.RegionIpDictionary : [
      for hostedzone_id in toset(split(",", RegionIpDictionary_value.hostedzone_ids)) : {
        vpc_id = aws_vpc.create_vpc_in_child_account[RegionIpDictionary_key].id
        zone_id  = hostedzone_id
      }
    ]
  ])
}

resource "aws_route53_vpc_association_authorization" "create_vpc_association_authorization" {
  provider = aws.sharedaccount
  for_each =  { for key,value in local.vpc_hostedzone_list : value.zone_id => value }

  vpc_id  = each.value.vpc_id
  zone_id = each.value.zone_id
}

resource "aws_route53_zone_association" "associate_vpc_with_hosted_zone" {
  for_each =  { for key,value in local.vpc_hostedzone_list : value.zone_id => value }

  vpc_id  = each.value.vpc_id
  zone_id = each.value.zone_id

  depends_on = [ aws_route53_vpc_association_authorization.create_vpc_association_authorization ]
}


