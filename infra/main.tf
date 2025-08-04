provider "aws" {}

# IAM Role for Lambda
resource "aws_iam_role" "lambda_exec" {
  name = "demo-lambda-exec-role-${terraform.workspace}"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

# Attach basic policies
resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "lambda_s3" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
}

# Custom Bedrock policy
resource "aws_iam_policy" "lambda_bedrock" {
  name        = "lambda-bedrock-policy-${terraform.workspace}"
  description = "Policy for Lambda to access Bedrock"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "bedrock:InvokeModel"
        ],
        Resource = "arn:aws:bedrock:us-east-1::foundation-model/*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_bedrock" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = aws_iam_policy.lambda_bedrock.arn
}

# Pull the hash text (base64-encoded SHA-256)
data "aws_s3_object" "zip_hash" {
  bucket = var.artifact_bucket
  key    = var.artifact_hash_key
}

# Data source for metadata/etag if desired
data "aws_s3_object" "zip" {
  bucket = var.artifact_bucket
  key    = var.artifact_key
}

# Prefer metadata; fall back to body if you also upload the text file.
locals {
  source_code_hash = try(
    trimspace(data.aws_s3_object.zip.metadata["sha256-b64"]),
    trimspace(data.aws_s3_object.zip_hash.body)
  )
}

resource "aws_lambda_function" "demo_lambda" {
  function_name = "${var.lambda_function_name}-${terraform.workspace}"
  role          = aws_iam_role.lambda_exec.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.11"
  timeout       = 120
  memory_size   = 512

  s3_bucket        = var.artifact_bucket
  s3_key           = var.artifact_key

  # Use the precomputed base64(SHA-256) from CI
  source_code_hash = local.source_code_hash

  # Helpful traceability in the function's environment
  environment {
    variables = {
      BUILD_VERSION   = var.artifact_version
      GIT_COMMIT_SHA  = var.git_commit_sha
      GIT_SHORT_SHA   = var.git_short_sha
      VERSION_NUMBER  = tostring(var.version_number)
    }
  }

  # Ensure replacement, not in-place update
  lifecycle {
    create_before_destroy = true
  }
}
