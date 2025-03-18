# platform send alarm notification lambda
/*
resource "aws_lambda_function" "send_notification_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_send_alarm_notification.zip"
  function_name = "platform_send_alarm_notification"
  role          = var.role_arn
  handler       = "platform_send_alarm_notification.lambda_handler"
  source_code_hash = data.archive_file.send_notification_lambda_lambda_zip.output_base64sha256

  runtime = "python3.9"
  memory_size = 2176
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# subscription filter for  send alarm notification lambda
resource "aws_cloudwatch_log_subscription_filter" "subscription_filter_1" {
  name            = "platform-subscription-filter-1"
  log_group_name  = "aws-controltower/CloudTrailLogs"
  filter_pattern  = "{(($.eventName=ConsoleLogin) && ($.errorMessage=\"Failed authentication\")) || ($.userIdentity.type=\"Root\" && $.userIdentity.invokedBy NOT EXISTS && $.eventType !=\"AwsServiceEvent\") || (($.eventName=\"ConsoleLogin\") && ($.additionalEventData.MFAUsed !=\"Yes\") && ($.userIdentity.sessionContext.sessionIssuer.arn !=\"*sso.amazonaws.com*\")) || (($.eventSource=kms.amazonaws.com) && (($.eventName=DisableKey) || ($.eventName=ScheduleKeyDeletion))) || ($.eventName=CreateNetworkAcl) || ($.eventName=CreateNetworkAclEntry) || ($.eventName=DeleteNetworkAcl) || ($.eventName=DeleteNetworkAclEntry) || ($.eventName=ReplaceNetworkAclEntry) || ($.eventName=ReplaceNetworkAclAssociation)}"
  destination_arn = aws_lambda_function.send_notification_lambda.arn
}

# subscription filter for  send alarm notification lambda
resource "aws_cloudwatch_log_subscription_filter" "subscription_filter_2" {
  name            = "platform-subscription-filter-2"
  log_group_name  = "aws-controltower/CloudTrailLogs"
  filter_pattern  = "{($.eventName=CreateCustomerGateway) || ($.eventName=DeleteCustomerGateway) || ($.eventName=AttachInternetGateway) || ($.eventName=CreateInternetGateway) || ($.eventName=DeleteInternetGateway) || ($.eventName=DetachInternetGateway) || ($.eventName=CreateRoute) || ($.eventName=CreateRouteTable) || ($.eventName=ReplaceRoute) || ($.eventName=ReplaceRouteTableAssociation) || ($.eventName=DeleteRouteTable) || ($.eventName=DeleteRoute) || ($.eventName=DisassociateRouteTable) || ($.eventName=CreateVpc) || ($.eventName=DeleteVpc) || ($.eventName=ModifyVpcAttribute) || ($.eventName=AcceptVpcPeeringConnection) || ($.eventName=CreateVpcPeeringConnection) || ($.eventName=DeleteVpcPeeringConnection) || ($.eventName=RejectVpcPeeringConnection) || ($.eventName=AttachClassicLinkVpc) || ($.eventName=DetachClassicLinkVpc) || ($.eventName=DisableVpcClassicLink) || ($.eventName=EnableVpcClassicLink)}"
  destination_arn = aws_lambda_function.send_notification_lambda.arn
}

# permission for subscription filter to invoke send alarm notification lambda
resource "aws_lambda_permission" "send_notification_lambda_permission" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.send_notification_lambda.arn
  principal     = "logs.us-east-1.amazonaws.com"
  source_account = var.master_account
  source_arn    = "arn:aws:logs:us-east-1:${var.master_account}:log-group:aws-controltower/CloudTrailLogs:*"
}
*/

