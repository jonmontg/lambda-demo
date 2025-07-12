# Lambda Demo with Bedrock and S3 Access

This project demonstrates a Lambda function with access to AWS Bedrock and S3 services, deployed using Terraform and GitHub Actions.

## Features

- AWS Lambda function with Python 3.11 runtime
- IAM role with permissions for:
  - AWS Lambda basic execution (CloudWatch logs)
  - S3 read-only access
  - Bedrock model invocation
- Automated deployment via GitHub Actions

## Prerequisites

1. AWS Account with appropriate permissions
2. GitHub repository with GitHub Actions enabled

## Setup Instructions

### 1. AWS Credentials Setup

Create an IAM user in your AWS account with the following permissions:
- `AdministratorAccess` (for Terraform deployment)
- Or create a custom policy with permissions for:
  - IAM (for creating roles and policies)
  - Lambda (for creating and updating functions)
  - S3 (for reading from S3)
  - Bedrock (for invoking models)

### 2. GitHub Secrets Configuration

Add the following secrets to your GitHub repository (Settings > Secrets and variables > Actions):

- `AWS_ACCESS_KEY_ID`: Your AWS access key ID
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret access key

### 3. Customization (Optional)

Create a `terraform.tfvars` file to customize the deployment:

```hcl
aws_region = "us-west-2"
lambda_function_name = "my-custom-lambda"
lambda_role_name = "my-custom-role"
```

### 4. Deployment

The infrastructure will be automatically deployed when you push to the `main` branch. The GitHub Actions workflow will:

1. Zip the Lambda function code
2. Configure AWS credentials
3. Initialize Terraform
4. Plan and apply the infrastructure changes

## Infrastructure Components

- **Lambda Function**: Python 3.11 runtime with 60-second timeout and 512MB memory
- **IAM Role**: Execution role with permissions for CloudWatch logs, S3 read access, and Bedrock model invocation
- **IAM Policies**: Custom policy for Bedrock access with the following permissions:
  - `bedrock:InvokeModel`
  - `bedrock:InvokeModelWithResponseStream`
  - `bedrock:ListFoundationModels`
  - `bedrock:GetFoundationModel`

## Local Development

To test locally:

1. Install Terraform
2. Configure AWS credentials (`aws configure`)
3. Run:
   ```bash
   terraform init
   terraform plan
   terraform apply
   ```

## Security Notes

- The Lambda function has read-only access to S3
- Bedrock permissions are scoped to model invocation only
- Consider implementing least-privilege access for production use
- Review and adjust IAM permissions based on your specific requirements

## Troubleshooting

- Ensure your AWS credentials have sufficient permissions
- Check that the AWS region supports Bedrock (not all regions have Bedrock available)
- Verify that your Lambda function code is compatible with the runtime