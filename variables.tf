variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "lambda_function_name" {
  description = "Name of the Lambda function"
  type        = string
  default     = "demo-lambda-function"
}

variable "lambda_role_name" {
  description = "Name of the Lambda execution role"
  type        = string
  default     = "demo-lambda-exec-role"
}