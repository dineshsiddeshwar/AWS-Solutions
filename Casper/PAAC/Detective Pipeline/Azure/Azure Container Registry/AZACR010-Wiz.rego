package wiz

default result = "fail"

result = "pass" {
input.properties.policies.trustPolicy.status == "enabled"
}