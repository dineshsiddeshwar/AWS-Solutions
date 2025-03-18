{
  "Comment": "A description of my state machine",
  "StartAt": "Choice",
  "States": {
    "Choice": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.RequestType",
          "StringEquals": "New",
          "Next": "Get OU Details"
        },
        {
          "Variable": "$.RequestType",
          "StringEquals": "Renewal",
          "Next": "Validate OU"
        }
      ]
    },
    "Get OU Details": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_scp_get_ou_details",
      "Next": "Is in Exception OU?"
    },
    "Is in Exception OU?": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.Exception_account",
          "StringEquals": "yes",
          "Next": "Update Exception Account Policy"
        },
        {
          "Variable": "$.Exception_account",
          "StringEquals": "no",
          "Next": "Move Account to Exception OU"
        }
      ]
    },
    "Update Exception Account Policy": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_scp_update_policy",
      "Next": "Policy Updated?"
    },
    "Policy Updated?": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.Update_service_policy",
          "StringEquals": "FAILED",
          "Next": "Send Failure Email"
        },
        {
          "Variable": "$.Update_service_policy",
          "StringEquals": "SUCCESS",
          "Next": "Update Dynamo DB"
        }
      ]
    },
    "Move Account to Exception OU": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_scp_move_account",
      "Next": "Trigerred AVM?"
    },
    "Trigerred AVM?": {
      "Type": "Choice",
      "Choices": [
      {
        "Or": [
          {
            "Variable": "$.Account_movement",
            "StringEquals": "Skipped"
          },
          {
            "Variable": "$.Account_movement",
            "StringEquals": "FAILED"
          }
        ],
        "Next": "Send Failure Email"
      },
      {
          "Variable": "$.Account_movement",
          "StringEquals": "SUCCESS",
          "Next": "Check Product Status"
        }
      ]
    },
    "Send Failure Email": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_scp_send_failure_email",
      "Next": "Send Snow Response"
    },
    "Check Product Status": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_scp_check_status",
      "Next": "product Available?"
    },
    "product Available?": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.provision_product_status",
          "StringEquals": "AVAILABLE",
          "Next": "check OU"
        },
        {
          "Or": [
            {
              "Variable": "$.provision_product_status",
              "StringEquals": "ERROR"
            },
            {
              "Variable": "$.provision_product_status",
              "StringEquals": "TAINTED"
            }
          ],
          "Next": "Send Failure Email"
        }
      ],
      "Default": "Short Wait"
    },
    "Short Wait": {
      "Type": "Wait",
      "Seconds": 180,
      "Next": "Check Product Status"
    },
    "Validate OU": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_scp_validate_ou",
      "Next": "Is in Exception OU still?"
    },
  "Is in Exception OU still?": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.Exception_validation",
          "StringEquals": "FAILED",
          "Next": "Send Failure Email"
        },
        {
          "Variable": "$.Exception_validation",
          "StringEquals": "SUCCESS",
          "Next": "Update Dynamo DB"
        }
      ]
    },
    "check OU": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_scp_check_ou",
      "Next": "Account Moved?"
    },
    "Account Moved?": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.check_ou_status",
          "StringEquals": "SUCCESS",
          "Next": "Create Exception Policy"
        },
        {
          "Variable": "$.check_ou_status",
          "StringEquals": "FAILED",
          "Next": "Send Failure Email"
        }
      ]
    },
    "Create Exception Policy": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_scp_create_policy",
      "Next": "Policy Created??"
    },
    "Policy Created??": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.Create_attach_status",
          "StringEquals": "FAILED",
          "Next": "Send Failure Email"
        },
        {
          "Variable": "$.Create_attach_status",
          "StringEquals": "SUCCESS",
          "Next": "Update Dynamo DB"
        }
      ]
    },
    "Update Dynamo DB": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_scp_update_db",
      "Next": "DB Updated??"
    },
    "DB Updated??": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.Update_DB",
          "StringEquals": "FAILED",
          "Next": "Send Failure Email"
        },
        {
          "Variable": "$.Update_DB",
          "StringEquals": "SUCCESS",
          "Next": "Send Snow Response"
        }
      ]
    },
    "Send Snow Response": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_scp_send_snow_response",
      "Next": "Send  Success Email"
    },
    "Send  Success Email": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_scp_send_success_email",
      "End": true
    }
  }
}