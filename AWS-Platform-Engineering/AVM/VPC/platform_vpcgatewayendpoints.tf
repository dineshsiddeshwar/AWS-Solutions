data "aws_route_tables" "describe_route_tables" {
  for_each = var.RegionIpDictionary

  vpc_id = aws_vpc.create_vpc_in_child_account[each.key].id
}

resource "aws_vpc_endpoint" "create_vpc_endpoint_s3_gateway" {
  for_each = var.RegionIpDictionary

  vpc_id            = aws_vpc.create_vpc_in_child_account[each.key].id
  service_name      = "com.amazonaws.${data.aws_region.current.name}.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids   =  data.aws_route_tables.describe_route_tables[each.key].ids

  tags = {
    platform_donotdelete = "yes"
    Name = "platform-S3-Endpoint"
  }
}

resource "aws_vpc_endpoint" "create_vpc_endpoint_ddb_gateway" {
  for_each = var.RegionIpDictionary

  vpc_id            = aws_vpc.create_vpc_in_child_account[each.key].id
  service_name      = "com.amazonaws.${data.aws_region.current.name}.dynamodb"
  vpc_endpoint_type = "Gateway"
  route_table_ids   =  data.aws_route_tables.describe_route_tables[each.key].ids

  tags = {
    platform_donotdelete = "yes"
    Name = "platform-DynamoDB-Endpoint"
  }
}