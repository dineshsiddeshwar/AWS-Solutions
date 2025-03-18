# data "archive_file" "notifier_lambda_zip" {
#   type        = "zip"
#   source_file = "${path.module}/PythonFunctionFiles/notifier/"
#   output_path = "${path.module}/PythonFunctionZippedFiles/notifier.zip"
# }

# data "archive_file" "access_key_rotation_evaluation_lambda_zip" {
#   type        = "zip"
#   source_file = "${path.module}/PythonFunctionFiles/access_key_rotation_evaluation/"
#   output_path = "${path.module}/PythonFunctionZippedFiles/access_key_rotation_evaluation.zip"
# }

# data "archive_file" "account_inventory_lambda_zip" {
#   type        = "zip"
#   source_file = "${path.module}/PythonFunctionFiles/account_inventory/"
#   output_path = "${path.module}/PythonFunctionZippedFiles/account_inventory.zip"
# }
