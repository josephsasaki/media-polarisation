# Variables with defaults
variable "region" {
    description = "Region the AWS services are hosted on"
    type = string
    default = "eu-west-2"
}

variable "lambda_policy_name" {
    description = "Policy name for lambda"
    type = string
    default = "c16-media-polarisation-policy-lambda"
}

variable "lambda_permission_policy_name" {
    description = "Permission policy name for lambda"
    type = string
    default = "c16-media-polarisation-permissions-lambda"
}

# from tfvars

variable "SCRAPER_LAMBDA_NAME" {
    description = "Name for scraper lambda (worker)"
    type = string
}


variable "SCRAPER_DISPATCHER_LAMBDA_NAME" {
    description = "Name for scraper lambda"
    type = string
}

variable "EMAIL_LAMBDA_NAME" {
    description = "Name for email lambda"
    type = string
}

variable "ARCHIVE_LAMBDA_NAME" {
    description = "Name for archive lambda"
    type = string
}

variable "SCRAPER_ECR_NAME" {
    description = "ECR name containing scraper image"
    type = string
}

variable "EMAIL_ECR_NAME" {
    description = "ECR name containing email image"
    type = string
}

variable "ARCHIVE_ECR_NAME" {
    description = "ECR name containing archive image"
    type = string
}

variable "SCRAPER_DISPATCHER_ECR_NAME" {
    description = "ECR name containing archive image"
    type = string
}

# .env variables
variable "DB_HOST" {
    description = "Database Host"
    type = string
}

variable "DB_PORT" {
    description = "Database Port"
    type = string
}

variable "DB_NAME" {
    description = "Database Name"
    type = string
}

variable "DB_USERNAME" {
    description = "Database Username"
    type = string
}

variable "DB_PASSWORD" {
    description = "Database Password"
    type = string
}
variable "ACCESS_KEY" {
    description = "ACCESS KEY for IAM"
    type = string
}
variable "SECRET_ACCESS_KEY" {
    description = "SECRET ACCESS KEY for IAM"
    type = string
}

variable "BUCKET_NAME" {
    description = "Name of step function that is used to send emails"
    type = string
}

variable "OPENAI_API_KEY" {
    description = "OPENAI API Key"
    type = string
}