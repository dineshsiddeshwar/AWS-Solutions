package wiz

default result = "pass"

result = "fail" {
	input.properties.ipConfigurations[_].properties.publicIPAddress.id > 0
}