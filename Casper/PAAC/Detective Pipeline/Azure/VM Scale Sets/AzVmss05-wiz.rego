package wiz

default result = "fail"

result = "pass" {
input.properties.virtualMachineProfile.storageProfile.osDisk.managedDisk.diskEncryptionSet.id > 0 ; input.properties.virtualMachineProfile.storageProfile.dataDisks[_].managedDisk.diskEncryptionSet.id> 0
}
result = "pass" {
input.properties.virtualMachineProfile.storageProfile.osDisk.managedDisk.diskEncryptionSet.id > 0
}