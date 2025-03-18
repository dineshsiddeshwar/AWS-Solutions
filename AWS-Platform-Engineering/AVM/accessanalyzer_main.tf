module "us-east-1-accessanalyzers" {
  source = "./AccessAnalyzers"

  region = "us-east-1"
}

module "eu-west-1-accessanalyzers" {
  source = "./AccessAnalyzers"

  region = "eu-west-1"
  providers = {
    aws = aws.eu-west-1
   }
}

module "us-east-2-accessanalyzers" {
  source = "./AccessAnalyzers"

  region = "us-east-2"
  providers = {
    aws = aws.us-east-2
   }
}

module "us-west-1-accessanalyzers" {
  source = "./AccessAnalyzers"

  region = "us-west-1"
  providers = {
    aws = aws.us-west-1
   }
}

module "us-west-2-accessanalyzers" {
  source = "./AccessAnalyzers"

  region = "us-west-2"
  providers = {
    aws = aws.us-west-2
   }
}

module "ap-south-1-accessanalyzers" {
  source = "./AccessAnalyzers"

  region = "ap-south-1"
  providers = {
    aws = aws.ap-south-1
   }
}

module "ap-southeast-2-accessanalyzers" {
  source = "./AccessAnalyzers"

  region = "ap-southeast-2"
  providers = {
    aws = aws.ap-southeast-2
   }
}

module "ap-southeast-1-accessanalyzers" {
  source = "./AccessAnalyzers"

  region = "ap-southeast-1"
  providers = {
    aws = aws.ap-southeast-1
   }
}

module "eu-central-1-accessanalyzers" {
  source = "./AccessAnalyzers"

  region = "eu-central-1"
  providers = {
    aws = aws.eu-central-1
   }
}

module "eu-west-2-accessanalyzers" {
  source = "./AccessAnalyzers"

  region = "eu-west-2"
  providers = {
    aws = aws.eu-west-2
   }
}

module "ap-northeast-2-accessanalyzers" {
  source = "./AccessAnalyzers"

  region = "ap-northeast-2"
  providers = {
    aws = aws.ap-northeast-2
   }
}

module "eu-north-1-accessanalyzers" {
  source = "./AccessAnalyzers"

  region = "eu-north-1"
  providers = {
    aws = aws.eu-north-1
   }
}

module "ap-northeast-1-accessanalyzers" {
  source = "./AccessAnalyzers"

  region = "ap-northeast-1"
  providers = {
    aws = aws.ap-northeast-1
   }
}

module "ca-central-1-accessanalyzers" {
  source = "./AccessAnalyzers"

  region = "ca-central-1"
  providers = {
    aws = aws.ca-central-1
   }
}
