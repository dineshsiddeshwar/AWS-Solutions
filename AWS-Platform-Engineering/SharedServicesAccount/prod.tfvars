iam = {
"s3_bucket": "master-prod-ch-billing-da-2",
"platform_cloudhealth_external_id" : "c77460390542f0fe486c6adbba257e",
"platform_cloudhealth_account" : "454464851268",
"platform_shared_account" : "771319309933"
}


ou_principals = {
  "privateProduction" = "arn:aws:organizations::604596384198:ou/o-3dr03gfhjr/ou-sdpg-kdgducg0",
  "hybridAccount" = "arn:aws:organizations::604596384198:ou/o-3dr03gfhjr/ou-sdpg-npy37s4n",
  "privateStaging"= "arn:aws:organizations::604596384198:ou/o-3dr03gfhjr/ou-sdpg-4vidyeqk",
  "privateException" = "arn:aws:organizations::604596384198:ou/o-3dr03gfhjr/ou-sdpg-vqfh6169",
  "Managed_Services"="arn:aws:organizations::604596384198:ou/o-3dr03gfhjr/ou-sdpg-dtt2388g",
  "NON-Prod-Private"="arn:aws:organizations::604596384198:ou/o-3dr03gfhjr/ou-sdpg-0efqj8yj",
  "NON-Prod-Hybrid"="arn:aws:organizations::604596384198:ou/o-3dr03gfhjr/ou-sdpg-d272vhho",
  "Prod-Private"="arn:aws:organizations::604596384198:ou/o-3dr03gfhjr/ou-sdpg-ycd3k392",
  "Prod-Hybrid"="arn:aws:organizations::604596384198:ou/o-3dr03gfhjr/ou-sdpg-nvzlodt1",
  "Shared-Services-Private"="arn:aws:organizations::604596384198:ou/o-3dr03gfhjr/ou-sdpg-gmpwmejp",
  "Shared-Services-Hybrid"="arn:aws:organizations::604596384198:ou/o-3dr03gfhjr/ou-sdpg-6m4gp4di",
  "RESPC-Migration"="arn:aws:organizations::604596384198:ou/o-3dr03gfhjr/ou-sdpg-vc3iqnav"
}

