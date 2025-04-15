# **Elastic Container Service - Terraform Configuration**

This directory contains Terraform scripts to create and configure an ECS instance which will use FARGATE. To do this a task definition was first created and then used as an input into the ECS definition. A security group was also created and attached to the ECS to allow connections on only port **80**.

- `main.tf`: The main Terraform script to define and create the Lambda functions and their associated roles.
- `variables.tf`: A file that defines the variables used in the Terraform configuration.

## **Variables**

The `variables.tf` file defines several variables used for configuring the AWS RDS instance. Some of these variables have default values, but there are others that must be defined in the `terraform.tfvars` file for Terraform to successfully run. Only variables without default values are **essential** and must be included in the `terraform.tfvars` file.

Below is a list of all the variables in `variables.tf`:

#### **1. DASHBOARD_ECR_NAME**
- **Description**: Name of ECR which hosts the dashboard image.
- **Type**: `string`
- **REQUIRED**

#### **2. ECS_CLUSTER_NAME**
- **Description**: Name of ECR cluster where the service will be hosted.
- **Type**: `string`
- **REQUIRED**

#### **3. SUBNET_ID_1**
- **Description**: Subnet ID of first public subnet in VPC.
- **Type**: `string`
- **REQUIRED**

#### **4. SUBNET_ID_2**
- **Description**: Subnet ID of second public subnet in VPC.
- **Type**: `string`
- **REQUIRED**

#### **5. VPC_ID**
- **Description**: VPC ID where the ECS will be created.
- **Type**: `string`
- **REQUIRED**

#### **6. DB_HOST**
- **Description**: RDS host URL.
- **Type**: `string`
- **REQUIRED**

#### **7. DB_PORT**
- **Description**: RDS port.
- **Type**: `string`
- **REQUIRED**

#### **8. DB_NAME**
- **Description**: Name of the database.
- **Type**: `string`
- **REQUIRED**

#### **9. DB_USERNAME**
- **Description**: Username credential to log into database.
- **Type**: `string`
- **REQUIRED**

#### **10. DB_PASSWORD**
- **Description**: Password credential to log into database.
- **Type**: `string`
- **REQUIRED**

#### **11. TASK_EXECUTION_ROLE_ARN**
- **Description**: Task definition role to with corresponding trust policy, also contains all permissions needed to run the task.
- **Type**: `string`
- **REQUIRED**

#### **12. region**
- **Description**: The AWS region where the RDS will be deployed.
- **Type**: `string`
- **Optional**: Default = `"eu-west-2"`

#### **13. task_definition_name**
- **Description**: Name of task definition
- **Type**: `string`
- **Optional**: Default = `"c16-media-polarisation-dashboard-task-definition"`

#### **14. container_definition_name**
- **Description**: Name of container definition, used in task definition.
- **Type**: `string`
- **Optional**: Default = `"c16-media-polarisation-container-definition"`

#### **15. ecs_service_name**
- **Description**: Name of ECS service.
- **Type**: `string`
- **Optional**: Default = `"c16-media-polarisation-dashboard-service"`

#### **16. sg_name**
- **Description**: Name of security group used for ECS.
- **Type**: `string`
- **Optional**: Default = `"c16-media-polarisation-dashboard-sg"`

---

## **Required Configuration: terraform.tfvars**

The `terraform.tfvars` file is where you provide values for the variables that do not have a default. These are essential for the Terraform configuration to run successfully.

The `terraform.tfvars` should have these variables along with relevant values:

```
DASHBOARD_ECR_NAME="..."
ECS_CLUSTER_NAME="..."
SUBNET_ID_1="..."
SUBNET_ID_2="..."
VPC_ID="..."
DB_HOST="..."
DB_PORT="..."
DB_NAME="..."
DB_USERNAME="..."
DB_PASSWORD="..."
TASK_EXECUTION_ROLE_ARN="..."
```

## **Steps to Run the Terraform Script**

1. **Initialize the Terraform working directory**:
   terraform init
   
2. **Apply the Terraform configuration**:
   terraform apply
   Provide confirmation i.e 'yes' when prompted with: Do you want to perform these actions?