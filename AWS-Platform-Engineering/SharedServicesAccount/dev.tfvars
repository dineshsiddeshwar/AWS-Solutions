iam = {
"s3_bucket": "cloudhealth-billing-da-2",
"platform_cloudhealth_external_id" : "c77460390542f0fe486c6adbba257e",
"platform_cloudhealth_account" : "454464851268",
"platform_shared_account" : "111923448168"
}


ou_principals = {
  "privateProduction" = "arn:aws:organizations::364355817034:ou/o-djaer94p95/ou-93cv-2ph2c0tc",
  "hybridAccount" = "arn:aws:organizations::364355817034:ou/o-djaer94p95/ou-93cv-o3i3n5qr",
  "privateStaging"= "arn:aws:organizations::364355817034:ou/o-djaer94p95/ou-93cv-chay3epk",
  "privateException" = "arn:aws:organizations::364355817034:ou/o-djaer94p95/ou-93cv-3o8ln75z",
  "Managed_Services"="arn:aws:organizations::364355817034:ou/o-djaer94p95/ou-93cv-l9id6b28",
  "NON-Prod-Private"="arn:aws:organizations::364355817034:ou/o-djaer94p95/ou-93cv-zxdzbt2b",
  "NON-Prod-Hybrid"="arn:aws:organizations::364355817034:ou/o-djaer94p95/ou-93cv-nt07gw4m",
  "Prod-Private"="arn:aws:organizations::364355817034:ou/o-djaer94p95/ou-93cv-70dkgazs",
  "Prod-Hybrid"="arn:aws:organizations::364355817034:ou/o-djaer94p95/ou-93cv-1hnw0pde",
  "Shared-Services-Private"="arn:aws:organizations::364355817034:ou/o-djaer94p95/ou-93cv-9xpzru50",
  "Shared-Services-Hybrid"="arn:aws:organizations::364355817034:ou/o-djaer94p95/ou-93cv-5nlttx2a",
  "RESPC-Migration"="arn:aws:organizations::364355817034:ou/o-djaer94p95/ou-93cv-kz8l46qu"
}

vpc_all_details = {
  "us-east-1"= {
      action_type = {
        "createVPC" = {
        cidr = "10.93.3.0/26",
        secondary_cidr = "10.93.1.0/25",
        securitygroupname= "sharedvpcsecgroup",
        private = ["10.93.0.0/16"],
        Infoblox1 = "10.223.121.217",
        Infoblox2 = "10.223.121.246",
        hostedzone_ids = "",
        subnets = {
        "subnet1a" = {
        AvailabilityZone = "us-east-1a"
        Subnet_cidr = "10.93.3.0/27"
        route53_iplist = ["10.93.3.21","10.93.3.16","10.93.3.15"]
        Subnet_name = "platform-shared-subnet-1A"
        },
        "subnet1b" = {
        AvailabilityZone = "us-east-1b"
        Subnet_cidr = "10.93.3.32/27"
        route53_iplist = ["10.93.3.47","10.93.3.36","10.93.3.56"]
        Subnet_name = "platform-shared-subnet-1B"
        },
        "subnet2a" = {
        AvailabilityZone = "us-east-1a"
        Subnet_cidr = "10.93.1.0/26"
        Subnet_name = "platform-shared-subnet-2A"
        },
        "subnet2b" = {
        AvailabilityZone = "us-east-1b"
        Subnet_cidr = "10.93.1.64/26"
        Subnet_name = "platform-shared-subnet-2B"
        }

	}
  }
  }},
    
  "eu-west-1"= {
      action_type = {
        "createVPC" ={
        cidr = "10.95.3.0/26",
        secondary_cidr = "10.95.90.0/25",
        securitygroupname= "sharedvpcsecgroup",
        private = ["10.95.0.0/16"],
        Infoblox1 = "10.223.121.94",
        Infoblox2 = "10.223.121.126",
        hostedzone_ids = "",
        subnets = {
        "subnet1a" = {
        AvailabilityZone = "eu-west-1a"
        Subnet_cidr = "10.95.3.0/27"
        route53_iplist = ["10.95.3.20","10.95.3.15","10.95.3.14"]
        Subnet_name = "platform-shared-subnet-1A"
        },
        "subnet1b" = {
        AvailabilityZone = "eu-west-1b"
        Subnet_cidr = "10.95.3.32/27"
        route53_iplist = ["10.95.3.46","10.95.3.36","10.95.3.38"]
        Subnet_name = "platform-shared-subnet-1B"
        },
        "subnet2a" = {
        AvailabilityZone = "eu-west-1a"
        Subnet_cidr = "10.95.90.0/26"
        Subnet_name = "platform-shared-subnet-2A"
        },
        "subnet2b" = {
        AvailabilityZone = "eu-west-1b"
        Subnet_cidr = "10.95.90.64/26"
        Subnet_name = "platform-shared-subnet-2B"
        }}
  }
  }},

  "ap-southeast-1"= {
      action_type = {
        "createVPC" = {
        cidr = "10.124.16.0/25",
        secondary_cidr = "10.124.19.0/25",
        securitygroupname= "sharedvpcsecuritygroup",
        private = ["10.124.16.0/21"],
        hostedzone_ids = "",
        subnets = {
        "subnet1a" = {
        AvailabilityZone = "ap-southeast-1a"
        Subnet_cidr = "10.124.16.0/26"
        route53_iplist = ["10.124.16.22","10.124.16.15","10.124.16.57"]
        Subnet_name = "platform-shared-subnet-1A"
        },
        "subnet1b" = {
        AvailabilityZone = "ap-southeast-1b"
        Subnet_cidr = "10.124.16.64/26"
        route53_iplist = ["10.124.16.126","10.124.16.99","10.124.16.91"]
        Subnet_name = "platform-shared-subnet-1B"
        },
        "subnet2a" = {
        AvailabilityZone = "ap-southeast-1a"
        Subnet_cidr = "10.124.19.0/26"
        Subnet_name = "platform-shared-subnet-2A"
        },
        "subnet2b" = {
        AvailabilityZone = "ap-southeast-1b"
        Subnet_cidr = "10.124.19.64/26"
        Subnet_name = "platform-shared-subnet-2B"
        }}
  }
  }}
 }

