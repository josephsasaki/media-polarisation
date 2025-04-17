variable "region" {
    description = "Region the AWS services are hosted on"
    type = string
    default = "eu-west-2"
}

variable "lambda_scraper_dispatcher_schedule_name" {
    description = "Name of schedule for Dispatcher Lambda in scraper pipeline"
    type = string
    default = "c16-media-polarisation-scraper-dispatcher-scheduler"
}

variable "lambda_archive_schedule_name" {
    description = "Name of schedule for Lambda in archive pipeline"
    type = string
    default = "c16-media-polarisation-archive-scheduler"
}

variable "lambda_email_schedule_name" {
    description = "Name of schedule for Lambda in emailing service"
    type = string
    default = "c16-media-polarisation-email-scheduler"
}

variable "lambda_schedule_role_name" {
    description = "Name of role for scheduler"
    type = string
    default = "c16-media-polarisation-lambda-schedule-role"
}

variable "lambda_schedule_permission_policy_name" {
    description = "Name of permission policy for scheduler"
    type = string
    default = "c16-media-polarisation-lambda-schedule-permission-policy"
}


variable "step_function_schedule_permission_policy_name" {
    description = "Name of permission policy for step function"
    type = string
    default = "c16-media-polarisation-step-function-scheduler-permission"
}


# tf vars variables
variable "SCRAPER_DISPATCHER_LAMBDA_NAME" {
    description = "Name for scraper lambda"
    type = string
}

variable "ARCHIVE_LAMBDA_NAME" {
    description = "Name for archive lambda"
    type = string
}

variable "EMAIL_LAMBDA_NAME" {
    description = "Name for email lambda"
    type = string
}