# Application Insights

This module creates an Azure application Insights, desiered nunber of analytics Item/ Web Item, smart detection rules (all 3 rules by default) and the following api keys.

API Keys:

- read_telemetry
- write_annotations
- authenticate_sdk_control_channel
- full_permissions


An example of how to use this module

```terraform
module "app_insight" {
  source = "../Modules/App_Insights_module"
  resource_group_name = "EYGDS-baselie-rg"
  app_insights_name = "Test_App"
  application_type = "java"
  analytics_items = [
    analytics_item1 = {
      type = "function"
      scope = "shared"
      content = "requests //simple example query"
      function_alias = "alias_name"
    }
  ]
  smart_detection_rules = [ "Slow page load time" ]
  additional_email_recipients = [ "xyz@example.com" ]
      web_tests = {
      ping_test = {
        kind                    = "ping"
        frequency               = 300
        timeout                 = 60
        enabled                 = true
        geo_locations           = ["us-tx-sn1-azr", "us-il-ch1-azr"]
        configuration = <<XML
  <WebTest Name="WebTest1" Id="ABD48585-0831-40CB-9069-682EA6BB3583" Enabled="True" CssProjectStructure="" CssIteration="" Timeout="0" WorkItemIds="" xmlns="http://microsoft.com/schemas/VisualStudio/TeamTest/2010" Description="" CredentialUserName="" CredentialPassword="" PreAuthenticate="True" Proxy="default" StopOnError="False" RecordedResultFile="" ResultsLocale="">
    <Items>
      <Request Method="GET" Guid="a5f10126-e4cd-570d-961c-cea43999a200" Version="1.1" Url="http://microsoft.com" ThinkTime="0" Timeout="300" ParseDependentRequests="True" FollowRedirects="True" RecordResult="True" Cache="False" ResponseTimeGoal="0" Encoding="utf-8" ExpectedHttpStatusCode="200" ExpectedResponseUrl="" ReportingName="" IgnoreHttpStatusCode="False" />
    </Items>
  </WebTest>
  XML
      }
    }
}
```
