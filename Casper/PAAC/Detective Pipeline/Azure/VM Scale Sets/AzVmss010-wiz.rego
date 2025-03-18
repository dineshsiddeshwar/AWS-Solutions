package wiz

default result = "fail"

result = "pass" {
	input.resources[0].identity.type == "SystemAssigned" 
}