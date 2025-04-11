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


# Roles and Policies for archive and scraper lambda
data "aws_iam_policy_document" "trust-policy-doc" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["scheduler.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

data "aws_iam_policy_document" "permission-policy-doc" {
  statement {
    effect="Allow"

      actions = ["lambda:InvokeFunction"]
      resources = [
        data.aws_lambda_function.scraper_dispatcher_lambda.arn,
        data.aws_lambda_function.archive_lambda.arn
      ]
    }
}

resource "aws_iam_role" "schedule_role" {
  name               = var.lambda_schedule_policy_name
  assume_role_policy = data.aws_iam_policy_document.trust-policy-doc.json
}

# Permissions policy
resource "aws_iam_policy" "schedule-role-permissions-policy" {
    name = var.lambda_schedule_permission_policy_name
    policy = data.aws_iam_policy_document.permission-policy-doc.json
}

# Attach permission policy
resource "aws_iam_role_policy_attachment" "lambda-role-policy-connection" {
  role = aws_iam_role.schedule_role.name
  policy_arn = aws_iam_policy.schedule-role-permissions-policy.arn
}


# Event scheduler scraper lambda
data "aws_lambda_function" "scraper_dispatcher_lambda" {
  function_name = var.lambda_scraper_dispatcher_name
}

resource "aws_scheduler_schedule" "scraper_lambda_schedule" {
  name       = var.lambda_scraper_dispatcher_name
  group_name = "default"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression_timezone = "Europe/London"
  schedule_expression = "cron(15 * * * ? *)"

  target {
    arn      = data.aws_lambda_function.scraper_dispatcher_lambda.arn
    role_arn = aws_iam_role.schedule_role.arn
  }
}

# Event scheduler archive lambda
data "aws_lambda_function" "archive_lambda" {
  function_name = var.lambda_archive_name
}

resource "aws_scheduler_schedule" "archive_lambda_schedule" {
  name       = var.lambda_archive_name
  group_name = "default"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression_timezone = "Europe/London"
  schedule_expression = "cron(0 9 * * ? *)"

  target {
    arn      = data.aws_lambda_function.archive_lambda.arn
    role_arn = aws_iam_role.schedule_role.arn
  }
}

## Event schedule for step function emailing
# The step function
data "aws_sfn_state_machine" "step-function-email" {
  name = var.step_function_name
}

data "aws_iam_policy_document" "permission-policy-doc-step-function" {
  statement {
    effect="Allow"

      actions = ["states:StartExecution"]
      resources = [
        data.aws_sfn_state_machine.step-function-email.arn
      ]
    }
}

resource "aws_iam_role" "schedule-role-step-function" {
  name               = var.step_function_schedule
  assume_role_policy = data.aws_iam_policy_document.trust-policy-doc.json
}

# Permissions policy
resource "aws_iam_policy" "schedule-role-permissions-policy-step-function" {
  name = var.step_function_schedule_permission_policy_name
  policy = data.aws_iam_policy_document.permission-policy-doc-step-function.json
}

# Attach permission policy
resource "aws_iam_role_policy_attachment" "step-function-role-policy-connection" {
  role = aws_iam_role.schedule-role-step-function.name
  policy_arn = aws_iam_policy.schedule-role-permissions-policy-step-function.arn
}

resource "aws_scheduler_schedule" "step-function-email-schedule" {
  name       = var.step_function_name
  group_name = "default"

  flexible_time_window {
    mode = "OFF"
  }
  schedule_expression_timezone = "Europe/London"
  schedule_expression = "cron(0 9 * * ? *)"

  target {
    arn      = data.aws_sfn_state_machine.step-function-email.arn
    role_arn = aws_iam_role.schedule-role-step-function.arn
  }
}
