package wiz

default result = "pass"

now_ns := time.now_ns()
days_90_ns := time.parse_duration_ns("2160h") # 90 days

unusedCredentials[credential] {
	not now_ns - time.parse_rfc3339_ns(input.userCredentials.AccessKey1LastUsedDate) < days_90_ns
	input.userCredentials.AccessKey1Active == "true"
	credential = "access key 1"
}

unusedCredentials[credential] {
	input.userCredentials.AccessKey1LastUsedDate = "N/A"
	input.userCredentials.AccessKey1Active == "true"
	credential = "access key 1"
}

unusedCredentials[credential] {
	input.userCredentials.AccessKey2LastUsedDate = "N/A"
	input.userCredentials.AccessKey2Active == "true"
	credential = "access key 2"
}

unusedCredentials[credential] {
	not now_ns - time.parse_rfc3339_ns(input.userCredentials.AccessKey2LastUsedDate) < days_90_ns
	input.userCredentials.AccessKey2Active == "true"
	credential = "access key 2"
}

result = "fail" {
	now_ns - time.parse_rfc3339_ns(input.CreateDate) > days_90_ns
    count(unusedCredentials) > 0
}

currentConfiguration = concat("",["Access keys have not been used in the past 90 days: ",concat(", ", unusedCredentials)])
expectedConfiguration = "Access keys unused for 90 days or more should be disabled or removed."