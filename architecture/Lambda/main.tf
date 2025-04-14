terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}



# Configure the AWS Provider
provider "aws" {
  region = var.region
}

### Policies and Roles
# Trust policy
data "aws_iam_policy_document" "trust-policy-doc" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}
# Create permission policy document for logging
data "aws_iam_policy_document" "permission-policy-doc" {
  statement {
    effect="Allow"

      actions = [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "ses:SendRawEmail",
        "ses:SendEmail"

      ]
      resources = [ "arn:aws:logs:eu-west-2:129033205317:*" ]
    }
    
}
# Create IAM with the trust policy
resource "aws_iam_role" "lambda_role" {
  name               = var.lambda_policy_name
  assume_role_policy = data.aws_iam_policy_document.trust-policy-doc.json
}

# Permissions policy
resource "aws_iam_policy" "lambda-role-permissions-policy" {
    name = var.lambda_permission_policy_name
    policy = data.aws_iam_policy_document.permission-policy-doc.json
}

# Attach permission policy
resource "aws_iam_role_policy_attachment" "lambda-role-policy-connection" {
  role = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda-role-permissions-policy.arn
}


### ECR
# Scraper worker pipeline ECR
data "aws_ecr_image" "scraper_pipeline_image" {
  repository_name = var.scraper_ecr_name
  image_tag = "latest"
}

# Scraper dispatcher pipeline ECR
data "aws_ecr_image" "scraper_dispatcher_pipeline_image" {
  repository_name = var.scraper_dispatcher_ecr_name
  image_tag = "latest"
}

# # email service ECR
data "aws_ecr_image" "email_service_image" {
  repository_name = var.email_ecr_name
  image_tag = "latest"
}

# # Archive pipeline ECR
data "aws_ecr_image" "archive_pipeline_image" {
  repository_name = var.archive_ecr_name
  image_tag = "latest"
}



resource "aws_lambda_function" "scraper_lambda" {
  image_uri = data.aws_ecr_image.scraper_pipeline_image.image_uri
  function_name = var.scraper_lambda_name
  role          = aws_iam_role.lambda_role.arn
  package_type = "Image"
  timeout = 900
  environment {
    variables = {
       DB_HOST = var.DB_HOST,
       DB_PORT = var.DB_PORT,
       DB_NAME = var.DB_NAME,
       DB_USERNAME = var.DB_USERNAME,
       DB_PASSWORD = var.DB_PASSWORD,
       OPENAI_API_KEY = var.OPENAI_API_KEY
    }
  }
}

resource "aws_lambda_function" "email_lambda" {
  image_uri = data.aws_ecr_image.email_service_image.image_uri
  function_name = var.email_lambda_name
  role          = aws_iam_role.lambda_role.arn
  package_type = "Image"
  timeout = 300
  memory_size = 1024
  environment {
    variables = {
       DB_HOST = var.DB_HOST,
       DB_PORT = var.DB_PORT,
       DB_NAME = var.DB_NAME,
       DB_USERNAME = var.DB_USERNAME,
       DB_PASSWORD = var.DB_PASSWORD,
       SECRET_ACCESS_KEY = var.SECRET_ACCESS_KEY
       ACCESS_KEY = var.ACCESS_KEY
    }
  }
}

resource "aws_lambda_function" "archive_lambda" {
  image_uri = data.aws_ecr_image.archive_pipeline_image.image_uri
  function_name = var.archive_lambda_name
  role          = aws_iam_role.lambda_role.arn
  package_type = "Image"
  timeout = 300
  environment {
    variables = {
       DB_HOST = var.DB_HOST,
       DB_PORT = var.DB_PORT,
       DB_NAME = var.DB_NAME,
       DB_USERNAME = var.DB_USERNAME,
       DB_PASSWORD = var.DB_PASSWORD,
       ACCESS_KEY = var.ACCESS_KEY,
       SECRET_ACCESS_KEY = var.SECRET_ACCESS_KEY,
       BUCKET_REGION = var.region,
       BUCKET_NAME = var.BUCKET_NAME
    }
  }
}

resource "aws_lambda_function" "scraper_dispatcher_lambda" {
  image_uri = data.aws_ecr_image.scraper_dispatcher_pipeline_image.image_uri
  function_name = var.scraper_dispatcher_lambda_name
  role          = aws_iam_role.lambda_role.arn
  package_type = "Image"
  timeout = 30
  environment {
    variables = {
       ACCESS_KEY = var.ACCESS_KEY,
       SECRET_ACCESS_KEY = var.SECRET_ACCESS_KEY,
       LAMBDA_REGION = var.region
       WORKER_FUNCTION_NAME = var.WORKER_FUNCTION_NAME
    }
  }
}