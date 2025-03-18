locals {
  region    = data.aws_region.current.name
  accountid = data.aws_caller_identity.current.account_id
}

locals {
  region_name = split("-", data.aws_region.current.name)
}

locals {
  region1 = local.region_name[0]
  region2 = local.region_name[1]
  region3 = local.region_name[2]
}