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
  id = var.VPC_ID
}


# Create SG
resource "aws_security_group" "RDS-SG" {
  name   = var.sg_name
  vpc_id = data.aws_vpc.c16_vpc.id

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

# Create subnet group to specify VPC and subnets
resource "aws_db_subnet_group" "c16-public-subnets" {
  name       = var.subnet_group_name
  subnet_ids = [var.SUBNET_ID_1, var.SUBNET_ID_2]

  tags = {
    Name = var.subnet_group_name
  }
}


# Create RDS
resource "aws_db_instance" "RDS-media-polarisation" {
  identifier = var.RDS_IDENTIFIER
  allocated_storage    = 30
  db_name              = var.DB_NAME
  engine               = "postgres"
  engine_version       = "17.2"
  instance_class       = "db.t3.micro"
  username             = var.DB_USERNAME
  password             = var.DB_PASSWORD
  vpc_security_group_ids = [resource.aws_security_group.RDS-SG.id]
  db_subnet_group_name = resource.aws_db_subnet_group.c16-public-subnets.name
  publicly_accessible = true
  skip_final_snapshot  = true
}