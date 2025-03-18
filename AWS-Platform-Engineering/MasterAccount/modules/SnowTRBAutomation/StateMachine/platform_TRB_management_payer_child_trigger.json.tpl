{
  "StartAt": "Choice",
  "States": {
    "Choice": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.status.statusCode",
          "NumericEquals": 400,
          "Next": "AggregateResults"
        }
      ],
      "Default": "Invoke-Child-Trigger"
    },
    "Invoke-Child-Trigger": {
      "Type": "Map",
      "ItemsPath": "$.events",
      "Iterator": {
        "StartAt": "InvokeLambdaFunction",
        "States": {
          "InvokeLambdaFunction": {
            "Type": "Task",
            "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_TRB_management_payer_child_account_trigger:$LATEST",
            "End": true
          }
        }
      },
      "ResultPath": "$.LambdaResults",
      "Next": "AggregateResults",
      "MaxConcurrency": 10
    },
    "AggregateResults": {
      "Type": "Pass",
      "Next": "Lambda - Result Aggregator"
    },
    "Lambda - Result Aggregator": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "OutputPath": "$.Payload",
      "Parameters": {
        "Payload.$": "$",
        "FunctionName": "arn:aws:lambda:${account_region}:${account_number}:function:platform_TRB_management_payer_result_aggregator:$LATEST"
      },
      "Retry": [
        {
          "ErrorEquals": [
            "Lambda.ServiceException",
            "Lambda.AWSLambdaException",
            "Lambda.SdkClientException",
            "Lambda.TooManyRequestsException"
          ],
          "IntervalSeconds": 1,
          "MaxAttempts": 3,
          "BackoffRate": 2
        }
      ],
      "End": true
    }
  }
}