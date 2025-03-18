{
    "Comment": "Step function to automate execution of update Dedicated Account sequentially",
    "StartAt": "UpdateChildAccount",
    "States": {
      "UpdateChildAccount": {
        "Type": "Task",
        "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_update_child_account",
        "Next": "VerifyChildAccountUpdate"
      },
      "VerifyChildAccountUpdate": {
        "Type": "Choice",
        "Choices": [
          {
            "Variable": "$.IsUpdateComplete",
            "BooleanEquals": false,
            "Next": "LongWait"
          },
          {
            "Variable": "$.IsUpdateComplete",
            "BooleanEquals": true,
            "Next": "EndOfUpdate"
          }
        ]
      },
      "LongWait": {
        "Type": "Wait",
        "Seconds": 240,
        "Next": "UpdateChildAccount"
      },
      "EndOfUpdate": {
        "Type": "Pass",
        "Result": "AccountsUpdateComplete",
        "End": true
      }
    }
  }