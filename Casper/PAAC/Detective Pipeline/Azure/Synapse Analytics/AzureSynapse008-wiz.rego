package wiz

default result = "fail"

result = "pass"{
	input.properties.azureADOnlyAuthentication == true 
}