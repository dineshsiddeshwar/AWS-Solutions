package wiz
default result = "fail"

result = "pass" {
   count(input.properties.parameters.resourceTags.value) > 0
}