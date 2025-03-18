resource "aws_securityhub_insight" "ssm_managed_instance_count" {
  filters {
    type {
      comparison = "EQUALS"
      value      = "Software and Configuration Checks/Industry and Regulatory Standards/AWS-Foundational-Security-Best-Practices"
    }

    record_state {
      comparison = "EQUALS"
      value      = "ACTIVE"
    }

    workflow_status {
      comparison = "NOT_EQUALS"
      value      = "SUPPRESSED"
    }

    title {
      value      = "SSM.1"
      comparison = "PREFIX"
    }

    resource_type {
      value      = "AwsEc2Instance"
      comparison = "EQUALS"
    }
  }

  group_by_attribute = "SeverityLabel"

  name = "SSM-MANAGED-INSTANCE-COUNT"

}

resource "aws_securityhub_insight" "aws_foundational_security_best_practices" {
  filters {
    type {
      comparison = "EQUALS"
      value      = "Software and Configuration Checks/Industry and Regulatory Standards/AWS-Foundational-Security-Best-Practices"
    }

    record_state {
      comparison = "EQUALS"
      value      = "ACTIVE"
    }

    workflow_status {
      comparison = "NOT_EQUALS"
      value      = "SUPPRESSED"
    }

    compliance_status {
      comparison = "EQUALS"
      value      = "FAILED"
    }

  }

  group_by_attribute = "ComplianceStatus"

  name = "AWS-FOUNDATIONAL-SECURITY-BEST-PRACTICES"

}

resource "aws_securityhub_insight" "cis_foundational_security_best_practices" {

  filters {
    type {
      comparison = "EQUALS"
      value      = "Software and Configuration Checks/Industry and Regulatory Standards/CIS AWS Foundations Benchmark"
    }

    record_state {
      comparison = "EQUALS"
      value      = "ACTIVE"
    }

    workflow_status {
      comparison = "NOT_EQUALS"
      value      = "SUPPRESSED"
    }

    compliance_status {
      comparison = "EQUALS"
      value      = "FAILED"
    }

  }

  group_by_attribute = "ComplianceStatus"

  name = "CIS-FOUNDATIONAL-SECURITY-BEST-PRACTICES"

}

resource "aws_securityhub_insight" "amazon_guardDuty_findings" {
  filters {
    process_name {
      comparison = "EQUALS"
      value      = "GuardDuty"
    }

    workflow_status {
      comparison = "NOT_EQUALS"
      value      = "SUPPRESSED"
    }

    record_state {
      comparison = "EQUALS"
      value      = "ACTIVE"
    }

  }

  group_by_attribute = "ComplianceStatus"

  name = "AMAZON-GUARDDUTY-FINDINGS"

}

resource "aws_securityhub_insight" "iam_Access_Analyzer_findings" {
  filters {
    process_name {
      comparison = "EQUALS"
      value      = "IAM Access Analyzer"
    }

    workflow_status {
      comparison = "NOT_EQUALS"
      value      = "SUPPRESSED"
    }

    record_state {
      comparison = "EQUALS"
      value      = "ACTIVE"
    }

  }

  group_by_attribute = "ComplianceStatus"

  name = "IAM-ACCESS-ANALYSER-FINDINGS"

}

resource "aws_securityhub_insight" "unresolved_findings" {
  filters {
    workflow_status   {
      comparison = "NOT_EQUALS"
      value      = "SUPPRESSED"
    }
    workflow_status {
      value      = "RESOLVED"
      comparison = "NOT_EQUALS"
    }
    
  }

  group_by_attribute = "ComplianceStatus"

  name = "UNRESOLVED-FINDINGS"

}
