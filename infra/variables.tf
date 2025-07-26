variable "lambda_function_name" {
  description = "Name of the Lambda function"
  type        = string
  default     = "demo-lambda-function"
}

variable "artifact_bucket" {
  description = "Bucket for the lambda code"
  type        = string
}

variable "artifact_key" {
  description = "Key in artifact_bucket"
  type        = string
}

variable "artifact_hash_key" {
  description = "Same as artifact_key plus .sha256.b64"
  type        = string
}

variable "artifact_version" {
  description = "Unique artifact version. run-<version_number>-<short_sha>"
  type        = string
}

variable "git_commit_sha" {
  description = "Git commit SHA for traceability"
  type        = string
}

variable "git_short_sha" {
  description = "Short (7-char) git commit SHA"
  type        = string
}

variable "version_number" {
  description = "Incremented version number for rollbacks"
  type        = string
}
