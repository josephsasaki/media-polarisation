variable "region" {
    description = "Region the AWS services are hosted on"
    type = string
    default = "eu-west-2"
}

variable "s3_bucket_name" {
    description = "Name of S3 bucket for archiving"
    type = string
    default = "c16-media-polarisation-s3"
}