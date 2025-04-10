variable "region" {
    description = "Region the AWS services are hosted on"
    type = string
    default = "eu-west-2"
}

variable "task_definition_name" {
    description = "Name of task definition"
    type = string
    default = "c16-media-polarisation-dashboard-task-definition"
}

variable "container_execution_role_arn" {
    description = "ARN for container execution role"
    type = string
    default = "arn:aws:iam::129033205317:role/aws-service-role/ecs.amazonaws.com/AWSServiceRoleForECS"
}

variable "container_definition_name" {
    description = "Name for container definition in task definition"
    type = string
    default = "c16-media-polarisation-container-definition"
}

variable "ecs_service_name" {
    description = "Name for container definition in task definition"
    type = string
    default = "c16-media-polarisation-dashboard-service"
}

variable "sg_name" {
    description = "Name for container definition in task definition"
    type = string
    default = "c16-media-polarisation-dashboard-sg"
}


# From tfvars

variable "dashboard_ecr_name" {
    description = "Name of ECR for that has image of dashboard"
    type = string
}

variable "ecs_cluster_name" {
    description = "Name of ECS cluster"
    type = string
}

variable "subnet_id_1" {
    description = "Id of first public subnet"
    type = string
}

variable "subnet_id_2" {
    description = "Id of second public subnet"
    type = string
}

variable "vpc_id" {
    description = "VPC ID for RDS and SG"
    type = string
}