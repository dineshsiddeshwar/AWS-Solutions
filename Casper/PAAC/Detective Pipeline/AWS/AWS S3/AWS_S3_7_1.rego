# 	Use the Rego code below to programmatically define a Configuration Rule
# 	based on the raw json of a resource. By default, every resource with the selected
# 	Native Type will be assessed, and will have either 'fail' or 'pass' result.
# 
#
#  	You must populate the 'result' variable in either of the following string:
#	1. "pass" - The rule resource assessment will be set as "pass". 
#				Will not result in a Configuration Finding.
#	2. "fail" - The rule resource assessment will be set as "failed".
#				Will result in a Configuration Finding associated to the resource.
#	3. "skip" - The resource will not be assessed, and will not be counted in compliance reporting. 
#
#	To control the Expected Configuration and Current Configuration of a failed rule, declare
#	and populate 'currentConfiguration' and 'expectedConfiguration' variables with strings.

package wiz

default result = "pass"

result = "fail" {
    input.bucketPublicAccessBlock.PublicAccessBlockConfiguration.BlockPublicPolicy == false   
}
