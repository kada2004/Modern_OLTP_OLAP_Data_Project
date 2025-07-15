variable "terraform_sp_object_id" {
  description = "Object ID of the service principal used by Terraform"
  type        = string
  sensitive   = true
}

variable "synapse_sql_password" {
  description = "Password for Synapse SQL admin"
  type        = string
  sensitive   = true
}
