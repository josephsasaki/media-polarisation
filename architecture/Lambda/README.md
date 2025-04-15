# **Lambda Directory - Terraform Configuration**

This directory contains Terraform scripts to create and configure four Lambda functions which serve different purposes: 
- Dispatcher Lambda - dispatches Scraper Lambdas.
- Archive Lambda - archives six month old data from RDS into S3.
- Scraper Lambdas - scrapes RSS feed and uploads analysis to RDS.
- Email Lambda - emails a daily report to recipients.

The required roles along with trust and permission policies are also defined. The trust policy allows any Lambda to take on the role and the permission allow these lambdas to create and write to CloudWatch logs.

- `main.tf`: The main Terraform script to define and create the Lambda functions and their associated roles.
- `variables.tf`: A file that defines the variables used in the Terraform configuration.

## **Variables**

The `variables.tf` file defines several variables used for configuring the AWS Lambda functions. Some of these variables have default values, but there are others that must be defined in the `terraform.tfvars` file for Terraform to successfully run. Only variables without default values are **essential** and must be included in the `terraform.tfvars` file.

Below is a list of all the variables in `variables.tf`:

#### **1. SCRAPER_ECR_NAME**
- **Description**: Name of ECR which hosts the Scraper Lambda (worker).
- **Type**: `string`
- **REQUIRED**

#### **2. EMAIL_ECR_NAME**
- **Description**: Name of ECR which hosts the Email Lambda image.
- **Type**: `string`
- **REQUIRED**

#### **3. ARCHIVE_ECR_NAME**
- **Description**: Name of ECR which hosts the Archive Lambda image.
- **Type**: `string`
- **REQUIRED**

#### **4. SCRAPER_DISPATCHER_ECR_NAME**
- **Description**: Name of ECR which hosts the Scraper Dispatcher Lambda image.
- **Type**: `string`
- **REQUIRED**

#### **5. DB_HOST**
- **Description**: RDS host URL.
- **Type**: `string`
- **REQUIRED**

#### **6. DB_PORT**
- **Description**: RDS port.
- **Type**: `string`
- **REQUIRED**

#### **7. DB_NAME**
- **Description**: Name of the database.
- **Type**: `string`
- **REQUIRED**

#### **8. DB_USERNAME**
- **Description**: Username credential to log into database.
- **Type**: `string`
- **REQUIRED**

#### **9. DB_PASSWORD**
- **Description**: Password credential to log into database.
- **Type**: `string`
- **REQUIRED**

#### **10. ACCESS_KEY**
- **Description**: Access key of IAM user.
- **Type**: `string`
- **REQUIRED**

#### **11. SECRET_ACCESS_KEY**
- **Description**: Secret access key of IAM user.
- **Type**: `string`
- **REQUIRED**

#### **12. BUCKET_NAME**
- **Description**: Archive S3 bucket name.
- **Type**: `string`
- **REQUIRED**

#### **13. OPENAI_API_KEY**
- **Description**: OpenAI API key.
- **Type**: `string`
- **REQUIRED**

#### **14. SCRAPER_LAMBDA_NAME**
- **Description**: Name of scraper (worker) Lambda.
- **Type**: `string`
- **REQUIRED**

#### **15. SCRAPER_DISPATCHER_LAMBDA_NAME**
- **Description**: Name of dispatcher Lambda.
- **Type**: `string`
- **REQUIRED**

#### **16. EMAIL_LAMBDA_NAME**
- **Description**: Name of email Lambda.
- **Type**: `string`
- **REQUIRED**

#### **17. ARCHIVE_LAMBDA_NAME**
- **Description**: Name of archive Lambda.
- **Type**: `string`
- **REQUIRED**

#### **18. region**
- **Description**: The AWS region where the RDS will be deployed.
- **Type**: `string`
- **Optional**: Default = `"eu-west-2"`

#### **19. lambda_policy_name**
- **Description**: Name of created trust policy used for Lambdas.
- **Type**: `string`
- **Optional**: Default = `"c16-media-polarisation-policy-lambda"`

#### **20. lambda_permission_policy_name**
- **Description**: Name of created permission policy used for Lambdas.
- **Type**: `string`
- **Optional**: Default = `"c16-media-polarisation-permissions-lambda"`

---

## **Required Configuration: terraform.tfvars**

The `terraform.tfvars` file is where you provide values for the variables that do not have a default. These are essential for the Terraform configuration to run successfully.

The `terraform.tfvars` should have these variables along with relevant values:

```
SCRAPER_ECR_NAME="..."
EMAIL_ECR_NAME="..."
ARCHIVE_ECR_NAME="..."
SCRAPER_DISPATCHER_ECR_NAME="..."
DB_HOST="..."
DB_PORT="..."
DB_NAME="..."
DB_USERNAME="..."
DB_PASSWORD="..."
ACCESS_KEY = "..."
SECRET_ACCESS_KEY="..."
BUCKET_NAME="..."
OPENAI_API_KEY="..."
SCRAPER_LAMBDA_NAME="..."
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