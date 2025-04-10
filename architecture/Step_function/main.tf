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

# Archive lambda data
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
    # This might be the problem. You need to attach this invoke to lambda and the SES to seomthing else
      actions = [
        "lambda:InvokeFunction",
        "ses:SendEmail"
      ]

      resources = [
        data.aws_lambda_function.email_lambda.qualified_arn,
        
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
        "FunctionName": "arn:aws:lambda:eu-west-2:129033205317:function:c16-media-polarisation-email-lambda:$LATEST",
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
            "trainee.antariksh.patel@sigmalabs.co.uk",
            "trainee.joseph.sasaki@sigmalabs.co.uk",
            "trainee.josh.allen@sigmalabs.co.uk",
            "trainee.jake.hussey@sigmalabs.co.uk"
          ]
        },
        "FromEmailAddress": "trainee.antariksh.patel@sigmalabs.co.uk"
      }
    }
  },
  "QueryLanguage": "JSONata"
}
EOF
}