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

# Create scraper worker ECR

resource "aws_ecr_repository" "scraper-ecr" {
  name                 = var.ecr_name_scraper
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

# Create dispatcher scraper ECR

resource "aws_ecr_repository" "dispatcher-scraper-ecr" {
  name                 = var.ecr_name_scraper_dispatcher
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}


# Create email ECR

resource "aws_ecr_repository" "email-ecr" {
  name                 = var.ecr_name_email
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

# Create archive ECR

resource "aws_ecr_repository" "archive-ecr" {
  name                 = var.ecr_name_archive
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

# Create dashboard ECR

resource "aws_ecr_repository" "dashboard-ecr" {
  name                 = var.ecr_name_dashboard
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}