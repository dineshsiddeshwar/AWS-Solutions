{
    "Comment": "A description of my state machine",
    "StartAt": "Get Account List Lambda",
    "States": {
      "Get Account List Lambda": {
        "Type": "Task",
        "Resource": "arn:aws:states:::lambda:invoke",
        "OutputPath": "$.Payload",
        "Parameters": {
          "FunctionName": "${main_lambda_arn}"
        },
        "Retry": [
          {
            "ErrorEquals": [
              "Lambda.ServiceException",
              "Lambda.AWSLambdaException",
              "Lambda.SdkClientException"
            ],
            "IntervalSeconds": 2,
            "MaxAttempts": 6,
            "BackoffRate": 2
          }
        ],
        "Next": "Iterate Account List"
      },
      "Iterate Account List": {
        "Type": "Map",
        "End": true,
        "Iterator": {
          "StartAt": "Get EC2 List Lambda",
          "States": {
            "Get EC2 List Lambda": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "OutputPath": "$.Payload",
              "Parameters": {
                "Payload.$": "$",
                "FunctionName": "${secondary_lambda_arn}"
              },
              "Retry": [
                {
                  "ErrorEquals": [
                    "Lambda.ServiceException",
                    "Lambda.AWSLambdaException",
                    "Lambda.SdkClientException"
                  ],
                  "IntervalSeconds": 2,
                  "MaxAttempts": 4,
                  "BackoffRate": 2
                }
              ],
              "Catch": [
                {
                  "ErrorEquals": [
                    "States.ALL"
                  ],
                  "Next": "Pass"
                }
              ],
              "Next": "Pass"
            },
            "Pass": {
              "Type": "Pass",
              "End": true
            }
          }
        },
        "ItemsPath": "$.Payload"
      }
    }
  }
