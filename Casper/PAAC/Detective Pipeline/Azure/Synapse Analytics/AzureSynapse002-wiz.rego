package wiz

default result = "fail"

result = "pass"{
	input.properties.defaultDataLakeStorage.createManagedPrivateEndpoint == true 
}