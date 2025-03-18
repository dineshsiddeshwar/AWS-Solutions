package wiz

default result = "fail"

result = "pass" {
count(input.identity.userAssignedIdentities) > 0
}