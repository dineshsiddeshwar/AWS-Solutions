package wiz

default result = "pass"

result = "fail" {
  input.keyRotationStatus.KeyRotationEnabled = false
}