{
  "Comment": "This step function is to generate the CIS Report for latest ami",
  "StartAt": "Launch EC2 Instance for latest ami",
  "States": {
    "Launch EC2 Instance for latest ami": {
            "Type": "Task",
            "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_CIS_Launch_EC2_Instance",
            "Next": "Wait for EC2 instance launch"
          },
           "Wait for EC2 instance launch": {
			"Type": "Wait",
			"Seconds": 500,
			"Next": "SSM Reporting Status"
          },
           "SSM Reporting Status": {
            "Type": "Task",
            "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_CIS_Get_EC2_SSM_Reporting_Status",
            "Next": "Select operation based on SSM Status"
          },
          "Select operation based on SSM Status": {
            "Type": "Choice",
            "Choices": [
                      {
                        "Variable": "$.ssm_status",
                        "StringEquals": "Online",
                        "Next": "CIS Report using SSM"
                      },
                      {
                        "Variable": "$.ssm_status",
                        "StringEquals": "ConnectionLost",
                        "Next": "SSM_status Wait"
                      },
                      {
                        "Variable": "$.ssm_status",
                        "StringEquals": "Inactive",
                        "Next": "SSM_status Wait"
                      }
                  ]
           },
          "CIS Report using SSM":{
            "Type": "Task",
            "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_CIS-Get_CIS_Report_Using_SSM",
            "Next": "Collect_CIS_Report Wait"
          },
          "SSM_status Wait": {
			"Type": "Wait",
			"Seconds": 250,
			"Next": "SSM Reporting Status"
          },
          "Collect_CIS_Report Wait": {
			"Type": "Wait",
			"Seconds": 700,
			"Next": "Update Score in DynamoDB"
          },
           "Update Score in DynamoDB":{
            "Type": "Task",
            "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_CIS_Update_CIS_Score_DynamoDB",
            "Next": "Select operation based on Score_Status"
           },
           "Select operation based on Score_Status": {
            "Type": "Choice",
            "Choices": [
                      {
                        "Variable": "$.Score",
                        "StringEquals": "True",
                        "Next": "Terminate EC2 Instance"
                      },
                      {
                        "Variable": "$.Score",
                        "StringEquals": "False",
                        "Next": "Send Email Notification"
                      }
                  ]
           },
          "Terminate EC2 Instance":{
            "Type": "Task",
            "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_CIS_Terminate_EC2_Instance",
            "End": true
          },
          "Send Email Notification": {
			"Type": "Task",
            "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_CIS_Send_notification_on_failure",
            "End": true
          }
  }
}