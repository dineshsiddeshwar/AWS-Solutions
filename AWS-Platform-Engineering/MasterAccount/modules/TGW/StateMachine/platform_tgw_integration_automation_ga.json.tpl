{
    "Comment": "Step function execution for TGW Automations",
    "StartAt": "Select TGW Operation",
    "States": {
        "Select TGW Operation": {
            "Type": "Choice",
            "Choices": [
            {
                "Variable": "$.RequestType",
                "StringEquals": "Create",
                "Next": "Associate TGW"
            },
            {
                "Variable": "$.RequestType",
                "StringEquals": "Update",
                "Next": "TGW Association Update"
            },
            {
                "Variable": "$.RequestType",
                "StringEquals": "Delete",
                "Next": "Disassociate TGW Attachment"
            }
            ]
        },
        "Disassociate TGW Attachment": {
            "Type": "Task",
            "Resource":"arn:aws:lambda:${account_region}:${account_number}:function:platform_disassociate_TGW_attachment_ga",
            "Next": "Disassociate TGW Resource Share"
        },
        "Disassociate TGW Resource Share": {
            "Type": "Task",
            "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_disassociate_TGW_resource_share_ga",
            "End": true
        },
        "Associate TGW":{
            "Type": "Pass",
            "Next": "Request TGW Shared Resource"
        }, 
        "Request TGW Shared Resource": {
            "Type": "Task",
            "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_request_TGW_resource_share_ga",
            "Next": "Short Wait 1"
        },
        "Short Wait 1": {
            "Type": "Wait",
            "Seconds": 60,
            "Next": "Accept TGW Resource share"
        },
        "Accept TGW Resource share": {
            "Type": "Task",
            "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_accept_TGW_resource_share_ga",
            "Next": "Create TGW Attachment"
       },
       "Create TGW Attachment": {
            "Type": "Task",
            "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_create_TGW_attachment_ga",
            "Next":  "Accept TGW Attachment"
        },
        "Accept TGW Attachment": {
            "Type": "Task",
            "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_accept_TGW_attachment_ga",
            "Next": "Short Wait 2"
        },
        "Short Wait 2": {
            "Type": "Wait",
            "Seconds": 240,
            "Next": "Configure VPC Traffic Route to TGW"
        },
        "Configure VPC Traffic Route to TGW": {
            "Type": "Task",
            "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_configure_vpc_traffic_to_TGW_ga",
            "Next": "Long Wait"
        },    
        "Long Wait": {
            "Type": "Wait",
            "Seconds": 420,
            "Next": "Verify TGW Association status"
        },
        "Verify TGW Association status": {
            "Type": "Task",
            "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_verify_TGW_route_association_ga",
            "End": true
        },
        "TGW Association Update": {
            "Type": "Task",
            "Resource":"arn:aws:lambda:${account_region}:${account_number}:function:platform_vpc_extension_tgw_update_ga",
            "Next": "Associate TGW"
        }
    }
}