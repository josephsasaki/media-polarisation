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


variable "container_definition_name" {
    description = "Name of container definition, used in task definition."
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

variable "DASHBOARD_ECR_NAME" {
    description = "Name of ECR for that has image of dashboard"
    type = string
}

variable "ECS_CLUSTER_NAME" {
    description = "Name of ECS cluster"
    type = string
}

variable "SUBNET_ID_1" {
    description = "Id of first public subnet"
    type = string
}

variable "SUBNET_ID_2" {
    description = "Id of second public subnet"
    type = string
}

variable "VPC_ID" {
    description = "VPC ID for RDS and SG"
    type = string
}

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

variable "TASK_EXECUTION_ROLE_ARN" {
    description = "Task definition role to with corresponding trust policy, also contains all permissions needed to run the task"
    type = string
}