data "archive_file" "bulk_dl_ddb_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_bulk_dl_ddb.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_bulk_dl_ddb.zip"
}

data "aws_iam_policy_document" "data_bulk_dl_ddb_policy" {
  statement {
    effect = "Allow"

    actions = [
      "s3:GetObject*"
    ]

    resources = [
      "arn:aws:s3:::new-dl-excel-bucket-us-east-1-${var.master_account}/*",
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "dynamodb:BatchGetItem", "dynamodb:BatchWriteItem"
    ]

    resources = [
      "arn:aws:dynamodb:us-east-1:${var.master_account}:table/DL_Details",
    ]
  }
}