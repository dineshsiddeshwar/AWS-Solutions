package wiz

default result = "pass"

result = "fail" {
	not input.encryptionKeyMetadata.KeyManager == "CUSTOMER"
}

currentConfiguration = "encryptionKeyMetadata.KeyManager is set to AWS or the volume is not encrypted"
expectedConfiguration = "The EBS volume should be encrypted with a customer managed key"