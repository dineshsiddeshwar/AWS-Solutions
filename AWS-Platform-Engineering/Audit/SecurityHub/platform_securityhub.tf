data "aws_lambda_function" "CreateCustomActionE7A973F5" {
  function_name = "SO0111-SHARR-CustomAction"
}

resource "aws_securityhub_action_target" "RemediateWithSharrCustomActionABE4122A" {
  depends_on  = [data.aws_lambda_function.CreateCustomActionE7A973F5]
  name        = "Remediate with ASR"
  identifier  = "ASRRemediation"
  description = "Submit the finding to AWS Security Hub Automated Response and Remediation"
}