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

# Email Lambda data source
data "aws_lambda_function" "email_lambda" {
  function_name = var.lambda_email_name
}

## Policies and roles

# Step function trust policy
data "aws_iam_policy_document" "step_function_trust_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["states.amazonaws.com"]
    }
  }
}
# Step function permission policies
data "aws_iam_policy_document" "step_function_permission-policy" {
  statement {
    effect="Allow"
      actions = [
        "lambda:InvokeFunction",
        "ses:SendEmail"
      ]

      resources = [
        "*"
      ]
    }
}

# Create role with trust policy
resource "aws_iam_role" "step-function-role" {
  name               = var.step_function_role_name
  assume_role_policy = data.aws_iam_policy_document.step_function_trust_policy.json
}

# Create permission policy
resource "aws_iam_policy" "step_function-role-permissions-policy" {
    name = var.step_function_permission_policy_name
    policy = data.aws_iam_policy_document.step_function_permission-policy.json
}

# Attach permission policy to trust policy role
resource "aws_iam_role_policy_attachment" "lambda-role-policy-connection" {
  role = aws_iam_role.step-function-role.name
  policy_arn = aws_iam_policy.step_function-role-permissions-policy.arn
}

## Create step function
resource "aws_sfn_state_machine" "state_machine_email" {
  name     = var.state_machine_name
  role_arn = aws_iam_role.step-function-role.arn

  definition = <<EOF
{
  "Comment": "A description of my state machine",
  "StartAt": "Lambda Invoke",
  "States": {
    "Lambda Invoke": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Output": "{% $states.result.Payload %}",
      "Arguments": {
        "FunctionName": "${data.aws_lambda_function.email_lambda.qualified_arn}",
        "Payload": "{% $states.input %}"
      },
      "Retry": [
        {
          "ErrorEquals": [
            "Lambda.ServiceException",
            "Lambda.AWSLambdaException",
            "Lambda.SdkClientException",
            "Lambda.TooManyRequestsException"
          ],
          "IntervalSeconds": 1,
          "MaxAttempts": 3,
          "BackoffRate": 2,
          "JitterStrategy": "FULL"
        }
      ],
      "Next": "SendEmail"
    },
    "SendEmail": {
      "Type": "Task",
      "Resource": "arn:aws:states:::aws-sdk:sesv2:sendEmail",
      "End": true,
      "Arguments": {
        "Content": {
          "Simple": {
            "Subject": {
              "Charset": "UTF-8",
              "Data": "Hello from SES"
            },
            "Body": {
              "Html": {
                "Charset": "UTF-8",
                "Data": "{% $states.input.body %}"
              }
            }
          }
        },
        "Destination": {
          "ToAddresses": [
            "${var.receiver_address_1}",
            "${var.receiver_address_2}",
            "${var.receiver_address_3}",
            "${var.receiver_address_4}"
          ]
        },
        "FromEmailAddress": "${var.sender_address}"
      }
    }
  },
  "QueryLanguage": "JSONata"
}
EOF
}