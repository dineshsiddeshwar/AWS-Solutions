# Title:Geo-redundant storage should be enabled for Storage Accounts
# Description: Use geo-redundancy to create highly available applications
# Developer: EY
# Version: 1.0

package wiz

default result = "pass"

result = "fail" {
    allowedGRS := ["Standard_LRS","Premium_LRS","Standard_ZRS","Premium_ZRS"]
    some i
    input.sku.name == allowedGRS[i]
}

# Remediation
# choose any one of the Geo redundant sku name "Standard_GRS",
#                "Standard_RAGRS",
#                "Standard_GZRS",
#                "Standard_RAGZRS"