package wiz

default result = "fail"

result = "pass" {
count(input.tags) > 0
}
