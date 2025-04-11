variable "region" {
    description = "Region the AWS services are hosted on"
    type = string
    default = "eu-west-2"
}

variable "ecr_name_scraper" {
    description = "ECR name for scraper pipeline"
    type = string
    default = "c16-media-polarisation-scraper-ecr"
}

variable "ecr_name_scraper_dispatcher" {
    description = "ECR name for main scraper which provisions workers"
    type = string
    default = "c16-media-polarisation-dispatcher-scraper-ecr"
}

variable "ecr_name_email" {
    description = "ECR name for email pipeline"
    type = string
    default = "c16-media-polarisation-email-ecr"
}

variable "ecr_name_archive" {
    description = "ECR name for archive pipeline"
    type = string
    default = "c16-media-polarisation-archive-ecr"
}

variable "ecr_name_dashboard" {
    description = "ECR name for dashboard pipeline"
    type = string
    default = "c16-media-polarisation-dashboard-ecr"
}