# **RDS Directory - Terraform Configuration**

This directory contains Terraform scripts to create and configure an AWS RDS instance with a Postgres SQL engine. It includes:

- `main.tf`: The main Terraform script to define and create the RDS instance.
- `variables.tf`: A file that defines the variables used in the Terraform configuration.

## **Variables**

The `variables.tf` file defines several variables used for configuring the AWS RDS instance. Some of these variables have default values, but there are others that must be defined in the `terraform.tfvars` file for Terraform to successfully run. Only variables without default values are **essential** and must be included in the `terraform.tfvars` file.

Below is a list of all the variables in `variables.tf`:

#### **1. DB_NAME**
- **Description**: Name of database.
- **Type**: `string`
- **REQUIRED**

#### **2. DB_USERNAME**
- **Description**: Username used to log into the database.
- **Type**: `string`
- **REQUIRED**

#### **3. DB_PASSWORD**
- **Description**: Password used to log into the database.
- **Type**: `string`
- **REQUIRED**

#### **4. VPC_ID**
- **Description**: The VPC ID of VPC which contains the defined subnets and where the RDS is deployed.
- **Type**: `string`
- **REQUIRED**

#### **5. SUBNET_ID_1**
- **Description**: Subnet ID for first AWS subnet.
- **Type**: `string`
- **REQUIRED**

#### **6. SUBNET_ID_2**
- **Description**: Subnet ID for second AWS subnet.
- **Type**: `string`
- **REQUIRED**

#### **7. RDS_IDENTIFIER**
- **Description**: The RDS identification name.
- **Type**: `string`
- **REQUIRED**

#### **8. region**
- **Description**: The AWS region where the RDS will be deployed.
- **Type**: `string`
- **Optional**: Default = `"eu-west-2"`

#### **9. sg_name**
- **Description**: Name of security group used for the RDS.
- **Type**: `string`
- **Optional**: Default = `"c16-media-polarisation-rds-s"`

#### **10. subnet_group_name**
- **Description**: Name of subnet group to be created, this contains subnets which will host the RDS.
- **Type**: `string`
- **Optional**: Default = `"c16-media-polarisation-subnet-group"`

---

## **Required Configuration: terraform.tfvars**

The `terraform.tfvars` file is where you provide values for the variables that do not have a default. These are essential for the Terraform configuration to run successfully.

The `terraform.tfvars` should have these variables along with relevant values:

```
DB_USERNAME="..."
DB_PASSWORD="..."
DB_NAME="..."
VPC_ID="..."
SUBNET_ID_1="..."
SUBNET_ID_2="..."
RDS_IDENTIFIER="..."
```

## **Steps to Run the Terraform Script**

1. **Initialize the Terraform working directory**:
   terraform init
   
2. **Apply the Terraform configuration**:
   terraform apply
   Provide confirmation i.e 'yes' when prompted with: Do you want to perform these actions?
