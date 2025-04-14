variable "region" {
    description = "Region the AWS services are hosted on"
    type = string
    default = "eu-west-2"
}

variable "step_function_role_name" {
    description = "Role name used for step function which sends emails"
    type = string
    default = "c16-media-polarisation-step-function-role"
}

variable "step_function_permission_policy_name" {
    description = "Permission policy name for step function"
    type = string
    default = "c16-media-polarisation-step-function-permission-policies"
}


variable "state_machine_name" {
    description = "Name of state machine"
    type = string
    default = "c16-media-polarisation-step-function-email"
}

# tfvars input

variable "lambda_email_name" {
    description = "Name of lambda responsible for outputing email content"
    type = string
}

## Receiver email address'
variable "receiver_address_1" {
    description = "Receiver email address 1"
    type = string
}

variable "receiver_address_2" {
    description = "Receiver email address 2"
    type = string
}

variable "receiver_address_3" {
    description = "Receiver email address 3"
    type = string
}

variable "receiver_address_4" {
    description = "Receiver email address 4"
    type = string
}

## Sender email address
variable "sender_address" {
    description = "Sender email address"
    type = string
}