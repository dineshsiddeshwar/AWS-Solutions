{
  "Comment": "Step function execution for the Dedicated Account",
  "StartAt": "Select Operation On Network Product",
  "States": {
    "Select Operation On Network Product": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.RequestType",
          "StringEquals": "Create",
          "Next": "New VPC Creation"
        },
        {
          "Variable": "$.RequestType",
          "StringEquals": "Update",
          "Next": "VPCUpdate"
        },
        {
          "Variable": "$.RequestType",
          "StringEquals": "Delete",
          "Next": "Delete"
        }
      ]
    },
    "New VPC Creation": {
      "Type": "Pass",
      "Next": "Fetch CIDR"
     },
    "Fetch CIDR": {
      "Type": "Task",
      "Resource":"arn:aws:lambda:${account_region}:${account_number}:function:platform_network_fetch_cidr",
      "Next": "CIDR status"
    },
    "CIDR status": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.fetch_cidr",
          "StringEquals": "true",
          "Next": "Create VPC"
        },
        {
          "Variable": "$.fetch_cidr",
          "StringEquals": "false",
          "Next": "Execution Failed"
        }
      ]
    },
    "Create VPC": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_network_vpc_creation",
      "Next": "Create Subnet"
    },
    "Create Subnet": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_network_subnet_creation",
      "Next": "Create Associations"
    },
    "Create Associations": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_network_vpc_associations",
      "Next": "Create Resolver"
    },
    "Create Resolver": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_network_create_resolver",
      "Next": "Update Tables"
    },
    "Update Tables": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_network_update_table",
      "Next": "Associate TGW"
    },
    "VPCUpdate": {
      "Type": "Choice",
      "Choices":[
              {
          "Variable": "$.vpc_extension",
          "StringEquals": "true",
          "Next": "Fetch new IP Block"
        },
          {
          "Variable": "$.vpc_extension",
          "StringEquals": "false",
          "Next": "New VPC Creation"
        }
       ]
    },
    "VPCDeletion": {
      "Type": "Pass",
      "Next": "DisassociateTGWAttachment"
    },
    "DisassociateTGWAttachment": {
      "Type": "Task",
      "Resource":"arn:aws:lambda:${account_region}:${account_number}:function:platform_disassociate_TGW_attachment",
      "Next": "DisassociateTGWResourceShare"
   },
   "DisassociateTGWResourceShare": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_disassociate_TGW_resource_share",
      "End": true
  },
    "Associate TGW":{
      "Type": "Pass",
      "Next": "Request TGW Shared Resource"
    }, 
    "Request TGW Shared Resource": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_request_TGW_resource_share",
      "Next": "Short Wait 1"
    },
    "Short Wait 1": {
      "Type": "Wait",
      "Seconds": 60,
      "Next": "Accept TGW Resource share"
    },
    "Accept TGW Resource share": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_accept_TGW_resource_share",
      "Next": "Create TGW Attachment"
    },
    "Create TGW Attachment": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_create_TGW_attachment",
      "Next":  "Accept TGW Attachment"
        },
    "Accept TGW Attachment": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_accept_TGW_attachment",
      "Next": "Short Wait 2"
  },
  "Short Wait 2": {
    "Type": "Wait",
    "Seconds": 240,
    "Next": "Configure VPC Traffic Route to TGW"
  },
    "Configure VPC Traffic Route to TGW": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_configure_vpc_traffic_to_TGW",
      "Next": "Long Wait"
    },    
    "Long Wait": {
      "Type": "Wait",
      "Seconds": 420,
      "Next": "Verify TGW Association status"
    },
    "Verify TGW Association status": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_verify_TGW_route_association",
      "Next": "TGW Association Completed"
    },
    "TGW Association Completed": {
      "Type": "Pass",
      "Next": "Non-Routable Range addition"
    }, 
    "Non-Routable Range addition": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_non_routable_vpc_extension",
      "Next": "Non-Routable Resource Creation"
    },
    "Non-Routable Resource Creation": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_non_routable_network_resources",
      "Next": "Action Complete"
    }, 
    "Action Complete": {
      "Type": "Pass",
       "Result": "Network create/update completed",
      "End": true
    },
    "Execution Failed": {
      "Type": "Pass",
      "End": true
    },
    "Fetch new IP Block": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_network_fetch_cidr",
      "Next": "Extension CIDR status"
    },
     "Extension CIDR status": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.fetch_cidr",
          "StringEquals": "true",
          "Next": "Extend VPC"
        },
        {
          "Variable": "$.fetch_cidr",
          "StringEquals": "false",
          "Next": "Execution Failed"
        }
      ]
    },
    "Extend VPC": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_network_vpc_extension",
      "Next": "Create new Subnet"
    },
    "Create new Subnet": {
      "Type": "Task",
      "Resource":"arn:aws:lambda:${account_region}:${account_number}:function:platform_network_subnet_creation",
      "Next": "TGW Association Update"
    },
    "TGW Association Update": {
      "Type": "Task",
      "Resource":"arn:aws:lambda:${account_region}:${account_number}:function:platform_vpc_extension_tgw_update",
      "Next": "New VPC Creation"
    },
    "Delete": {
      "Type": "Pass",
      "Next": "VPCDeletion"
    }
  }
}