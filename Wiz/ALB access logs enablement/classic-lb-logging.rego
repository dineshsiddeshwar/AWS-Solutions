package wiz

default result := "pass"

result := "fail" {
	# Add the logic to have the rule fail here.
    #input.loadBalancerAttributes.AccessLog.Enabled == false
    not contains(input.loadBalancerAttributes.AccessLog.S3BucketName, "XXXXX")
}

result := "fail" {
	# Add the logic to have the rule fail here.
    input.loadBalancerAttributes.AccessLog.Enabled == false
    #not contains(input.loadBalancerAttributes.AccessLog.S3BucketName, "XXXX")
}

currentConfiguration := sprintf("", [])
expectedConfiguration := sprintf("Load Balancer should have access logs enabled and pointing to logging bucket", [])