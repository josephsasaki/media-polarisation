# Variables with defaults
variable "region" {
    description = "Region the AWS services are hosted on"
    type = string
    default = "eu-west-2"
}

variable "sg_name" {
    description = "Security group name for RDS"
    type = string
    default = "c16-media-sentiment-rds-sg"
}


variable "subnet_group_name" {
    description = "Subnet group name"
    type = string
    default = "c16-media-sentiment-subnet-group"
}

# From Tfvars 

variable "db_name" {
    description = "Database name"
    type = string
}

variable "db_username" {
    description = "Database username"
    type=string
}

variable "db_password" {
    description = "Database password"
    type = string
}

variable "vpc_id" {
    description = "VPC ID for RDS and SG"
    type = string
}

variable "subnet_id_1" {
    description = "First subnet id"
    type = string
}

variable "subnet_id_2" {
    description = "Second subnet id"
    type = string
}

variable "rds_identifier" {
    description = "Identification name for RDS"
    type = string
}