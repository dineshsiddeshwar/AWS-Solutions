data "aws_iam_policy_document" "data_atl_terraform_backend_bucket_policy" {
  statement {
    sid = "DenyDeleteATLBucket"
    principals {
      type        = "*"
      identifiers = ["*"]
    }
    effect = "Deny"
    actions = [
      "s3:DeleteObject*",
      "s3:DeleteBucket*",
    ]

    resources = [
      aws_s3_bucket.atl_terraform_backend_bucket.arn,
      "${aws_s3_bucket.atl_terraform_backend_bucket.arn}/*",
    ]
  }
}