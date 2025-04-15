# **Scheduler - Terraform Configuration**

This directory contains Terraform scripts to create three EventBridge Schedules for the Dispatcher Lambda (every hour at 15 minutes past the hour), Archive Lambda (every day at 9 AM) and the Email Lambda (every day at 9 AM).

The required roles along with trust and permission policies are also defined. The trust policy allows any EventBridge Scheduler to take on the role and the permission run all the relevant Lambdas.

- `main.tf`: The main Terraform script to define and create the Lambda functions and their associated roles.
- `variables.tf`: A file that defines the variables used in the Terraform configuration.

## **Variables**

The `variables.tf` file defines several variables used for configuring the AWS RDS instance. Some of these variables have default values, but there are others that must be defined in the `terraform.tfvars` file for Terraform to successfully run. Only variables without default values are **essential** and must be included in the `terraform.tfvars` file.

Below is a list of all the variables in `variables.tf`:

#### **1. SCRAPER_DISPATCHER_LAMBDA_NAME**
- **Description**: Name of dispatcher Lambda.
- **Type**: `string`
- **REQUIRED**

#### **2. EMAIL_LAMBDA_NAME**
- **Description**: Name of email Lambda.
- **Type**: `string`
- **REQUIRED**

#### **3. ARCHIVE_LAMBDA_NAME**
- **Description**: Name of archive Lambda.
- **Type**: `string`
- **REQUIRED**

#### **4. region**
- **Description**: The AWS region where the RDS will be deployed.
- **Type**: `string`
- **Optional**: Default = `"eu-west-2"`

#### **5. lambda_scraper_dispatcher_schedule_name**
- **Description**: Name of schedule for Dispatcher Lambda in scraper pipeline.
- **Type**: `string`
- **Optional**: Default = `"cc16-media-polarisation-scraper-dispatcher-scheduler"`

#### **6. lambda_archive_schedule_name**
- **Description**: Name of schedule for Lambda in archive pipeline.
- **Type**: `string`
- **Optional**: Default = `"c16-media-polarisation-archive-scheduler"`

#### **7. lambda_email_schedule_name**
- **Description**: Name of schedule for Email Lambda in emailing service.
- **Type**: `string`
- **Optional**: Default = `"c16-media-polarisation-email-scheduler"`

#### **8. lambda_schedule_role_name**
- **Description**: Name of role for schedulers.
- **Type**: `string`
- **Optional**: Default = `"c16-media-polarisation-lambda-schedule-role"`

#### **9. lambda_schedule_permission_policy_name**
- **Description**: Name of permission policy for scheduler
- **Type**: `string`
- **Optional**: Default = `"c16-media-polarisation-lambda-schedule-permission-policy"`

#### **10. step_function_schedule_permission_policy_name**
- **Description**: Name of permission policy for step function
- **Type**: `string`
- **Optional**: Default = `"c16-media-polarisation-step-function-scheduler-permission"`

---

## **Required Configuration: terraform.tfvars**

The `terraform.tfvars` file is where you provide values for the variables that do not have a default. These are essential for the Terraform configuration to run successfully.

The `terraform.tfvars` should have these variables along with relevant values:

```
SCRAPER_DISPATCHER_LAMBDA_NAME="..."
EMAIL_LAMBDA_NAME="..."
ARCHIVE_LAMBDA_NAME="..."
```

## **Steps to Run the Terraform Script**

1. **Initialize the Terraform working directory**:
   terraform init
   
2. **Apply the Terraform configuration**:
   terraform apply
   Provide confirmation i.e 'yes' when prompted with: Do you want to perform these actions?