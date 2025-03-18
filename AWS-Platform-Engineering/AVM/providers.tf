provider "aws" {
  region = "us-east-1"
}

provider "aws" {
  alias  = "eu-west-1"
  region = "eu-west-1"
}

provider "aws" {
  alias  = "us-east-2"
  region = "us-east-2"
}

provider "aws" {
  alias  = "us-west-1"
  region = "us-west-1"
}

provider "aws" {
  alias  = "us-west-2"
  region = "us-west-2"
}

provider "aws" {
  alias  = "ap-south-1"
  region = "ap-south-1"
}

provider "aws" {
  alias  = "ap-southeast-2"
  region = "ap-southeast-2"
}

provider "aws" {
  alias  = "ap-southeast-1"
  region = "ap-southeast-1"
}

provider "aws" {
  alias  = "eu-central-1"
  region = "eu-central-1"
}

provider "aws" {
  alias  = "ap-northeast-2"
  region = "ap-northeast-2"
}

provider "aws" {
  alias  = "eu-north-1"
  region = "eu-north-1"
}

provider "aws" {
  alias  = "ap-northeast-1"
  region = "ap-northeast-1"
}

provider "aws" {
  alias  = "ca-central-1"
  region = "ca-central-1"
}

provider "aws" {
  alias  = "eu-west-2"
  region = "eu-west-2"
}

provider "aws" {
  alias  = "sa-us-east-1"
  region  = "us-east-1"
  access_key = "TFC_SHARED_ACCOUNT_KEY"
  secret_key = "TFC_SHARED_ACCOUNT_SECRET"
}

provider "aws" {
  alias  = "pa-us-east-1"
  region  = "us-east-1"
  access_key = "TFC_PAYER_ACCOUNT_KEY"
  secret_key = "TFC_PAYER_ACCOUNT_SECRET"
}

provider "aws" {
  alias  = "sa-eu-west-1"
  region  = "eu-west-1"
  access_key = "TFC_SHARED_ACCOUNT_KEY"
  secret_key = "TFC_SHARED_ACCOUNT_SECRET"
}

provider "aws" {
  alias  = "sa-ap-southeast-1"
  region  = "ap-southeast-1"
  access_key = "TFC_SHARED_ACCOUNT_KEY"
  secret_key = "TFC_SHARED_ACCOUNT_SECRET"
}
