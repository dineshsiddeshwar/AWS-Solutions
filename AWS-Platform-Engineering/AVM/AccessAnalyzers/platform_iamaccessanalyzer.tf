resource "aws_accessanalyzer_analyzer" "platform_analyzer" {
  analyzer_name = "platform_analyzer_${var.region}"
  type          = "ACCOUNT"
  tags = {
    platform_donotdelete = "yes"
  }
}