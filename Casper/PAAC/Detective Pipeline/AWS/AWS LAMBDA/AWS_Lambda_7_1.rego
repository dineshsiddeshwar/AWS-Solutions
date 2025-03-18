package wiz

default result = "fail"

result = "pass" {
	input.TracingConfig.Mode == "Active"
}