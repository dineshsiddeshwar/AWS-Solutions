data "aws_ssoadmin_instances" "sso_instance" {}

resource "aws_ssoadmin_permission_set" "business_ServiceNow_ITOM" {
  name             = "business_ServiceNow_ITOM"
  instance_arn     = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  session_duration= "PT1H"
  description = "role for ServiceNow ITOM"
}


data "aws_iam_policy" "business_ServiceNow_ITOM" {
  name = "ServiceNow_ITOM_Discovery_Child_Policy"
} 

resource "aws_ssoadmin_customer_managed_policy_attachment" "business_ServiceNow_ITOM" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  permission_set_arn = aws_ssoadmin_permission_set.business_ServiceNow_ITOM.arn
  customer_managed_policy_reference {
    name = data.aws_iam_policy.business_ServiceNow_ITOM.name
  }
}