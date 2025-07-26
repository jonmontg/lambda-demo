terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.0"
    }
  }
  required_version = ">= 1.0.0"
  backend "s3" {
    bucket        = "terraform-state-bucket-937"
    key           = "demo_lambda_function/${terraform.workspace}/terraform.tfstate"
    use_lockfile  = true
    encrypt       = true
  }
}