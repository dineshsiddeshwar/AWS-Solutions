##
## Secret Manager Secrets 
##

## Example Certificate Private Key Secret
resource "google_secret_manager_secret" "example_cert_private_key" {
  secret_id = "example-cert-secret"
  project   = var.project_id
  replication {
    user_managed {
      replicas {
        location = "us-east1"
        customer_managed_encryption {
          kms_key_name = google_kms_crypto_key.secret_manager_key_east1.id
        }
      }
    }
  }
}

