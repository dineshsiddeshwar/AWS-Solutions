package wiz
default result = "pass"

 result = "fail"{
  	input.AssumeRolePolicyDocument.Statement[0].Service == "*"
	
}