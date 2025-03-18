package wiz

default result = "fail"

result = "pass"{
	not input.identity.type == "SystemAssigned" 
}