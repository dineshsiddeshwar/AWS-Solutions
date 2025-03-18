package play

import future.keywords
package wiz
default result = "pass"

result = "fail"{
     #input.AssumeRolePolicyDocument.Statement[_].Effect=="Allow";input.AssumeRolePolicyDocument.Statement[_].Principal.AWS=="*";input.AssumeRolePolicyDocument.Statement[_].Action=="kms*";input.AssumeRolePolicyDocument.Statement[_].Resource=="*"
     input.AssumeRolePolicyDocument.Statement[_].Resource=="*";input.AssumeRolePolicyDocument.Statement[_].Principal.AWS=="*";input.AssumeRolePolicyDocument.Statement[_].Action=="kms*"
}

result = "fail"{
input.AssumeRolePolicyDocument.Statement[_].Resource=="*";input.AssumeRolePolicyDocument.Statement[_].Principal.AWS=="*";input.AssumeRolePolicyDocument.Statement[_].Effect=="Allow"
}

