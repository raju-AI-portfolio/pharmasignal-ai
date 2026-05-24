variable "resource_group_name" {
  description = "Name of the Azure resource group"
  default     = "pharmasignal-rg"
}

variable "location" {
  description = "Azure region"
  default     = "swedencentral"
}

variable "prefix" {
  description = "Prefix for all resource names"
  default     = "pharmasignal"
}

variable "environment" {
  description = "Environment name"
  default     = "dev"
}

variable "db_username" {
  description = "PostgreSQL admin username"
  default     = "pharmaadmin"
}

variable "db_password" {
  description = "PostgreSQL admin password"
  sensitive   = true
}

variable "azure_openai_key" {
  description = "Azure OpenAI API key"
  sensitive   = true
}