vpc_all_details = {
  "us-east-1"= {
      action_type = {
        "createVPC" = {
        cidr = "10.93.127.0/24",
        securitygroupname= "sharedvpcsecgroup",
        private = ["10.95.112.32/27","10.93.128.0/17","10.95.113.192/27","10.93.0.0/16","10.93.58.0/23","10.124.128.0/17","10.105.159.96/27","10.105.128.0/19"],
        Infoblox1 = "10.223.121.217",
        Infoblox2 = "10.223.121.246",
        hostedzone_ids = "",
        subnets = {
        "subnet1a" = {
        AvailabilityZone = "us-east-1a"
        Subnet_cidr = "10.93.127.0/25"
        route53_iplist = ["10.93.127.113","10.93.127.22","10.93.127.87"]
        Subnet_name = "platform-shared-subnet-1A"
        },
        "subnet1b" = {
        AvailabilityZone = "us-east-1b"
        Subnet_cidr = "10.93.127.128/25"
        route53_iplist = ["10.93.127.242","10.93.127.207","10.93.127.163"]
        Subnet_name = "platform-shared-subnet-1B"
        }
	}
  }}},
    
  "eu-west-1"= {
      action_type = {
       "createVPC" ={
        cidr = "10.95.127.0/24",
        securitygroupname= "sharedvpcsecgroup",
        private = ["10.95.121.128/26","10.95.121.64/26","10.95.113.196/32","10.95.113.192/27","10.95.0.0/16","10.105.160.0/19"],
        Infoblox1 = "10.223.121.94",
        Infoblox2 = "10.223.121.126",
        hostedzone_ids = "",
        subnets = {
        "subnet1a" = {
        AvailabilityZone = "eu-west-1a"
        Subnet_cidr = "10.95.127.0/25"
        route53_iplist = ["10.95.127.77","10.95.127.92","10.95.127.79"]
        Subnet_name = "platform-shared-subnet-1A"
        },
        "subnet1b" = {
        AvailabilityZone = "eu-west-1b"
        Subnet_cidr = "10.95.127.128/25"
        route53_iplist = ["10.95.127.173","10.95.127.197","10.95.127.250"]
        Subnet_name = "platform-shared-subnet-1B"
        }}
  }}},

  "ap-southeast-1"= {
      action_type = {
        "createVPC" ={
        cidr = "10.124.64.0/24",
        securitygroupname= "sharedvpcsecuritygroup",
        private = ["10.124.64.0/18","10.124.222.0/23"],
        hostedzone_ids = "",
        subnets = {
        "subnet1a" = {
        AvailabilityZone = "ap-southeast-1a"
        Subnet_cidr = "10.124.64.0/25"
        route53_iplist = ["10.124.64.86","10.124.64.82","10.124.64.123"]
        Subnet_name = "platform-shared-subnet-1A"
        },
        "subnet1b" = {
        AvailabilityZone = "ap-southeast-1b"
        Subnet_cidr = "10.124.64.128/25"
        route53_iplist = ["10.124.64.155","10.124.64.154","10.124.64.214"]
        Subnet_name = "platform-shared-subnet-1B"
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
    "kinesis-streams-Endpoint" = {
      service_name_suffix       = "kinesis-streams"
      hostedzone_suffix ="kinesis"
      service_type = "Interface"
    },
    "kinesis-firehose-Endpoint" = {
      service_name_suffix       = "kinesis-firehose"
      hostedzone_suffix ="firehose"
      service_type = "Interface"
    },
    "AppStreamAPI-Endpoint" = {
      service_name_suffix       = "appstream.api"
      hostedzone_suffix ="appstream2"
      service_type = "Interface"
    },
    "AppStreamStreaming-Endpoint" = {
      service_name_suffix       = "appstream.streaming"
      hostedzone_suffix ="streaming.appstream"
      service_type = "Interface"
    },
    "athena-Endpoint" = {
      service_name_suffix       = "athena"
      service_type = "Interface"
    },
    "ecs-Endpoint" = {
      service_name_suffix       = "ecs"
      service_type = "Interface"
    },
    "ecs-agent-Endpoint" = {
      service_name_suffix       = "ecs-agent"
      hostedzone_suffix = "ecs-a"
      service_type = "Interface"
    },
    "ecs-telemetry-Endpoint" = {
      service_name_suffix       = "ecs-telemetry"
      hostedzone_suffix = "ecs-t"
      service_type = "Interface"
    },
    "elasticfilesystem-Endpoint" = {
      service_name_suffix       = "elasticfilesystem"
      service_type = "Interface"
    },
    "elasticfilesystem-fips-Endpoint" = {
      service_name_suffix       = "elasticfilesystem-fips"
      service_type = "Interface"
    },
    "glue-Endpoint" = {
      service_name_suffix       = "glue"
      service_type = "Interface"
    },
    "SageMakerAPI-Endpoint" = {
      service_name_suffix       = "sagemaker.api"
      hostedzone_suffix = "api.sagemaker"
      service_type = "Interface"
    },
    "SageMakerRuntime-Endpoint" = {
      service_name_suffix       = "sagemaker.runtime"
      hostedzone_suffix = "runtime.sagemaker"
      service_type = "Interface"
    },
    "servicecatalog-Endpoint" = {
      service_name_suffix       = "servicecatalog"
      service_type = "Interface"
    },
    "StepFunction-Endpoint" = {
      service_name_suffix       = "states"
      service_type = "Interface"
    },
    "workspaces-Endpoint" = {
      service_name_suffix       = "workspaces"
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
    "rds-endpoint" = {
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
env_type = "prod"
s3_bucket = "master-prod-ch-billing-da-2"
platform_cloudhealth_external_id = "c77460390542f0fe486c6adbba257e"
platform_cloudhealth_account = "454464851268"
platform_shared_account = "771319309933"
isproduction=true
env_instanceprofile_suffix = "Z2VR5ryS6Xko"
