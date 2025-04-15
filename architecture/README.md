### How to create the `terraform.tfvars` file:

1. **Create a new file** in the same directory as your Terraform scripts, named `terraform.tfvars` by running the command `touch terraform.tfvars`.
2. **Provide values for the required variables** (`DB_USERNAME`, `DB_PASSWORD`). You can also override other default values here if needed.

### Example `terraform.tfvars`:

DB_USERNAME = "my_db_username"
DB_PASSWORD = "my_db_password"
