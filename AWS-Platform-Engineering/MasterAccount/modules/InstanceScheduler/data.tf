# Instance Scheduler lambda zip 
data "archive_file" "instance_scheduler_solution_creator_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_instance_scheduler_solution_creator.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_instance_scheduler_solution_creator.zip"
}
