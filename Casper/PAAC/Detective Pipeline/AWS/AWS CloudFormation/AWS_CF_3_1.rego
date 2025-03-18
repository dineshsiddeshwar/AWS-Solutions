package wiz

default result = "pass"

result = "fail" {
	input.EnableTerminationProtection == false
}

#currentConfiguration = "The field 'EnableTerminationProtection' is set to false"
#expectedConfiguration = "The field 'EnableTerminationProtection' should be set to true"