#service_name_suffix is only required in the variables
#actual service_name will be set to "com.amazonaws.{var.region}.{var.service_name_suffix}"

endpoints = {
    "ec2messages-Endpoint" = {
      service_name_suffix       = "ec2messages"
      service_type = "Interface"
    },
   "sqs-Endpoint" = {
      service_name_suffix       = "sqs"
      service_type="Interface"
    },
     "cloudtrail-Endpoint" = {
      service_name_suffix       = "cloudtrail"
      service_type = "Interface"
    },
     "CloudWatchLogs-Endpoint" = {
      service_name_suffix       = "logs"
      service_type = "Interface"
    },
     "ssmmessages-Endpoint" = {
      service_name_suffix       = "ssmmessages"
      service_type = "Interface"
    },
     "CloudWatchEvents-Endpoint" = {
      service_name_suffix       = "events"
      service_type = "Interface"
    },
     "ssm-Endpoint" = {
      service_name_suffix       = "ssm"
      service_type = "Interface"
    },
     "CloudWatchMonitoring-Endpoint" = {
      service_name_suffix       = "monitoring"
      service_type = "Interface"
    },
     "sns-Endpoint" = {
      service_name_suffix       = "sns"
      service_type = "Interface"
    },
     "S3PrivateLink-Endpoint" = {
      service_name_suffix       = "s3"
      service_type = "Interface"
    },
     "LambdaPrivateLink-Endpoint" = {
      service_name_suffix       = "lambda"
      service_type = "Interface"
    },
      "api-gateway-Endpoint" = {
      service_name_suffix       = "execute-api"
      hostedzone_suffix ="api-gateway"
      service_type = "Interface"
    },
     "textract-Endpoint" = {
      service_name_suffix       = "textract"
      service_type = "Interface"
    },
     "rekognition-Endpoint" = {
      service_name_suffix       = "rekognition"
      service_type = "Interface"
    },
     "comprehend-Endpoint" = {
      service_name_suffix       = "comprehend"
      service_type = "Interface"
    },
     "dms-Endpoint" = {
     service_name_suffix       = "dms"
     service_type = "Interface"
    }
  }

endpoint_extended = {
    "transfer-Endpoint" = {
      service_name_suffix       = "transfer"
      service_type = "Interface"
    },
    "polly-Endpoint" = {
      service_name_suffix       = "polly"
      service_type = "Interface"
    },
    "ApacheAirflowAPI-Endpoint" = {
      service_name_suffix       = "airflow.api"
      service_type = "Interface"
    },
    "ApacheAirflowENV-Endpoint" = {
      service_name_suffix       = "airflow.env"
      service_type = "Interface"
    },
    "ApacheAirflowOPS-Endpoint" = {
      service_name_suffix       = "airflow.ops"
      service_type = "Interface"
    },
    "Aps-Endpoint" = {
      service_name_suffix       = "aps"
      service_type = "Interface"
    },
    "Aps-workspaces-Endpoint" = {
      service_name_suffix       = "aps-workspaces"
      service_type = "Interface"
    },
    "rds-Endpoint" = {
      service_name_suffix       = "rds"
      service_type = "Interface"
    },
    "eks-Endpoint" = {
      service_name_suffix       = "eks"
      service_type = "Interface"
    },
    "dynamodb-Endpoint" = {
      service_name_suffix       = "dynamodb"
      service_type = "Interface"
    },
    "grafana-Endpoint" = {
      service_name_suffix       = "grafana"
      service_type = "Interface"
    },
    "redshift-Endpoint" = {
      service_name_suffix       = "redshift"
      service_type = "Interface"
    },
    "elasticloadbalancing-Endpoint" = {
      service_name_suffix       = "elasticloadbalancing"
      service_type = "Interface"
    },
    "fsx-Endpoint" = {
      service_name_suffix       = "fsx"
      service_type = "Interface"
    },
    "config-Endpoint" = {
      service_name_suffix       = "config"
      service_type = "Interface"
    },
    "elasticache-Endpoint" = {
      service_name_suffix       = "elasticache"
      service_type = "Interface"
    },
    "securityhub-Endpoint" = {
      service_name_suffix       = "securityhub"
      service_type = "Interface"
    },
    "backup-Endpoint" = {
      service_name_suffix       = "backup"
      service_type = "Interface"
    },
    "codebuild-Endpoint" = {
      service_name_suffix       = "codebuild"
      service_type = "Interface"
    },
    "appsync-api-Endpoint" = {
      service_name_suffix       = "appsync-api"
      service_type = "Interface"
    },
    "quicksight-website-Endpoint" = {
      service_name_suffix       = "quicksight-website"
      service_type = "Interface"
    }
}


rules = {
  "allow_all_traffic_from_private_cidr" = ["0","0","-1","allow_all_traffic_from_private_cidr"]
}

ingress_rules = [ "allow_all_traffic_from_private_cidr" ]
env_type = "dev"
s3_bucket = "cloudhealth-billing-da-2"
platform_cloudhealth_external_id = "454464851268"
platform_cloudhealth_account = "c77460390542f0fe486c6adbba257e"
platform_shared_account = "111923448168"
isproduction=false
env_instanceprofile_suffix = "Zfn3FtgV3b5i"