package wiz

default result = "pass"

result = "fail" {
	input.userCredentials.PasswordEnabled == "true"; input.userCredentials.AccessKey1Active == "true"

}
result = "fail" {
	input.userCredentials.PasswordEnabled == "true"; input.userCredentials.AccessKey2Active == "true"

}