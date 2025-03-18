output "Default_key_used" {
    value = var.default_key_for_SSE
}

output "SNS_topic_name" {
    value = aws_sns_topic.casper_sns.name
}

output "SNS_key_used_name" {
    value = var.default_key_for_SSE? "alias/aws/sns" : "alias/casper_key_for_SNS"
}