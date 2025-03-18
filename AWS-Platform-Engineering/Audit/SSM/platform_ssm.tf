data "aws_kms_key" "sharr_key"{
    key_id = "alias/SO0111-SHARR-Key" 
}

data "aws_sns_topic" "SHARRTopic229CFB9E" {
  name = "SO0111-SHARR_Topic"
}

resource "aws_ssm_parameter" "SHARRKeyC551FE02" {
  name  = "/Solutions/SO0111/CMK_ARN"
  description = "KMS Customer Managed Key that SHARR will use to encrypt data"
  type  = "String"
  value = data.aws_kms_key.sharr_key.arn
}

resource "aws_ssm_parameter" "SHARRSNSTopicB940F479" {
  name  = "/Solutions/SO0111/SNS_Topic_ARN"
  description = "SNS Topic ARN where SHARR will send status messages. This        topic can be useful for driving additional actions, such as email notifications,        trouble ticket updates."
  type  = "String"
  value = data.aws_sns_topic.SHARRTopic229CFB9E.arn
  }

resource "aws_ssm_parameter" "SHARRSendAnonymousMetricsCDAE439D" {
  name  = "/Solutions/SO0111/sendAnonymousMetrics"
  description = "Flag to enable or disable sending anonymous metrics."
  type  = "String"
  value = "Yes"
  }

resource "aws_ssm_parameter" "SHARRversionAC0E4F96" {
  name  = "/Solutions/SO0111/version"
  description = "Solution version for metrics."
  type  = "String"
  value = "v2.0.0"
  }

data "aws_sfn_state_machine" "sfn_state_machine" {
  name     = "SO0111-SHARR-Orchestrator"
}


resource "aws_ssm_parameter" "orchestratorSHARROrchestratorArn0ACC7B05" {
  name  = "/Solutions/SO0111/OrchestratorArn"
  description = "Arn of the SHARR Orchestrator Step Function. This step function routes findings to remediation runbooks."
  type  = "String"
  value = data.aws_sfn_state_machine.sfn_state_machine.arn
}  

resource "aws_ssm_parameter" "CISShortNameB8C8810A" {
  name  = "/Solutions/SO0111/cis-aws-foundations-benchmark/1.2.0/shortname"
  description = "Provides a short (1-12) character abbreviation for the standard."
  type  = "String"
  value = "CIS"
} 

resource "aws_ssm_parameter" "StandardVersionCB2C6951CIS120" {
  name  = "/Solutions/SO0111/cis-aws-foundations-benchmark/1.2.0/status"
  description = "This parameter controls whether the SHARR step function will process findings for this version of the standard."
  type  = "String"
  value = "enabled"
} 


resource "aws_ssm_parameter" "RemapCIS4245EB49A0" {
  name  = "/Solutions/SO0111/CIS/1.2.0/4.2/remap"
  description = "Remap the CIS 4.2 finding to CIS 4.1 remediation"
  type  = "String"
  value = "4.1"
} 

resource "aws_ssm_parameter" "SCShortName2FDDCF16" {
  name  = "/Solutions/SO0111/security-control/2.0.0/shortname"
  description = "Provides a short (1-12) character abbreviation for the standard."
  type  = "String"
  value = "SC"
} 

resource "aws_ssm_parameter" "StandardVersionCB2C6951SC" {
  name  = "/Solutions/SO0111/security-control/2.0.0/status"
  description = "This parameter controls whether the SHARR step function will process findings for this version of the standard."
  type  = "String"
  value = "enabled"
} 

resource "aws_ssm_parameter" "RemapSCEC2149F46BFF8" {
  name  = "/Solutions/SO0111/SC/2.0.0/EC2.14/remap"
  description = "Remap the SC EC2.14 finding to SC EC2.13 remediation"
  type  = "String"
  value = "EC2.13"
} 
