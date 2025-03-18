
package wiz
default result = "fail"

result = "pass" {
   input.properties.parameters.enableNoPublicIp.value = true
}
