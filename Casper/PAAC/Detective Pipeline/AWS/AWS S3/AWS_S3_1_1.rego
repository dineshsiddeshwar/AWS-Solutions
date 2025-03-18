# 	Label: Ensure AWS S3 buckets are not granting FULL_CONTROL access to authenticated users (least privilege access)
#   Description: An S3 bucket that allows full control access to authenticated users will give any AWS account or IAM user the ability to LIST (READ) objects, UPLOAD/DELETE (WRITE) objects, VIEW (READ_ACP) objects permissions and EDIT (WRITE_ACP) permissions for the objects within the bucket.

package wiz

default result = "pass"

result = "fail" {
	input.bucketAcl.Grants[_].Permission == "FULL_CONTROL"
}
