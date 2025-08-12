import csv

def get_recommendation(service):
    recommendations = {
        # AWS
        "ec2": [
            "Terminate unused EC2 instances to save costs.",
            "Use spot instances for non-critical workloads.",
            "Right-size EC2 instances based on usage.",
            "Purchase Reserved Instances for predictable workloads.",
            "Enable EC2 Auto Scaling to match demand.",
            "Monitor and optimize EBS volumes attached to EC2.",
            "Use Savings Plans for compute resources.",
            "Automate instance scheduling to shut down during off-hours.",
            "Consolidate workloads using EC2 placement groups.",
            "Leverage Graviton-based instances for cost/performance."
        ],
        "rds": [
            "Switch to reserved RDS instances for savings.",
            "Enable RDS storage auto-scaling.",
            "Right-size RDS instances and storage.",
            "Enable Multi-AZ only for critical workloads.",
            "Delete unused RDS snapshots and automated backups.",
            "Use Aurora Serverless for variable workloads.",
            "Monitor RDS performance and optimize queries.",
            "Enable RDS Performance Insights to identify bottlenecks.",
            "Consolidate databases where possible."
        ],
        "s3": [
            "Enable S3 lifecycle policies to delete old objects.",
            "Use S3 Intelligent-Tiering for cost savings.",
            "Move infrequently accessed data to Glacier or Deep Archive.",
            "Enable S3 versioning and regularly clean up old versions.",
            "Compress objects before storing in S3.",
            "Review and remove unused buckets.",
            "Enable default encryption to avoid compliance costs.",
            "Monitor S3 usage and set alerts for unexpected growth."
        ],
        "elb": [
            "Remove unused load balancers.",
            "Enable connection draining to optimize costs.",
            "Use Application Load Balancer (ALB) for HTTP/HTTPS workloads.",
            "Consolidate traffic to fewer load balancers.",
            "Monitor ELB metrics and scale down when possible.",
            "Delete unused target groups and listeners."
        ],
        "lambda": [
            "Optimize Lambda memory allocation.",
            "Remove unused Lambda functions.",
            "Use Lambda Power Tuning to find optimal settings.",
            "Monitor invocation frequency and duration.",
            "Consolidate functions where possible.",
            "Use provisioned concurrency only when needed.",
            "Review and optimize function code for efficiency."
        ],
        "dynamodb": [
            "Enable DynamoDB auto-scaling.",
            "Delete unused tables.",
            "Use on-demand capacity for unpredictable workloads.",
            "Enable TTL to automatically delete expired items.",
            "Monitor and optimize indexes.",
            "Consolidate tables and reduce item size."
        ],
        "cloudfront": [
            "Optimize cache behaviors.",
            "Remove unused distributions.",
            "Enable origin shield for cost savings.",
            "Compress content before delivery.",
            "Monitor CloudFront usage and invalidate unused objects."
        ],
        "ecr": [
            "Delete unused ECR repositories.",
            "Enable ECR lifecycle policies.",
            "Remove old container images.",
            "Enable image scanning to avoid security costs."
        ],
        "ecs": [
            "Scale down unused ECS clusters.",
            "Optimize ECS task definitions.",
            "Use Fargate Spot for cost savings.",
            "Monitor and right-size ECS services.",
            "Consolidate workloads into fewer clusters."
        ],
        "sagemaker": [
            "Stop idle SageMaker notebook instances.",
            "Delete unused models and endpoints.",
            "Use spot training for cost savings.",
            "Monitor and optimize instance types for training.",
            "Archive old experiments and models."
        ],
        "redshift": [
            "Pause unused Redshift clusters.",
            "Resize Redshift clusters for cost savings.",
            "Use concurrency scaling only when needed.",
            "Monitor and optimize query performance.",
            "Delete unused tables and databases."
        ],
        "elasticache": [
            "Delete unused ElastiCache clusters.",
            "Resize cache nodes to optimal size.",
            "Enable auto-discovery for scaling.",
            "Monitor cache usage and evict old data."
        ],
        "cloudwatch": [
            "Delete unused CloudWatch log groups.",
            "Reduce CloudWatch retention period.",
            "Aggregate metrics to reduce costs.",
            "Monitor and clean up custom metrics."
        ],
        "sns": [
            "Delete unused SNS topics.",
            "Review SNS subscription protocols.",
            "Consolidate notifications into fewer topics.",
            "Monitor message delivery and optimize filters."
        ],
        "sqs": [
            "Delete unused SQS queues.",
            "Enable SQS long polling.",
            "Monitor and optimize message retention.",
            "Consolidate queues where possible."
        ],
        # Azure
        "vm": [
            "Resize Azure VMs to optimize spending.",
            "Deallocate unused VMs.",
            "Purchase reserved VM instances for predictable workloads.",
            "Enable auto-shutdown for dev/test VMs.",
            "Monitor and optimize disk usage.",
            "Use Azure Hybrid Benefit for Windows Server and SQL Server.",
            "Move workloads to lower-cost regions if possible."
        ],
        "sql": [
            "Switch to reserved SQL Database capacity.",
            "Enable SQL elastic pools.",
            "Right-size SQL databases and DTUs.",
            "Enable automatic tuning and indexing.",
            "Delete unused databases and backups.",
            "Monitor query performance and optimize."
        ],
        "blob": [
            "Enable Azure Blob lifecycle management.",
            "Move infrequently accessed data to cool tier.",
            "Enable blob versioning and clean up old versions.",
            "Compress data before upload.",
            "Monitor and delete unused containers."
        ],
        "appsvc": [
            "Scale down unused App Service plans.",
            "Enable auto-scaling for App Services.",
            "Move workloads to lower pricing tiers.",
            "Monitor and optimize app service usage.",
            "Delete unused web apps and slots."
        ],
        "cosmos": [
            "Enable Cosmos DB autoscale throughput.",
            "Delete unused databases.",
            "Monitor and optimize RU/s allocation.",
            "Consolidate collections and databases."
        ],
        "aks": [
            "Scale down AKS node pools.",
            "Remove unused AKS clusters.",
            "Use spot nodes for non-critical workloads.",
            "Monitor and optimize pod resource requests."
        ],
        "containerinstance": [
            "Delete unused Container Instances.",
            "Optimize container resource allocation.",
            "Monitor and right-size container groups."
        ],
        "batch": [
            "Delete completed Batch jobs.",
            "Resize Batch pools for cost savings.",
            "Monitor and optimize job scheduling.",
            "Use low-priority VMs for batch workloads."
        ],
        "eventhub": [
            "Delete unused Event Hub namespaces.",
            "Scale down Event Hub throughput units.",
            "Monitor and optimize event retention.",
            "Consolidate event streams where possible."
        ],
        "redis": [
            "Resize Azure Redis Cache instances.",
            "Delete unused Redis caches.",
            "Monitor and optimize cache usage.",
            "Enable geo-replication only when needed."
        ],
        "monitor": [
            "Reduce Azure Monitor data retention.",
            "Delete unused monitoring resources.",
            "Aggregate metrics to reduce costs.",
            "Monitor and clean up custom logs."
        ],
        "storagequeue": [
            "Delete unused Storage Queues.",
            "Optimize queue message retention.",
            "Monitor and consolidate queues."
        ],
        "logicapp": [
            "Delete unused Logic Apps.",
            "Optimize Logic App workflows.",
            "Monitor and reduce connector usage."
        ],
        # GCP
        "gce": [
            "Terminate unused Compute Engine instances.",
            "Resize instances to lower machine types.",
            "Purchase committed use contracts for predictable workloads.",
            "Enable instance scheduling for off-hours.",
            "Monitor and optimize disk usage.",
            "Move workloads to lower-cost regions if possible."
        ],
        "cloudsql": [
            "Enable Cloud SQL automatic backups.",
            "Switch to committed use discounts.",
            "Right-size Cloud SQL instances and storage.",
            "Enable automatic storage increase only when needed.",
            "Delete unused databases and backups.",
            "Monitor query performance and optimize."
        ],
        "gcs": [
            "Enable GCS lifecycle management.",
            "Move cold data to Nearline/Coldline.",
            "Enable object versioning and clean up old versions.",
            "Compress data before upload.",
            "Monitor and delete unused buckets."
        ],
        "gae": [
            "Scale down unused App Engine services.",
            "Enable App Engine autoscaling.",
            "Move workloads to lower pricing tiers.",
            "Monitor and optimize app service usage.",
            "Delete unused services and versions."
        ],
        "bigquery": [
            "Partition BigQuery tables for cost savings.",
            "Delete unused datasets.",
            "Enable table expiration policies.",
            "Monitor and optimize query costs.",
            "Use flat-rate pricing for predictable workloads."
        ],
        "cloudfunctions": [
            "Optimize Cloud Functions memory allocation.",
            "Remove unused functions.",
            "Monitor invocation frequency and duration.",
            "Consolidate functions where possible."
        ],
        "pubsub": [
            "Delete unused Pub/Sub topics.",
            "Optimize Pub/Sub message retention.",
            "Monitor and consolidate topics."
        ],
        "datastore": [
            "Delete unused Datastore entities.",
            "Optimize Datastore indexes.",
            "Monitor and consolidate namespaces."
        ],
        "memorystore": [
            "Resize Memorystore instances.",
            "Delete unused Memorystore resources.",
            "Monitor and optimize cache usage."
        ],
        "composer": [
            "Pause unused Composer environments.",
            "Optimize Composer DAG schedules.",
            "Monitor and clean up old environments."
        ],
        "dataproc": [
            "Delete unused Dataproc clusters.",
            "Resize Dataproc clusters for cost savings.",
            "Monitor and optimize job scheduling.",
            "Use preemptible VMs for batch workloads."
        ],
        "spanner": [
            "Delete unused Spanner instances.",
            "Optimize Spanner node count.",
            "Monitor and consolidate databases."
        ],
        "tasks": [
            "Delete unused Cloud Tasks queues.",
            "Optimize Cloud Tasks execution policies.",
            "Monitor and consolidate queues."
        ],
    }
    return recommendations.get(service, [])

def get_specific_recommendation(service, index):
    recs = get_recommendation(service)
    if 0 <= index < len(recs):
        return recs[index]
    return None

def save_to_csv(service, recommendation, filename="recommendation.csv"):
    with open(filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["service", "recommendation"])
        writer.writerow([service, recommendation])