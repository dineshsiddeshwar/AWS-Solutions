package wiz

default result = "pass"

now_ns := time.now_ns()
days_90_ns := time.parse_duration_ns("2160h") # 90 days

notrotatedCredentials[credential] {
	not now_ns - time.parse_rfc3339_ns(input.userCredentials.AccessKey1LastRotated) < days_90_ns
	input.userCredentials.AccessKey1Active == "true"
	credential = "access key 1"
}

notrotatedCredentials[credential] {
	input.userCredentials.AccessKey1LastRotated = "N/A"
	input.userCredentials.AccessKey1Active == "true"
	credential = "access key 1"
}

notrotatedCredentials[credential] {
	input.userCredentials.AccessKey2LastRotated = "N/A"
	input.userCredentials.AccessKey2Active == "true"
	credential = "access key 2"
}

notrotatedCredentials[credential] {
	not now_ns - time.parse_rfc3339_ns(input.userCredentials.AccessKey2LastRotated) < days_90_ns
	input.userCredentials.AccessKey2Active == "true"
	credential = "access key 2"
}

result = "fail" {
	now_ns - time.parse_rfc3339_ns(input.CreateDate) > days_90_ns
    count(notrotatedCredentials) > 0
}

currentConfiguration = concat("",["Access keys have not been Rotated in the past 90 days: ",concat(", ", notrotatedCredentials)])
expectedConfiguration = "Access keys not rotated for 90 days or more should be disabled or removed or rotated."