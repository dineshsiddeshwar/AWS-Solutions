# Title: Storage accounts should restrict network access using virtual network rules
# Description: Protect your storage accounts from potential threats using virtual network rules
# as a preferred method instead of IP-based filtering. Disabling IP-based filtering prevents public 
# IPs from accessing your storage accounts
# Developer: EY
# Version: 1.0

package wiz

default result = "pass"

result = "fail" {
	count(input.properties.networkAcls.virtualNetworkRules) == 0
    
}

# Remediation
# Protect your storage accounts from potential threats using virtual network rules as a preferred method
# instead of IP-based filtering. Disabling IP-based filtering prevents public IPs from accessing your storage accounts