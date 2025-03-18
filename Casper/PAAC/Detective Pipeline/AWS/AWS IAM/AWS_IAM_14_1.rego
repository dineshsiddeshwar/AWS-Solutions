package wiz

import data.generic.common as common_lib

WizPolicy[result] {
	password_policy := input.document[i].resource.aws_iam_account_password_policy[name]
	not common_lib.valid_key(password_policy, "password_reuse_prevention")

	result := {
		"documentId": input.document[i].id,
		"searchKey": sprintf("aws_iam_account_password_policy[%s]", [name]),
		"issueType": "MissingAttribute",
		"keyExpectedValue": "'password_reuse_prevention' should be set with value 12",
		"keyActualValue": "'password_reuse_prevention' is undefined",
		"resourceTags": object.get(password_policy, "tags", {}),
	}
}

WizPolicy[result] {
	password_policy := input.document[i].resource.aws_iam_account_password_policy[name]
	rp := password_policy.password_reuse_prevention
	rp < 12

	result := {
		"documentId": input.document[i].id,
		"searchKey": sprintf("aws_iam_account_password_policy[%s].password_reuse_prevention", [name]),
		"issueType": "IncorrectValue",
		"keyExpectedValue": "'password_reuse_prevention' should be 12",
		"keyActualValue": "'password_reuse_prevention' is lower than 12",
		"resourceTags": object.get(password_policy, "tags", {}),
	}
}
