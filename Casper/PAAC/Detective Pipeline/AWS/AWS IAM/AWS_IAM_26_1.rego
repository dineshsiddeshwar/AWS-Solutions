package wiz

default result = "pass"

result = "fail" {
	count(input.AttachedManagedPolicies) > 0
}