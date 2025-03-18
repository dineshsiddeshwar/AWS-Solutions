terraform {
  backend "s3" {
    bucket         = "terraform-remotestate-pfinternal"
    key            = "mcqa/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "mcqa-terraform-remotelock-pfinternal"
    encrypt        = true
  }
}

