# **ECR (Elastic Container Repository) - Terraform Configuration**

This directory contains Terraform scripts to create five ECRs for each of the following: Dispatcher Lambda, Worker (scraper) Lambda, Archive Lambda, Email Lambda and the Dashboard.

- `main.tf`: The main Terraform script to define and create the Lambda functions and their associated roles.
- `variables.tf`: A file that defines the variables used in the Terraform configuration.

## **Variables**

The `variables.tf` file defines several variables used for configuring the ECR instances. Some of these variables have default values, but there are others that must be defined in the `terraform.tfvars` file for Terraform to successfully run. Only variables without default values are **essential** and must be included in the `terraform.tfvars` file.

Below is a list of all the variables in `variables.tf`:

#### **12. region**
- **Description**: The AWS region where the RDS will be deployed.
- **Type**: `string`
- **Optional**: Default = `"eu-west-2"`

#### **12. ecr_name_scraper**
- **Description**: ECR name which contains the worker (scraper) Lambda image.
- **Type**: `string`
- **Optional**: Default = `"c16-media-polarisation-scraper-ecr"`

#### **13. ecr_name_scraper_dispatcher**
- **Description**: ECR name of which contains the dispatcher Lambda image.
- **Type**: `string`
- **Optional**: Default = `"c16-media-polarisation-dispatcher-scraper-ecr"`

#### **14. ecr_name_email**
- **Description**: ECR name of which contains the Email Lambda image.
- **Type**: `string`
- **Optional**: Default = `"c16-media-polarisation-email-ecr"`

#### **15. ecr_name_archive**
- **Description**: ECR name of which contains the archive Lambda image.
- **Type**: `string`
- **Optional**: Default = `"c16-media-polarisation-archive-ecr"`

#### **16. ecr_name_dashboard**
- **Description**: ECR name of which contains the dashboard image.
- **Type**: `string`
- **Optional**: Default = `"c16-media-polarisation-dashboard-ecr"`

---

## **Steps to Run the Terraform Script**

1. **Initialize the Terraform working directory**:
   terraform init
   
2. **Apply the Terraform configuration**:
   terraform apply
   Provide confirmation i.e 'yes' when prompted with: Do you want to perform these actions?