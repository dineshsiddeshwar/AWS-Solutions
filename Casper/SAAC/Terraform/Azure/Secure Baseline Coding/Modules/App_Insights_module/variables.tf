##############
# Common Variables
##############

variable "create_resource_group" {
  description = "Whether to create resource group and use it for all networking resources"
  default     = false
}

variable "resource_group_name" {
  description = "Name of the resource group to be imported."
  type        = string
}

variable "location" {
  description = "The location/region to keep all your network resources. To get the list of all locations with table format from azure cli, run 'az account list-locations -o table'"
  default     = "useast"
}

variable "tags" {
  description = "A mapping of tags to assign to the resource."
  type        = map(string)
  default = {
    Department = "EYGDS"
  }
}

##############
# Application Insight Inputs
##############

variable "app_insights_name" {
  description = "Specifies the name of the Application Insights component."
  type        = string
}

variable "application_type" {
  description = "Specifies the type of Application Insights to create. Valid values are ios for iOS, java for Java web, MobileCenter for App Center, Node.JS for Node.js, other for General, phone for Windows Phone, store for Windows Store and web for ASP.NET. Please note these values are case sensitive; unmatched values are treated as ASP.NET by Azure."
  type        = string
}

variable "daily_data_cap_in_gb" {
  description = "Specifies the Application Insights component daily data volume cap in GB."
  type        = number
  default     = 10
}

variable "daily_data_cap_notifications_disabled" {
  description = "Specifies if a notification email will be send when the daily data volume cap is met."
  type        = bool
  default     = false
}

variable "retention_in_days" {
  description = "Specifies the retention period in days. Possible values are 30, 60, 90, 120, 180, 270, 365, 550 or 730. Defaults to 90"
  type        = number
  default     = 30
}

variable "sampling_percentage" {
  description = "Specifies the percentage of the data produced by the monitored application that is sampled for Application Insights telemetry."
  type        = number
  default     = null
}

variable "disable_ip_masking" {
  description = "By default the real client ip is masked as 0.0.0.0 in the logs. Use this argument to disable masking and log the real client ip. Defaults to false."
  type        = bool
  default     = false
}

################
# Analytics Item
################

variable "analytics_items" {
  description = "A map containing the analytics item attributes for each analytics_item that needs to be created."
  default     = {}
  # Example
  # analytics_items = {
  #   analytics_item1 = {
  #     type = "function"
  #     scope = "shared"
  #     content = "requests //simple example query"
  #     function_alias = "alias_name"
  #   }
  # }
}

######################
# Smart Detection Rule
######################

variable "smart_detection_rules" {
  description = "A list containing a map for each smart_detection_rule that needs to created."
  type        = list(string)
  default = [
    "Slow page load time",
    "Slow server response time",
    "Long dependency duration"
  ]
}

variable "additional_email_recipients" {
  description = "Specifies a list of additional recipients that will be sent emails on this Application Insights Smart Detection Rule."
  type        = list(string)
  default     = null
}

################
# Web Test
################

variable "web_tests" {
  description = "A map containing the values for each web_test that needs to be created."
  default     = {}
  ### Example
  #   web_tests = {
  #     ping_test = {
  #       kind                    = "ping"
  #       frequency               = 300
  #       timeout                 = 60
  #       enabled                 = true
  #       geo_locations           = ["us-tx-sn1-azr", "us-il-ch1-azr"]
  #       configuration = <<XML
  # <WebTest Name="WebTest1" Id="ABD48585-0831-40CB-9069-682EA6BB3583" Enabled="True" CssProjectStructure="" CssIteration="" Timeout="0" WorkItemIds="" xmlns="http://microsoft.com/schemas/VisualStudio/TeamTest/2010" Description="" CredentialUserName="" CredentialPassword="" PreAuthenticate="True" Proxy="default" StopOnError="False" RecordedResultFile="" ResultsLocale="">
  #   <Items>
  #     <Request Method="GET" Guid="a5f10126-e4cd-570d-961c-cea43999a200" Version="1.1" Url="http://microsoft.com" ThinkTime="0" Timeout="300" ParseDependentRequests="True" FollowRedirects="True" RecordResult="True" Cache="False" ResponseTimeGoal="0" Encoding="utf-8" ExpectedHttpStatusCode="200" ExpectedResponseUrl="" ReportingName="" IgnoreHttpStatusCode="False" />
  #   </Items>
  # </WebTest>
  # XML
  #     }
  #   }
}
