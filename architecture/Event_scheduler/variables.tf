variable "region" {
    description = "Region the AWS services are hosted on"
    type = string
    default = "eu-west-2"
}

variable "lambda_scraper_schedule_name" {
    description = "Name of schedule for Lambda in scraper pipeline"
    type = string
    default = "c16-media-polarisation-scraper-scheduler"
}

variable "lambda_archive_schedule_name" {
    description = "Name of schedule for Lambda in archive pipeline"
    type = string
    default = "c16-media-polarisation-archive-scheduler"
}

variable "lambda_schedule_policy_name" {
    description = "Name of policy for scheduler"
    type = string
    default = "c16-media-polarisation-lambda-schedule-policy"
}

variable "lambda_schedule_permission_policy_name" {
    description = "Name of permission policy for scheduler"
    type = string
    default = "c16-media-polarisation-lambda-schedule-permission-policy"
}


# tf vars variables
variable "lambda_scraper_name" {
    description = "Name of lambda in scraper pipeline"
    type = string
}

variable "lambda_archive_name" {
    description = "Name of lambda in archive pipeline"
    type = string
}