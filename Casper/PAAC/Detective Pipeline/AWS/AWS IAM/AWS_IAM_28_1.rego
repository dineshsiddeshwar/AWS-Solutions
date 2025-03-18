package wiz

default result = "pass"
now_ns := time.now_ns()
days_30_ns := time.parse_duration_ns("720h") # 30 days

unusedCredentials[[credential,user]]{
	not now_ns - time.parse_rfc3339_ns(input.userCredentials.AccessKey1LastUsedDate) < days_30_ns
	input.userCredentials.AccessKey1Active == "true"
	credential = "access key 1"
    user = input.userCredentials.User
}

unusedCredentials[[credential,user]] {
	input.userCredentials.AccessKey1LastUsedDate = "N/A"
	input.userCredentials.AccessKey1Active == "true"
	credential = "access key 1"
    user = input.userCredentials.User
}

unusedCredentials[[credential,user]] {
	input.userCredentials.AccessKey2LastUsedDate = "N/A"
	input.userCredentials.AccessKey2Active == "true"
	credential = "access key 2"
    user = input.userCredentials.User
}

unusedCredentials[[credential,user]] {
	not now_ns - time.parse_rfc3339_ns(input.userCredentials.AccessKey2LastUsedDate) < days_30_ns
	input.userCredentials.AccessKey2Active == "true"
	credential = "access key 2"
    user = input.userCredentials.User
}

unusedCredentials[[credential,user]] {
	input.userCredentials.PasswordLastUsed = "no_information"
	input.userCredentials.PasswordEnabled == "true"
	credential = "Password"
    user = input.userCredentials.User
}

unusedCredentials[[credential,user]] {
	not now_ns - time.parse_rfc3339_ns(input.userCredentials.PasswordLastUsed) < days_30_ns
	input.userCredentials.PasswordEnabled == "true"
	credential = "Password"
    user = input.userCredentials.User
}

result = "fail" {
	now_ns - time.parse_rfc3339_ns(input.CreateDate) > days_30_ns
    count(unusedCredentials) > 0
}
currentConfiguration = concat("",["Password or Access keys have not been used in the past 30 days for Credential, User: ",concat(", ", unusedCredentials[i])])