# AVM catalog product
resource "aws_servicecatalog_product" "avm_servicecatalog_product" {
  accept_language  = "en"
  name  = "platform_avm_product"
  owner = "Shell"
  distributor = "Wipro"
  type  = "CLOUD_FORMATION_TEMPLATE"
  support_email = "SITI-CLOUD-SERVICES@shell.com"
  provisioning_artifact_parameters {
    template_url = "https://s3.amazonaws.com/${var.release_bucket_name}/TFC-Master/10/ServiceCatalogTemplates/avm_template.template"
    name = var.AVMTemplateVersion
    type = "CLOUD_FORMATION_TEMPLATE"
  }
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# new template version for AVM catalog product
resource "aws_servicecatalog_provisioning_artifact" "new_template_version" {
  product_id   = aws_servicecatalog_product.avm_servicecatalog_product.id
  name         = var.NewAVMTemplateVersion
  description  = "New template version (v3.0)"
  template_url = "https://s3.amazonaws.com/${var.release_bucket_name}/NewAVMTemplate/ServiceCatalogTemplates/avm_template.template"
  type         = "CLOUD_FORMATION_TEMPLATE"
}

# Network catalog product
resource "aws_servicecatalog_product" "network_servicecatalog_product" {
  accept_language  = "en"
  name  = "platform_network_request_product"
  owner = "Shell"
  distributor = "Wipro"
  type  = "CLOUD_FORMATION_TEMPLATE"
  support_email = "SITI-CLOUD-SERVICES@shell.com"
  provisioning_artifact_parameters {
    template_url = "https://s3.amazonaws.com/${var.release_bucket_name}/TFC-Master/10/ServiceCatalogTemplates/network.template"
    name = var.NetworkTemplateVersion
    type = "CLOUD_FORMATION_TEMPLATE"
  }
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Instance Scheduler catalog product
resource "aws_servicecatalog_product" "instancescheduler_servicecatalog_product" {
  accept_language  = "en"
  name  = "platform_instancescheduler_product"
  owner = "Shell"
  distributor = "Shell"
  type  = "CLOUD_FORMATION_TEMPLATE"
  support_email = "SITI-CLOUD-SERVICES@shell.com"
  provisioning_artifact_parameters {
    template_url = "https://s3.amazonaws.com/${var.release_bucket_name}/TFC-Master/10/ServiceCatalogTemplates/instancescheduler.template"
    name = "v1.0"
    type = "CLOUD_FORMATION_TEMPLATE"
  }
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# AVM catalog portfolio
resource "aws_servicecatalog_portfolio" "avm_servicecatalog_portfolio" {
  name          = "platform_admin_portfolio"
  provider_name = "Shell"
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# AVM catalog product portfolio association
resource "aws_servicecatalog_product_portfolio_association" "avm_servicecatalog_product_portfolio_association" {
  portfolio_id = aws_servicecatalog_portfolio.avm_servicecatalog_portfolio.id
  product_id   = aws_servicecatalog_product.avm_servicecatalog_product.id
}

# Network catalog product portfolio association
resource "aws_servicecatalog_product_portfolio_association" "network_servicecatalog_product_portfolio_association" {
  portfolio_id = aws_servicecatalog_portfolio.avm_servicecatalog_portfolio.id
  product_id   = aws_servicecatalog_product.network_servicecatalog_product.id
}

# Instance Scheduler product portfolio association
resource "aws_servicecatalog_product_portfolio_association" "instancescheduler_servicecatalog_product_portfolio_association" {
  portfolio_id = aws_servicecatalog_portfolio.avm_servicecatalog_portfolio.id
  product_id   = aws_servicecatalog_product.instancescheduler_servicecatalog_product.id
}

# AVM catalog principal portfolio association
resource "aws_servicecatalog_principal_portfolio_association" "avm_servicecatalog_principal_portfolio_association_1" {
  portfolio_id  = aws_servicecatalog_portfolio.avm_servicecatalog_portfolio.id
  principal_arn = var.AVMServiceCatalogRoleARN
  principal_type = "IAM"
}

# AVM catalog principal portfolio association
resource "aws_servicecatalog_principal_portfolio_association" "avm_servicecatalog_principal_portfolio_association_2" {
  portfolio_id  = aws_servicecatalog_portfolio.avm_servicecatalog_portfolio.id
  principal_arn = var.AVMServiceCatalogServiceRoleARN
  principal_type = "IAM"
}

# AVM catalog principal portfolio association
resource "aws_servicecatalog_principal_portfolio_association" "avm_servicecatalog_principal_portfolio_association_3" {
  portfolio_id  = aws_servicecatalog_portfolio.avm_servicecatalog_portfolio.id
  principal_arn = var.AVMServiceCatalogOperatorRoleARN
  principal_type = "IAM"
}

# AVM catalog principal portfolio association
resource "aws_servicecatalog_principal_portfolio_association" "avm_servicecatalog_principal_portfolio_association_4" {
  portfolio_id  = var.ControlTowerPortfolioARN
  principal_arn = var.AVMServiceCatalogServiceRoleARN
  principal_type = "IAM"
}

# AVM catalog Template Constraint
resource "aws_servicecatalog_constraint" "avm_servicecatalog_product_launch_constraint" {
  description  = "Constraints for not to create VPCs in Public Environment"
  portfolio_id = aws_servicecatalog_portfolio.avm_servicecatalog_portfolio.id
  product_id   = aws_servicecatalog_product.avm_servicecatalog_product.id
  type         = "TEMPLATE"

  parameters = jsonencode({
    "Rules" : {
        "Public-Production": {
            "RuleCondition": {
            "Fn::Equals": [
                {
                "Ref": "Environment"
                },
                "Public-Production"
            ]
            },
            "Assertions": [
            {
                "Assert": {
                "Fn::Contains": [
                    [
                    "No-VPC"
                    ],
                    {
                    "Ref": "NVirginia"
                    }
                ]
                },
                "AssertDescription": "For Public Production, all the public whitelisted regions are available to consume by the business and No VPC will be createds"
            },
            {
                "Assert": {
                "Fn::Contains": [
                    [
                    "No-VPC"
                    ],
                    {
                    "Ref": "Ireland"
                    }
                ]
                },
                "AssertDescription": "For Public Production, all the public whitelisted regions are available to consume by the business and No VPC will be created"
            },
            {
                "Assert": {
                "Fn::Contains": [
                    [
                    "No-VPC"
                    ],
                    {
                    "Ref": "Singapore"
                    }
                ]
                },
                "AssertDescription": "For Public Production, all the public whitelisted regions are available to consume by the business and No VPC will be created"             
            }
            ]
        },
        "Migration": {
            "RuleCondition": {
            "Fn::Equals": [
                {
                "Ref": "Environment"
                },
                "Migration"
            ]
            },
            "Assertions": [
            {
                "Assert": {
                "Fn::Contains": [
                    [
                    "No-VPC"
                    ],
                    {
                    "Ref": "NVirginia"
                    }
                ]
                },
                "AssertDescription": "For Migration, all the public whitelisted regions are available to consume by the business and No VPC will be createds"
            },
            {
                "Assert": {
                "Fn::Contains": [
                    [
                    "No-VPC"
                    ],
                    {
                    "Ref": "Ireland"
                    }
                ]
                },
                "AssertDescription": "For Migration, all the public whitelisted regions are available to consume by the business and No VPC will be created"
            },
            {
                "Assert": {
                "Fn::Contains": [
                    [
                    "No-VPC"
                    ],
                    {
                    "Ref": "Singapore"
                    }
                ]
                },
                "AssertDescription": "For Migration, all the public whitelisted regions are available to consume by the business and No VPC will be created" 
            }
            ]
        },
        "Public-Exception": {
            "RuleCondition": {
            "Fn::Equals": [
                {
                "Ref": "Environment"
                },
                "Public-Exception"
            ]
            },
            "Assertions": [
            {
                "Assert": {
                "Fn::Contains": [
                    [
                    "No-VPC"
                    ],
                    {
                    "Ref": "NVirginia"
                    }
                ]
                },
                "AssertDescription": "For Public Exception, all the public whitelisted regions are available to consume by the business and No VPC will be created"
            },
            {
                "Assert": {
                "Fn::Contains": [
                    [
                    "No-VPC"
                    ],
                    {
                    "Ref": "Ireland"
                    }
                ]
                },
                "AssertDescription": "For Public Exception, all the public whitelisted regions are available to consume by the business and No VPC will be created"
            },
            {
                "Assert": {
                "Fn::Contains": [
                    [
                    "No-VPC"
                    ],
                    {
                    "Ref": "Singapore"
                    }
                ]
                },
                "AssertDescription": "For Public Exception, all the public whitelisted regions are available to consume by the business and No VPC will be created"
            }
            ]
        },
        "Managed_Services-Prod": {
            "RuleCondition": {
                "Fn::Equals": [
                {
                    "Ref": "Environment"
                },
                "Managed_Services-Prod"
                ]
                },
                "Assertions": [
                {
                    "Assert": {
                        "Fn::Contains": [
                            [
                                "No-VPC"
                            ],
                            {
                                "Ref": "NVirginia"
                            }
                            ]
                        },
                        "AssertDescription": "For Managed_Services-Prod, all the public whitelisted regions are available to consume by the business and No VPC will be created"
                        },
                        {
                        "Assert": {
                            "Fn::Contains": [
                            [
                                "No-VPC"
                            ],
                            {
                                "Ref": "Ireland"
                            }
                            ]
                        },
                        "AssertDescription": "For Managed_Services-Prod, all the public whitelisted regions are available to consume by the business and No VPC will be created"
                        },
                        {
                        "Assert": {
                            "Fn::Contains": [
                            [
                                "No-VPC"
                            ],
                            {
                                "Ref": "Singapore"
                            }
                            ]
                        },
                        "AssertDescription": "For Managed_Services-Prod, all the public whitelisted regions are available to consume by the business and No VPC will be created"
                        }
                    ]
                    }
        }
  })
}