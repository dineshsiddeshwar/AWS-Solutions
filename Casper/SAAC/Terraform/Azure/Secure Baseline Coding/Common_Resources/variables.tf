variable "tags" {
  description = "Standard tags to be attached to the repo"
  default = {
    Department  = "EYGDSSEC"
    Environment = "Dev"
  }
}

variable "diag_object" {
  default = {
    log = []
    metric = [
      #["Category name",  "Diagnostics Enabled(true/false)", "Retention Enabled(true/false)", Retention_period]                 
      ["Transaction", true, true, 60],
    ]
  }
}


variable "logs" {
  default = ["StorageRead", "StorageWrite", "StorageDelete"]
}

variable "metrics" {
  default = ["Capacity","Transaction"]
}
