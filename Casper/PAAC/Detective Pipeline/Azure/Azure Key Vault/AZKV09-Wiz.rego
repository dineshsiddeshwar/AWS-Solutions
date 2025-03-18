package wiz

default result = "fail"

result = "pass" {
input.properties.enableSoftDelete ; input.properties.enablePurgeProtection ; input.properties.softDeleteRetentionInDays > 0
}