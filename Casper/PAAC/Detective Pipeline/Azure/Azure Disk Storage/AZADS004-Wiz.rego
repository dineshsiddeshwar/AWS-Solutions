package wiz

default result = "fail"

result = "pass" {
input.properties.encryption.type == "EncryptionAtRestWithCustomerKey"
}