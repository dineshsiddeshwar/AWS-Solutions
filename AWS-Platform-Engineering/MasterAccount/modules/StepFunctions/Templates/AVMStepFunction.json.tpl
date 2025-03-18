{
  "Comment": "Step function execution for the Dedicated Account",
  "StartAt": "Verify Parameter",
  "States": {
    "Verify Parameter": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_verifyproduct_parameters",
      "Next": "Verify Parameter Choice"
    },
    "Verify Parameter Choice": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.VerifiedParameters",
          "BooleanEquals": false,
          "Next": "Send Failed Email "
        },
        {
          "Variable": "$.VerifiedParameters",
          "BooleanEquals": true,
          "Next": "Select Operation On Child Account"
        }
      ]
    },
    "Select Operation On Child Account": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.RequestType",
          "StringEquals": "Create",
          "Next": "AccountCreation"
        },
        {
          "Variable": "$.RequestType",
          "StringEquals": "Update",
          "Next": "AccountUpdation"
        },
        {
          "Variable": "$.RequestType",
          "StringEquals": "Delete",
          "Next": "AccountDeletion"
        }
      ]
    },
    "AccountCreation": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.ResourceProperties.Migration",
          "StringEquals": "Yes",
          "Next": "AccountMigration"
        },
        {
          "Variable": "$.ResourceProperties.Migration",
          "StringEquals": "No",
          "Next": "Fetch DLs from DL table"
        }
      ]
    },
    "AccountMigration": {
      "Type": "Pass",
      "Next": "Create Child Account"
    },
    "Fetch DLs from DL table": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_fetch_dl",
      "Next": "Create Child Account"
    },
    "Create Child Account": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_provision_child_account",
      "Next": "Verify Child Account Creation"
    },
    "Verify Child Account Creation": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.ResultAccountCreation",
          "StringEquals": "Success",
          "Next": "Check Account Status"
        },
        {
          "Variable": "$.ResultAccountCreation",
          "StringEquals": "Fail",
          "Next": "Send Failed Email "
        }
      ]
    },
    "Long Wait": {
      "Type": "Wait",
      "Seconds": 240,
      "Next": "Check Account Status"
    },
    "Check Account Status": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_provision_product_status",
      "Next": "Verify Child Account Status"
    },
    "Verify Child Account Status": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.AccountCreationStatus",
          "StringEquals": "AVAILABLE",
          "Next": "Tag Accounts and Update DL Table"
        },
        {
          "Variable": "$.AccountCreationStatus",
          "StringEquals": "FAILED",
          "Next": "Send Failed Email "
        },
        {
          "Variable": "$.AccountCreationStatus",
          "StringEquals": "UNDER CHANGE",
          "Next": "Long Wait"
        }
      ]
    },
    "Tag Accounts and Update DL Table": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_update_dltable",
      "Next": "Remove admin access"
    },
    "Remove admin access": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_access_management",
      "Next": "Add Account into Account Details Table"
    },
    "Add Account into Account Details Table": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_update_account_table",
      "Next": "Create Roles In Child Account"
    },
    "Create Roles In Child Account": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_child_account_roles",
      "Next": "Short Wait"
    },
    "Short Wait": {
      "Type": "Wait",
      "Seconds": 120,
      "Next": "Create Security Groups in Shell Corp AD"
    },
    "Create Security Groups in Shell Corp AD": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_ipaws_integration",
      "Next": "Create custom insights"
    },
    "Create custom insights": {
       "Type": "Task",
       "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_create_custom_insights",
       "Next": "Tag Automation for Child Account"
    },
    "Tag Automation for Child Account": {
        "Type": "Task",
        "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_tagautomation_create_resource",
        "Next": "InflationProcess"
    },
    "InflationProcess": {
      "Type": "Parallel",
      "Next": "Update Accounts Details Table",
      "Branches": [
        {
          "StartAt": "Enable Create Budget In Child Account",
          "States": {
            "Enable Create Budget In Child Account": {
              "Type": "Choice",
              "Choices": [
                {
                  "Variable": "$.ResourceProperties.Migration",
                  "StringEquals": "Yes",
                  "Next": "Create Budget in Linked Account"
                },
                {
                  "Variable": "$.ResourceProperties.Migration",
                  "StringMatches": "No",
                  "Next": "Create Budget in Linked Account"
                }
              ]
            },
            "Create Budget in Linked Account": {
              "Type": "Task",
              "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_set_budget_in_childaccount",
              "Catch": [ {
                  "ErrorEquals": ["States.ALL"],
                  "Next": "Send budget Failure Status"
               }],
              "End": true
            },
            "Send budget Failure Status": {
              "Type": "Pass",
              "End": true
            }
          }
        },
        {
          "StartAt": "Enable Enterprise Support in Linked Account",
          "States": {
            "Enable Enterprise Support in Linked Account": {
              "Type": "Task",
              "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_enable_enterprise_support",
              "Catch": [ {
                  "ErrorEquals": ["States.ALL"],
                  "Next": "Send Enterprise Failure Status"
               }],
              "End": true
            },
            "Send Enterprise Failure Status": {
              "Type": "Pass",
              "End": true
            }
          }
        },
        {
          "StartAt": "Enable VPC",
          "States": {
            "Enable VPC": {
              "Type": "Choice",
              "Choices": [
                {
                  "Variable": "$.ResourceProperties.Environment",
                  "StringMatches": "Public-*",
                  "Next": "Public - No VPC"
                },
                {
                  "Variable": "$.ResourceProperties.Environment",
                  "StringMatches": "Migration*",
                  "Next": "Public - No VPC"
                },
                {
                  "Variable": "$.ResourceProperties.Environment",
                  "StringMatches": "Private-*",
                  "Next": "Private - Create VPC"
                },
                {
                  "Variable": "$.ResourceProperties.Environment",
                  "StringMatches": "Hybrid-*",
                  "Next": "Private - Create VPC"
                },
                {
                  "Variable": "$.ResourceProperties.Environment",
                  "StringMatches": "Managed_Services-Prod*",
                  "Next": "Public - No VPC"
                },
                {
                  "Variable": "$.ResourceProperties.Environment",
                  "StringMatches": "Data-Management*",
                  "Next": "Public - No VPC"
                }
              ]
            },
            "Private - Create VPC": {
              "Type": "Task",
              "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_network_launch",
              "Catch": [ {
                  "ErrorEquals": ["States.ALL"],
                  "Next": "Send VPC Failure Status"
               }],
              "End": true
            },
            "Send VPC Failure Status": {
              "Type": "Pass",
              "End": true
            },
            "Public - No VPC": {
              "Type": "Pass",
              "End": true
            }
          }
        },
        {
          "StartAt": "Tag AMI",
          "States": {
            "Tag AMI": {
              "Type": "Task",
              "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_ami_tagging",
              "Catch": [ {
                  "ErrorEquals": ["States.ALL"],
                  "Next": "Send AMI TAG Failure Status"
               }],
              "End": true
            },
            "Send AMI TAG Failure Status": {
              "Type": "Pass",
              "End": true
            }
          }
        },
        {
          "StartAt": "Tag EKS AMI",
          "States": {
            "Tag EKS AMI": {
              "Type": "Task",
              "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_ami_tagging_eks",
              "Catch": [ {
                  "ErrorEquals": ["States.ALL"],
                  "Next": "Send EKS AMI TAG Failure Status"
               }],
              "End": true
            },
            "Send EKS AMI TAG Failure Status": {
              "Type": "Pass",
              "End": true
            }
          }
        },
        {
          "StartAt": "Domain Join",
          "States": {
            "Domain Join": {
              "Type": "Task",
              "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_SSM_Association_Domainjoin",
              "Catch": [ {
                  "ErrorEquals": ["States.ALL"],
                  "Next": "Send Doamin Join Failure Status"
               }],
              "End": true
            },
            "Send Doamin Join Failure Status": {
              "Type": "Pass",
              "End": true
            }
          }
        },
        {
          "StartAt": "Default VPC Deletion",
          "States": {
            "Default VPC Deletion": {
              "Type": "Task",
              "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_default_vpc_deletion",
              "Catch": [
                {
                  "ErrorEquals": [
                    "States.ALL"
                  ],
                  "Next": "Send Default VPC Deletion Failure Status"
                }
              ],
              "End": true
            },
            "Send Default VPC Deletion Failure Status": {
              "Type": "Pass",
              "End": true
            }
          }
        },
        {
          "StartAt": "SSM Agent Auto-Update",
          "States": {
            "SSM Agent Auto-Update": {
              "Type": "Task",
              "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_ssm_agent_autoupdate",
              "Catch": [ {
                  "ErrorEquals": ["States.ALL"],
                  "Next": "Security Hub Refinements"
               }],
              "Next": "Security Hub Refinements"
            },
            "Security Hub Refinements": {
              "Type": "Task",
              "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_securityhub_refinements",
              "Catch": [ {
                  "ErrorEquals": ["States.ALL"],
                  "Next": "SSM Agent Auto-Update and Security hub refinement failure Status"
               }],
              "End": true
            },
            "SSM Agent Auto-Update and Security hub refinement failure Status": {
              "Type": "Pass",
              "End": true
            }
          }
        },
        {
          "Comment": "Step Function to enable Access Analyzer and security lambdas in child account",
          "StartAt": "Enable IAM_Access_Analyzer",
          "States": {
            "Enable IAM_Access_Analyzer": {
              "Type": "Task",
              "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_analyzer_enable_child",
              "Catch": [ {
                  "ErrorEquals": ["States.ALL"],
                  "Next": "Block EMR Public Access"
               }],
              "Next": "Block EMR Public Access"
            },
            "Block EMR Public Access": {
              "Type": "Task",
              "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_security_emr_block_public",
              "Catch": [ {
                  "ErrorEquals": ["States.ALL"],
                  "Next": "Block S3 Public Access"
               }],
              "Next": "Block S3 Public Access"
            },
            "Block S3 Public Access": {
              "Type": "Task",
              "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_security_s3_block_public",
              "Catch": [ {
                  "ErrorEquals": ["States.ALL"],
                  "Next": "Enable EBS Encryption"
               }],
              "Next": "Enable EBS Encryption"
            },
            "Enable EBS Encryption": {
              "Type": "Task",
              "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_security_enable_ebs_encryption",
              "Catch": [ {
                  "ErrorEquals": ["States.ALL"],
                  "Next": "Subscribe SNS Topic"
               }],
              "Next": "Subscribe SNS Topic"
            },
            "Subscribe SNS Topic": {
              "Type": "Task",
              "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_security_sns_topic",
              "Catch": [ {
                  "ErrorEquals": ["States.ALL"],
                  "Next": "Send Security configure failure Status"
               }],
              "End": true
            },
            "Send Security configure failure Status": {
              "Type": "Pass",
              "End": true
            }
          }
        },
        {
          "Comment": "Step Function to create SSM association in child for Agent installation ",
          "StartAt": "Install Falcon Agent Linux",
          "States": {
            "Install Falcon Agent Linux": {
              "Type": "Choice",
              "Choices": [
                {
                  "Variable": "$.ResourceProperties.Migration",
                  "StringEquals": "Yes",
                  "Next": "Install Falcon Agent on Linux"
                },
                {
                  "Variable": "$.ResourceProperties.Migration",
                  "StringMatches": "No",
                  "Next": "Install Falcon Agent on Linux"
                }
              ]
            },
            "Install Falcon Agent on Linux": {
              "Type": "Task",
              "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_installfalcon_linux",
              "Catch": [ {
                  "ErrorEquals": ["States.ALL"],
                  "Next": "Install Falcon Agent Windows"
               }],
              "Next": "Install Falcon Agent Windows"
            },
            "Install Falcon Agent Windows": {
              "Type": "Task",
              "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_InstallFalcon_Windows",
              "Catch": [ {
                  "ErrorEquals": ["States.ALL"],
                  "Next": "Install Flexera Agent Linux"
               }],
              "Next": "Install Flexera Agent Linux"
            },
            "Install Flexera Agent Linux": {
              "Type": "Task",
              "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_InstallFlexeraAgent_Linux",
              "Catch": [ {
                  "ErrorEquals": ["States.ALL"],
                  "Next": "Install Flexera Agent Windows"
               }],
              "Next": "Install Flexera Agent Windows"
            },
            "Install Flexera Agent Windows": {
              "Type": "Task",
              "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_InstallFlexeraAgent_Windows",
              "Catch": [ {
                  "ErrorEquals": ["States.ALL"],
                  "Next": "Install cloudhealth Agent Linux"
               }],
              "Next": "Install cloudhealth Agent Linux"
            },
            "Install cloudhealth Agent Linux": {
              "Type": "Task",
              "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_InstallCloudHealth_Linux",
              "Catch": [ {
                  "ErrorEquals": ["States.ALL"],
                  "Next": "Install cloudhealth Agent Windows"
               }],
              "Next": "Install cloudhealth Agent Windows"
            },
            "Install cloudhealth Agent Windows": {
              "Type": "Task",
              "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_InstallCloudHealth_Windows",
              "Catch": [ {
                  "ErrorEquals": ["States.ALL"],
                  "Next": "Install Rapid7 Linux"
               }],
              "Next": "Install Rapid7 Linux"
            },
            "Install Rapid7 Linux": {
              "Type": "Task",
              "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_InstallRapid7_Linux",
              "Catch": [ {
                  "ErrorEquals": ["States.ALL"],
                  "Next": "Install Rapid7 Windows"
               }],
              "Next": "Install Rapid7 Windows"
            },
            "Install Rapid7 Windows": {
              "Type": "Task",
              "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_InstallRapid7_windows",
              "Catch": [ {
                  "ErrorEquals": ["States.ALL"],
                  "Next": "Install CloudWatch Agent"
               }],
              "Next": "Install CloudWatch Agent"
            },
            "Install CloudWatch Agent": {
              "Type": "Task",
              "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_InstallCloudWatchAgent",
              "Catch": [ {
                  "ErrorEquals": ["States.ALL"],
                  "Next": "Install Association Linux"
               }],
              "Next": "Install Association Linux"
            },
            "Install Association Linux": {
              "Type": "Task",
              "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_linux_association",
              "Catch": [ {
                  "ErrorEquals": ["States.ALL"],
                  "Next": "Install Association Windows"
               }],
              "Next": "Install Association Windows"
            },
            "Install Association Windows": {
              "Type": "Task",
              "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_windows_association",
              "Catch": [ {
                  "ErrorEquals": ["States.ALL"],
                  "Next": "Send Agent Installation Failure Status"
               }],
              "End": true
            },
            "Send Agent Installation Failure Status": {
              "Type": "Pass",
              "End": true
            }
          }
        },
        {
          "Comment": "Step Function branch",
          "StartAt": "Back Up Vault Set Up",
          "States": {
            "Back Up Vault Set Up": {
              "Type": "Choice",
              "Choices": [
                {
                  "Variable": "$.ResourceProperties.Migration",
                  "StringEquals": "Yes",
                  "Next": "Back Up Vault Set Up in Linked Account"
                },
                {
                  "Variable": "$.ResourceProperties.Migration",
                  "StringMatches": "No",
                  "Next": "Back Up Vault Set Up in Linked Account"
                }
              ]
            },
            "Back Up Vault Set Up in Linked Account": {
              "Type": "Task",
              "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_setup_backup_resource",
              "Catch": [ {
                  "ErrorEquals": ["States.ALL"],
                  "Next": "Backup Vault Pass step"
               }],
              "Next": "Backup Vault Pass step"
            },
            "Backup Vault Pass step": {
              "Type": "Pass",
              "End": true
            }
          }
        }
      ]
    },
    "Update Accounts Details Table": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_update_account_table",
      "Next": "Send Success Email For Account Inflation"
    },
    "Send Success Email For Account Inflation": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_send_templated_mail",
      "Next": "EndOfInflation"
    },
    "EndOfInflation": {
      "Type": "Pass",
      "Result": "Inflation is complete",
      "End": true
    },
    "Send Failed Email ": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_send_templated_mail",
      "ResultPath": "$.ResultSendMail",
      "End": true
    },
    "AccountUpdation": {
      "Type": "Pass",
      "Next": "Create Child Account"
    },
    "AccountDeletion": {
      "Type": "Pass",
        "Next": "GetInventory"
     },
       "GetInventory": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_chargeable_resource_inventory",
      "Next": "Wait for one day"
    },
    "Wait for one day": {
      "Type": "Wait",
      "Seconds": 86400,
      "Next": "UpdateAccountDetailsTableAfterDecommission"
    },
    "UpdateAccountDetailsTableAfterDecommission": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_update_account_table",
      "Next": "UpdateDLDetailsTableAfterDecommission"
    },
    "UpdateDLDetailsTableAfterDecommission": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_update_dltable",
      "Next": "MoveAccountToDecomissionedOU"
    },
    "MoveAccountToDecomissionedOU": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_move_decom_ou",
      "Next": "CloseAccount"
    },
    "CloseAccount": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_close_account",
      "Next": "SendMailDeflationCompletion"
    },
    "SendMailDeflationCompletion": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_decom_mail",
      "Next": "EndOfDecommission"
    },
    "EndOfDecommission": {
      "Type": "Pass",
      "Result": "Decommission is complete",
      "End": true
    }
  }
}
