terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Configure the AWS Provider
provider "aws" {
  region = var.region
}

# VPC data
data "aws_vpc" "c16_vpc" {
  id = var.vpc_id
}

# Import ECR image
data "aws_ecr_image" "dashboard_image" {
  repository_name = var.dashboard_ecr_name
  image_tag       = "latest"
}

# Create Task Definition
resource "aws_ecs_task_definition" "dashboard-task-definition" {
  family = var.task_definition_name
  requires_compatibilities = ["FARGATE"]
  network_mode = "awsvpc"
  cpu                      = 1024
  memory                   = 2048
  execution_role_arn = var.task_execution_role_arn
  container_definitions = jsonencode([
    {
      name      = var.container_definition_name
      image     = data.aws_ecr_image.dashboard_image.image_uri
      cpu       = 1024
      memory    = 2048
      portMappings = [
        {
          containerPort = 8501
          hostPort      = 8501
        }
      ]
    }
  ])
}

# Create security group
resource "aws_security_group" "dashboard_sg" {
  name   = var.sg_name
  vpc_id = data.aws_vpc.c16_vpc.id

  ingress {
    from_port        = 8501
    to_port          = 8501
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
  }
  ## Check if we need!!!
  ingress {
    from_port        = 5432
    to_port          = 5432
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
  }
  
  egress {
    from_port        = 0
    to_port          = 65535
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
  }
  tags = {
    Name = var.sg_name
  }
}

# Create ECS Service
resource "aws_ecs_service" "dashboard_service" {
  name            = var.ecs_service_name
  cluster         = var.ecs_cluster_name
  task_definition = aws_ecs_task_definition.dashboard-task-definition.arn
  desired_count   = 1
  launch_type = "FARGATE"
  network_configuration {
    subnets = [var.subnet_id_1, var.subnet_id_2]
    security_groups = [aws_security_group.dashboard_sg.id]
    assign_public_ip = true
  }
}