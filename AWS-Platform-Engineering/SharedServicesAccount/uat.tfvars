iam = {
"s3_bucket": "master-accpt-ch-billing-da-2",
"platform_cloudhealth_external_id" : "c77460390542f0fe486c6adbba257e",
"platform_cloudhealth_account" : "454464851268",
"platform_shared_account" = "566854060281"
}


ou_principals = {
  "privateProduction" = "arn:aws:organizations::136349175397:ou/o-b3vc1sj5j5/ou-qkhr-g5muobex",
  "hybridAccount" = "arn:aws:organizations::136349175397:ou/o-b3vc1sj5j5/ou-qkhr-248fbf5e",
  "privateStaging"= "arn:aws:organizations::136349175397:ou/o-b3vc1sj5j5/ou-qkhr-ouggsdwn",
  "privateException" = "arn:aws:organizations::136349175397:ou/o-b3vc1sj5j5/ou-qkhr-ok6kh8k0",
  "Managed_Services"="arn:aws:organizations::136349175397:ou/o-b3vc1sj5j5/ou-qkhr-pch5lram",
  "NON-Prod-Private"="arn:aws:organizations::136349175397:ou/o-b3vc1sj5j5/ou-qkhr-ggjzn6tp",
  "NON-Prod-Hybrid"="arn:aws:organizations::136349175397:ou/o-b3vc1sj5j5/ou-qkhr-7z3edvcr",
  "Prod-Private"="arn:aws:organizations::136349175397:ou/o-b3vc1sj5j5/ou-qkhr-9b3put9a",
  "Prod-Hybrid"="arn:aws:organizations::136349175397:ou/o-b3vc1sj5j5/ou-qkhr-oonpepuu",
  "Shared-Services-Private"="arn:aws:organizations::136349175397:ou/o-b3vc1sj5j5/ou-qkhr-dggsb2xm",
  "Shared-Services-Hybrid"="arn:aws:organizations::136349175397:ou/o-b3vc1sj5j5/ou-qkhr-xtg8v5a7",
  "RESPC-Migration"="arn:aws:organizations::136349175397:ou/o-b3vc1sj5j5/ou-qkhr-e9s32k7x"
}

vpc_all_details = {
  "us-east-1"= {
      action_type = {
        "createVPC" = {
        cidr = "10.93.126.64/26",
        secondary_cidr = "10.93.129.0/25",
        securitygroupname= "sharedvpcsecgroup",
        private = ["10.93.0.0/16"],
        Infoblox1 = "10.223.121.217",
        Infoblox2 = "10.223.121.246",
        hostedzone_ids = "",
        subnets = {
        "subnet1a" = {
        AvailabilityZone = "us-east-1a"
        Subnet_cidr = "10.93.126.64/27"
        route53_iplist = ["10.93.126.90","10.93.126.77","10.93.126.69"]
        Subnet_name = "platform-shared-subnet-1A"
        },
        "subnet1b" = {
        AvailabilityZone = "us-east-1b"
        Subnet_cidr = "10.93.126.96/27"
        route53_iplist = ["10.93.126.117","10.93.126.104","10.93.126.123"]
        Subnet_name = "platform-shared-subnet-1B"
        },
        "subnet2a" = {
        AvailabilityZone = "us-east-1a"
        Subnet_cidr = "10.93.129.0/26"
        Subnet_name = "platform-shared-subnet-2A"
        },
        "subnet2b" = {
        AvailabilityZone = "us-east-1b"
        Subnet_cidr = "10.93.129.64/26"
        Subnet_name = "platform-shared-subnet-2B"
        }
	}
  }}},
    
  "eu-west-1"= {
      action_type = {
        "createVPC" ={
        cidr = "10.95.126.64/26",
        secondary_cidr = "10.95.4.0/25",
        securitygroupname= "sharedvpcsecgroup",
        private = ["10.95.0.0/16"],
        Infoblox1 = "10.223.121.94",
        Infoblox2 = "10.223.121.126",
        hostedzone_ids = "",
        subnets = {
        "subnet1a" = {
        AvailabilityZone = "eu-west-1a"
        Subnet_cidr = "10.95.126.64/27"
        route53_iplist = ["10.95.126.89","10.95.126.71","10.95.126.79"]
        Subnet_name = "platform-shared-subnet-1A"
        },
        "subnet1b" = {
        AvailabilityZone = "eu-west-1b"
        Subnet_cidr = "10.95.126.96/27"
        route53_iplist = ["10.95.126.117","10.95.126.125","10.95.126.112"]
        Subnet_name = "platform-shared-subnet-1B"
        },
        "subnet2a" = {
        AvailabilityZone = "eu-west-1a"
        Subnet_cidr = "10.95.4.0/26"
        Subnet_name = "platform-shared-subnet-2A"
        },
        "subnet2b" = {
        AvailabilityZone = "eu-west-1b"
        Subnet_cidr = "10.95.4.64/26"
        Subnet_name = "platform-shared-subnet-2B"
        }}
  }}},

  "ap-southeast-1"= {
      action_type = {
        "createVPC" ={
        cidr = "10.124.24.0/25",
        secondary_cidr = "10.124.27.128/25",
        securitygroupname= "sharedvpcsecuritygroup",
        private = ["10.124.24.0/21"],
        hostedzone_ids = "",
        subnets = {
        "subnet1a" = {
        AvailabilityZone = "ap-southeast-1a"
        Subnet_cidr = "10.124.24.0/26"
        route53_iplist = ["10.124.24.58","10.124.24.30","10.124.24.10"]
        Subnet_name = "platform-shared-subnet-1A"
        },
        "subnet1b" = {
        AvailabilityZone = "ap-southeast-1b"
        Subnet_cidr = "10.124.24.64/26"
        route53_iplist = ["10.124.24.72","10.124.24.109","10.124.24.84"]
        Subnet_name = "platform-shared-subnet-1B"
        },
        "subnet2a" = {
        AvailabilityZone = "ap-southeast-1a"
        Subnet_cidr = "10.124.27.128/26"
        Subnet_name = "platform-shared-subnet-2A"
        },
        "subnet2b" = {
        AvailabilityZone = "ap-southeast-1b"
        Subnet_cidr = "10.124.27.192/26"
        Subnet_name = "platform-shared-subnet-2B"
        }}
  }}}
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
    "ECRAPI-Endpoint" = {
      service_name_suffix       = "ecr.api"
      hostedzone_suffix ="api.ecr"
      service_type = "Interface"
    }
    "ECRDocker-Endpoint" = {
      service_name_suffix       = "ecr.dkr"
      hostedzone_suffix ="dkr.ecr"
      service_type = "Interface"
    },
    "secretsmanager-Endpoint" = {
      service_name_suffix       = "secretsmanager"
      service_type = "Interface"
    },
    "kms-Endpoint" = {
      service_name_suffix       = "kms"
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
env_type = "acceptance"
s3_bucket = "master-accpt-ch-billing-da-2"
platform_cloudhealth_external_id = "454464851268"
platform_cloudhealth_account = "c77460390542f0fe486c6adbba257e"
platform_shared_account = "566854060281"
isproduction=false
env_instanceprofile_suffix = "hpMyD5MehV8S"