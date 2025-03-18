package wiz
default result = "fail"

result = "pass" {
   count(input.resources[_].tags) > 0
}