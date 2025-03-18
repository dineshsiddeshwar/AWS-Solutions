package wiz
default result = "fail"

result = "pass" {
   count(input.resources[_].properties.privateEndpoint) > 0
}