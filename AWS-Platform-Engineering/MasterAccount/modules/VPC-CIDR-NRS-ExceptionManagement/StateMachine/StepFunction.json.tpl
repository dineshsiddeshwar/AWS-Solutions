{
    "Comment": "Step function to execute the snow request as expected",
    "StartAt": "SnowRequestProcessor",
    "States": {
      "SnowRequestProcessor": {
        "Type": "Task",
        "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_snow_networkvpc_integration_processing",
        "Next": "VerifySnowRequestProcessor"
      },
      "VerifySnowRequestProcessor": {
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
        "Seconds": 780,
        "Next": "SnowRequestProcessor"
      },
      "EndOfUpdate": {
        "Type": "Pass",
        "Result": "SnowRequestProcessingComplete",
        "End": true
      }
    }
  }