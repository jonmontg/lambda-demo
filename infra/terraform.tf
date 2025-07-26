terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.0"
    }
  }
  required_version = ">= 1.0.0"
  backend "s3" {
    workspace_key_prefix = "demo_lambda_function"
    use_lockfile = true
  }
}