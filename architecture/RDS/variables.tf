# Variables with defaults
variable "region" {
    description = "Region the AWS services are hosted on"
    type = string
    default = "eu-west-2"
}

variable "sg_name" {
    description = "Security group name for RDS"
    type = string
    default = "c16-media-polarisation-rds-sg"
}


variable "subnet_group_name" {
    description = "Subnet group name"
    type = string
    default = "c16-media-polarisation-subnet-group"
}

# From Tfvars 

variable "DB_NAME" {
    description = "Database name"
    type = string
}

variable "DB_USERNAME" {
    description = "Database username"
    type=string
}

variable "DB_PASSWORD" {
    description = "Database password"
    type = string
}

variable "VPC_ID" {
    description = "VPC ID for RDS and SG"
    type = string
}

variable "SUBNET_ID_1" {
    description = "First subnet id"
    type = string
}

variable "SUBNET_ID_2" {
    description = "Second subnet id"
    type = string
}

variable "RDS_IDENTIFIER" {
    description = "Identification name for RDS"
    type = string
}