
# Ensure VPC endpoints are used to access airflow service
# Ensure MWAA utilizes VPC endpoints to prevent public access
resource "aws_vpc_endpoint" "mwaa_vpc_endpoint" {
  #(Required) The ID of the VPC in which the endpoint will be used
  vpc_id = data.aws_vpc.aws_vpc_id.id
  #(Required) The service name
  service_name        = var.mwaa_service_name      # string
  vpc_endpoint_type   = var.mwaa_vpc_endpoint_type # string 
  security_group_ids  = var.mwaa_sg_ids            # list(string)
  private_dns_enabled = true
}

# MWAA

#  Enforce least privilege permission policies

resource "aws_iam_user" "mwaa_iam_user" {
  name = var.mwaa_iam_user
  tags = var.mwaa_tags # map(string)
}

resource "aws_iam_access_key" "mwaa_user_iam_access_key" {
  user = aws_iam_user.mwaa_iam_user.name
}

resource "aws_iam_policy" "mwaa_iam_policy" {
  name   = var.mwaa_iam_policy_name
  policy = data.template_file.mwaa_iam_policy_file.rendered
  tags   = var.mwaa_tags # map(string)
}

resource "aws_iam_user_policy_attachment" "mwaa_test_attach_iam_policy" {
  user       = aws_iam_user.mwaa_iam_user.name
  policy_arn = aws_iam_policy.mwaa_iam_policy.arn
}


#  Ensure to configure MWAA execution roles to enforce least privilege
resource "aws_iam_role" "mwaa_iam_execution_role" {
  name               = var.mwaa_iam_execution_role_name
  assume_role_policy = data.template_file.mwaa_iam_execution_role_file.rendered
  tags               = var.mwaa_tags #map
}

resource "aws_iam_policy" "mwaa_iam_execution_policy" {
  name   = var.mwaa_iam_execution_policy_name
  path   = var.mwaa_iam_execution_policy_path
  policy = data.template_file.mwaa_iam_execution_policy_file.rendered
  tags   = var.mwaa_tags # map(string)
}

resource "aws_iam_role_policy_attachment" "mwaa_iam_execution_role_policy_attachment" {
  role       = aws_iam_role.mwaa_iam_execution_role.name
  policy_arn = aws_iam_policy.mwaa_iam_execution_policy.arn
}



# MWAA Environemnt 

resource "aws_mwaa_environment" "mwaa_environment" {
  name                 = var.mwaa_environment_name                # string
  source_bucket_arn    = data.aws_s3_bucket.mwaa_s3_bucket.arn
  # Ensure Amazon MWAA environment's metadatabase and DAGs are secure
  # S3 bucket security implemented under seperate module
  dag_s3_path          = var.mwaa_enviroment_dag_s3_path          # string
  plugins_s3_path      = var.mwaa_enviroment_plugins_s3_path      # string
  requirements_s3_path = var.mwaa_enviroment_requirements_s3_path # string
  execution_role_arn   = aws_iam_role.mwaa_iam_execution_role.arn # string
  max_workers          = var.mwaa_max_workers                     # number
  # Ensure MWAA webserver access is set to private
  webserver_access_mode = "PRIVATE_ONLY"
  # Ensure data is encrypted at rest using organization managed key(CMK)
  kms_key = var.mwaa_kms_key_arn # string

  network_configuration {
    security_group_ids = var.mwaa_environment_sg_ids # list(string)
    #  Ensure MWAA environment is provisioned within organization VPC & private subnets
    subnet_ids = var.mwaa_environment_vpc_private_subnet_id # set(string)
  }

  # 9. Ensure to enable CloudWatch metrics for Amazon MWAA
  logging_configuration {
    dag_processing_logs {
      enabled   = true
      log_level = "INFO"
    }

    scheduler_logs {
      enabled   = true
      log_level = "INFO"
    }

    task_logs {
      enabled   = true
      log_level = "INFO"
    }

    webserver_logs {
      enabled   = true
      log_level = "INFO"
    }

    worker_logs {
      enabled   = true
      log_level = "INFO"
    }
  }
  #  Ensure MWAA Resources are tagged according to organization standard
  tags = var.mwaa_tags # map(string)
}
#  Ensure MWAA connections are encrypted in transit using TLS 1.2
/* 
By default Amazon encrypts the MWAA objects in transit between AWS services. If you are writing
applications that interact with other services it is required to use at minimum TLS 1.2
*/


#  Ensure to configure an Apache Airflow connection using a Secrets Manager secret key
data "aws_secretsmanager_secret" "mwaa_logging_user_secretsmanager_secret" {
  name        = var.mwaa_logging_user_secretsmanager_secret_name
}

resource "aws_secretsmanager_secret_policy" "mwaa_logging_user_secretsmanager_secret_policy" {
  secret_arn = data.aws_secretsmanager_secret.mwaa_logging_user_secretsmanager_secret.arn
  policy     = data.template_file.mwaa_logging_user_secretsmanager_secret_policy_file
}

# Ensure CloudTrail logging is enabled for MWAA
# Implementation already deployed per organisation standard.

