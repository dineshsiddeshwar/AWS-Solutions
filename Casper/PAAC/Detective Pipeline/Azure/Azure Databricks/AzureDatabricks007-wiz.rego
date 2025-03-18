package wiz
default result = "fail"

result = "pass" {
   input.properties.parameters.prepareEncryption.value = true
}
