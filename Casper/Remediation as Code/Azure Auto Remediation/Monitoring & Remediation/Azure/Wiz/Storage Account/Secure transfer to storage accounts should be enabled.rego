# Title:Secure transfer to storage accounts should be enabled
# Description: Audit requirement of Secure transfer in your storage account. 
# Secure transfer is an option that forces your storage account to accept requests only from secure connections (HTTPS).
# Use of HTTPS ensures authentication between the server and the service and protects data in transit from network layer attacks such as
# man-in-the-middle, eavesdropping, and session-hijacking
# Developer: EY
# Version: 1.0

package wiz

default result = "fail"

result = "pass" {
	input.properties.supportsHttpsTrafficOnly
}

# Remediation
# 1. Select an existing storage account in the Azure portal. 
# 2. In the storage account menu pane, under Settings, select Configuration.
# 3. Under Secure transfer required, select Enabled. 
# For more informtion refer https://docs.microsoft.com/en-us/azure/storage/common/storage-require-secure-transfer



