package wiz

default result = "fail"

result = "pass" {
count(input.properties.instanceView.events[_]) > 0
}