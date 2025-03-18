package wiz

default result = "fail"

result = "pass" {
	input.properties.virtualMachineProfile.networkProfile.networkInterfaceConfigurations[_].properties.ipConfigurations[_].properties.subnet.id > 0
}