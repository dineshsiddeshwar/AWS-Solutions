import random
import csv

def get_recommendation(service):
    recommendations = {
        "ec2": [
            "Terminate unused EC2 instances to save costs.",
            "Use spot instances for non-critical workloads."
        ],
        "vm": [
            "Resize Azure VMs to optimize spending.",
            "Deallocate unused VMs."
        ],
        "rds": [
            "Switch to reserved RDS instances for savings.",
            "Enable RDS storage auto-scaling."
        ]
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
