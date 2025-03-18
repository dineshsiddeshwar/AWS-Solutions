{
  "Comment": "Step function to execute the snow request as expected",
  "StartAt": "SnowRequestProcessor",
  "States": {
    "SnowRequestProcessor": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_snow_integration_processing_ga",
      "Next": "VerifySnowRequestProcessor"
    },
    "VerifySnowRequestProcessor": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.IsProcessingComplete",
          "BooleanEquals": false,
          "Next": "LongWait"
        },
        {
          "Variable": "$.IsProcessingComplete",
          "BooleanEquals": true,
          "Next": "SupportTag"
        }
      ]
    },
    "LongWait": {
      "Type": "Wait",
      "Seconds": 240,
      "Next": "SnowRequestProcessor"
    },
    "SupportTag": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_snow_integration_supporttag_ga",
      "Next": "VerifySupportTag"
    },
    "VerifySupportTag": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.IsSupportTagComplete",
          "BooleanEquals": false,
          "Next": "EndOfUpdate"
        },
        {
          "Variable": "$.IsSupportTagComplete",
          "BooleanEquals": true,
          "Next": "CreateTFCWorkSpace"
        }
      ]
    },
    "CreateTFCWorkSpace": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_snow_integration_tfcworkspace_ga",
      "Next": "VerifyTFCWorkspace"
    },
    "VerifyTFCWorkspace": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.IsTFCWorkspaceComplete",
          "BooleanEquals": false,
          "Next": "EndOfUpdate"
        },
        {
          "Variable": "$.IsTFCWorkspaceComplete",
          "BooleanEquals": true,
          "Next": "CreateIPAWSGroups"
        }
      ]
    },
    "CreateIPAWSGroups": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_ipaws_integration",
      "Next": "VerifyIPAWSGroups"
    },
    "VerifyIPAWSGroups": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.IsCreateIPAWSGroupsComplete",
          "BooleanEquals": false,
          "Next": "EndOfUpdate"
        },
        {
          "Variable": "$.IsCreateIPAWSGroupsComplete",
          "BooleanEquals": true,
          "Next": "GenerateParametersFile"
        }
      ]
    },
    "GenerateParametersFile": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_snow_integration_parameters_ga",
      "Next": "VerifyParametersFile"
    },
    "VerifyParametersFile": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.IsParametersFileComplete",
          "BooleanEquals": false,
          "Next": "EndOfUpdate"
        },
        {
          "Variable": "$.IsParametersFileComplete",
          "BooleanEquals": true,
          "Next": "InvokeGitHubActions"
        }
      ]
    },
    "InvokeGitHubActions": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${account_region}:${account_number}:function:platform_snow_integration_githubaction_ga",
      "Next": "EndOfUpdate"
    },
    "EndOfUpdate": {
      "Type": "Pass",
      "Result": "SnowRequestProcessingComplete",
      "End": true
    }
  }
}