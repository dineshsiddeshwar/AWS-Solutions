# Title:Storage accounts should be limited by allowed SKUs
# Description: Restrict the set of storage account SKUs that your organization can deploy
# Developer: EY
# Version: 1.0

package wiz

default result = "pass"

result = "fail" {
	not input.sku.tier == "Premium"
}

# Remediation
# upgrade to Premium