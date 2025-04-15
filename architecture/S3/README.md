# **S3 Directory - Terraform Configuration**

This directory contains Terraform scripts to create an S3 bucket on AWS which will be used to archive older data from the RDS.

- `main.tf`: The main Terraform script to define and create the S3 instance.
- `variables.tf`: A file that defines the variables used in the Terraform configuration.

## **Variables**

The `variables.tf` file defines several variables used for configuring the AWS RDS instance. Some of these variables have default values, but there are others that must be defined in the `terraform.tfvars` file for Terraform to successfully run. Only variables without default values are **essential** and must be included in the `terraform.tfvars` file.

Below is a list of all the variables in `variables.tf`:


#### **1. region**
- **Description**: Name of region the S3 bucket will be deployed to.
- **Type**: `string`
- **Optional**: Default = `"eu-west-2"`

#### **2. subnet_group_name**
- **Description**: Name of the archive S3 bucket.
- **Type**: `string`
- **Optional**: Default = `"c16-media-polarisation-s3"`

---

## **Steps to Run the Terraform Script**

1. **Initialize the Terraform working directory**:
   terraform init
   
2. **Apply the Terraform configuration**:
   terraform apply
   Provide confirmation i.e 'yes' when prompted with: Do you want to perform these actions?
