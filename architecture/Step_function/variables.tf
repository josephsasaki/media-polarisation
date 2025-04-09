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