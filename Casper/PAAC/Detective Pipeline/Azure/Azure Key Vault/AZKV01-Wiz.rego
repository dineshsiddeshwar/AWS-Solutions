package wiz

default result = "fail"

result = "pass" {
input.properties.privateEndpointConnections[_].id>0
}