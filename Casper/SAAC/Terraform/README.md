# Terraform Styleguide
Some straightforward best-practices as decided by the team

## Helpful Links
[Terraform Data Types](https://www.terraform.io/language/expressions/type-constraints)

## Assumptions
 - Policies will be drafted BEFORE resources are created.
 - Settings, Permissions, Tags will exist before the 
 - Some resources depend on others before being created, therefore depends_on tag should be used

## Helpful notes
 - Terraform Graph is a great resource, but is just a tool. Try to graph what we're building first, then use tf graph to compare expected to actual

## Reviewers
1. Move jira ticket to "QA Review"
2. Check mispellings, file structure, keys, values, etc (see guidance below), no default values in variables, etc
3. Run `terraform validate` and correct and issues
4. Run `terraform plan` and correct all issues until hitting this one "https response error StatusCode: 403" (because that means all pre-requesites passed, execept for deployment)
5. Make sure the actual requirements are covered, get from "how to" in client repo

## Checking in code
1. git checkout master / git merge (your branch) master
2. if you just want a review, put in a PR request, with WIP: in front of teh name `WIP:my-pr`
3. if your ready for final review / consider your work done, remove the WIP: from the pr name
4. move your jira ticket to validate

## Issue/Pull Request Format
When creating an issue and/or pull request, please use the following format:
1.	Name: “(CSP) (INSERT SERVICE NAME): Terraform Script” - e.g. "Azure Container Registry: Terraform Script"
2. Include the “IAC Implementation” label
3.	Projects should be “EY-SCMC”
4.	Use the following as a description and populate upon submitting a PR:<br>
```
**(CSP) (INSERT SERVICE NAME)**
- Brief description of the PR implements or fixes.
**Ticket**
- Add the JIRA ticket url:
**How to test**
- Steps to perform the test and expected results.
- Command-line invocation to run automated tests.
**Additional info**
- 
```

## File Structure
- snippets.tf
- terraform.tfvars
- variables.tf
- versions.tf
- providers.tf
policies
 - my_policy.json
 - other_policy.json 


## variables.tf
 - No default values
 - All variables must have description
 - Move all 'Data' resources here

## terraform.tfvars
- Usually not checked into git, these values, if checked in should be overwrite placeholders
- Flatten it, meaning no nested key-value pairs
- Assume provider is already configured

instead of

```
common_tags = {
  Usage-id    = "Network"    # For example only, Replace it with Application specific value
  cost-center = "524067"     # Fixed 6 numeric value. For example only, Replace it with Application specific value
  toc         = "ETOC"       # Technology oversight committees (TOCs). For example only, Replace it with Application specific value
  exp-date    = "99-00-9999" # date in mm-dd-yyyy format. Default value, Replace it with Application specific value 
  env-type    = "dev"        # For example only, Replace it with Application specific value
  sd-period   = "na"         # shutdown time, used for automation of shutdown. Default value, Replace it with Application specific value 
}
```

do this
```
common_tags_usage_id = "__AA_LAKEFORMATION_COMMON_TAGS_USAGE_ID__"
common_tags_cost_center = "_AA_LAKEFORMATION_COMMON_TAGS_COST_CENTER__"
```

## snippets.tf
- Does not actually run
- Use as many variables for values as possible
- Clearly mark what data types are accepted
- Watch the types! People put strings for numbers all the time, this might fail
- Avoid wildcards!

instead of
```
  tags = {
    Name = "lf-vpc-endpoint-security-group-${var.prefix}"
  }

```
something like this

```
  tags = {
    Name = var.lakeformation_security_group_ids # Array
  }
```

---

instead of
```
resource "aws_vpc_endpoint" "lf" {
    ...
```

something like this
```
resource "aws_vpc_endpoint" "lf_vpc_endpoint" {
    ...
```
also, in resource names, keys, etc, you don't need to specify the cloud provider like `aws_...`
---
instead of
```
resource "aws_vpc_endpoint" "lf" {
  vpc_id            = data.aws_vpc.aws_vpc_id.id
  service_name      = var.service_name
  vpc_endpoint_type = var.vpc_endpoint_type
  security_group_ids = [
    var.lf-vpc-sg,
  ]
  private_dns_enabled = true

  tags = {
    Name = "${var.lf-vpc-endpoint}-${var.prefix}"
  }
}
```

something like
```
resource "aws_vpc_endpoint" "lf_vpc_endpoint" {
  vpc_id            = var.lf_vpc_endpoint_vpc_id # String
  service_name      = var.lf_vpc_endpoint_service_name # String
  vpc_endpoint_type = var.lf_vpc_endpoint_endpoint_type # String
  security_group_ids = var.lf_vpc_endpoint_security_group_ids # Array
  private_dns_enabled = true

  tags = var.lf_vpc_endpoint_tags # Map
}
```

## Policies
- Avoid wildcards!

instead of inline policies

do JSON policies in one file, and reference it with `template_file` data source
https://stackoverflow.com/questions/63300892/terraform-replace-variable-inside-json

like this
```
data "template_file" "json_template" {
  template = file("path/to/file.json")
  vars = {
    role_arn = var.dynamic_value
  }
}

resource "provider_resource" "name" {
  property = "value"
  options = data.template_file.json_template.rendered # !!important - remember .rendered
}
```

Pay close attention to types!
```
# Bad - can you spot the error?
  ...
  memory_size = "250"
  timeout     = var.stop_ec2_lambda_timeout

# Good
  ...
  memory_size = 250
  timeout     = var.stop_ec2_lambda_timeout
```

Instead of
```
aws_instace...

  root_block_device {
    volume_size           = var.ec2_private_root_block_volume_size
    volume_type           = var.ec2_private_root_block_volume_type
    kms_key_id            = data.aws_kms_key.cg-cmk-key.arn # 4. Ensure EC2 data are encrypted at rest using Organization's Managed Keys (CMK)
    encrypted             = true 
    delete_on_termination = true
  }

## Do this

aws_instance...
   ami               = var.aws_instance_ami
```

