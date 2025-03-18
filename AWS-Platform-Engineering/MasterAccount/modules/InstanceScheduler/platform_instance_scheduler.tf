# Instance Scheduler Lambda
resource "aws_lambda_function" "instance_scheduler_solution_creator_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_instance_scheduler_solution_creator.zip"
  function_name = "platform_instance_scheduler_solution_creator"
  role          = var.role_arn
  handler       = "platform_instance_scheduler_solution_creator.lambda_handler"
  source_code_hash = data.archive_file.instance_scheduler_solution_creator_lambda_zip.output_base64sha256


  runtime = "python3.8"
  memory_size = 128
  timeout = 900

  layers = [var.requests_layer]
  
  tags = {
    "platform_donotdelete" = "yes"
  }
}


