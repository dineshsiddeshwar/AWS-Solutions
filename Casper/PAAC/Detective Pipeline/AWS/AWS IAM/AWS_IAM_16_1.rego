package wiz
default result = "pass"

result = "fail"{
    input.AssumeRolePolicyDocument.Statement[_].Condition.IpAddress["aws:SourceIp"] == "*"
}