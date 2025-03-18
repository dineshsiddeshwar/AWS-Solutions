

terraform {
	required_providers {
		aws = {
			source = "hashicorp/aws"
            version = ">=4.21.0"
		}
	}

	backend "remote" { }
}
