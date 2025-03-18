
# Secret Manager
resource "google_secret_manager_secret" "secret_manager_private_key" {
  secret_id = "secret-manager-certificate-key"
  project   = var.project_id
  replication {
    user_managed {
      replicas {
        location = "us-east1"
        customer_managed_encryption {
          kms_key_name = google_kms_crypto_key.secret_manager_key_east1.id
        }
      }
      replicas{
        location = "us-central1"
        customer_managed_encryption {
          kms_key_name = google_kms_crypto_key.secret_manager_key_central1.id
        }
      }
    }
  }
}
