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

variable "scraper_lambda_name" {
    description = "Name for scraper lambda"
    type = string
    default = "c16-media-polarisation-scraper-lambda"
}

variable "email_lambda_name" {
    description = "Name for email lambda"
    type = string
    default = "c16-media-polarisation-email-lambda"
}

variable "archive_lambda_name" {
    description = "Name for archive lambda"
    type = string
    default = "c16-media-polarisation-archive-lambda"
}

# from tfvars

variable "scraper_ecr_name" {
    description = "ECR name containing scraper image"
    type = string
}

variable "email_ecr_name" {
    description = "ECR name containing email image"
    type = string
}

variable "archive_ecr_name" {
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