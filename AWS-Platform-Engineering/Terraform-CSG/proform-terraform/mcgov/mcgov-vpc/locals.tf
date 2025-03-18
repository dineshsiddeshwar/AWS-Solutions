locals {
  resource_group = "${var.env}-${replace(data.aws_region.current.id, "-", "")}"
  # Tags
  tags = merge(var.tags,
    {
      Environment = var.env
  })
}