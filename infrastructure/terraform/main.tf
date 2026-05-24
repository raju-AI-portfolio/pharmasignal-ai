# PharmaSignal AI — Azure Infrastructure
# This file defines all Azure resources for the platform

terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

# ── RESOURCE GROUP ──────────────────────────────────────
resource "azurerm_resource_group" "pharmasignal" {
  name     = var.resource_group_name
  location = var.location

  tags = {
    project     = "pharmasignal-ai"
    environment = var.environment
  }
}

# ── LOG ANALYTICS WORKSPACE ─────────────────────────────
resource "azurerm_log_analytics_workspace" "pharmasignal" {
  name                = "${var.prefix}-logs"
  location            = azurerm_resource_group.pharmasignal.location
  resource_group_name = azurerm_resource_group.pharmasignal.name
  sku                 = "PerGB2018"
  retention_in_days   = 30

  tags = {
    project = "pharmasignal-ai"
  }
}

# ── AZURE CONTAINER REGISTRY ────────────────────────────
resource "azurerm_container_registry" "pharmasignal" {
  name                = "${var.prefix}registry"
  resource_group_name = azurerm_resource_group.pharmasignal.name
  location            = azurerm_resource_group.pharmasignal.location
  sku                 = "Basic"
  admin_enabled       = true

  tags = {
    project = "pharmasignal-ai"
  }
}

# ── CONTAINER APPS ENVIRONMENT ──────────────────────────
resource "azurerm_container_app_environment" "pharmasignal" {
  name                       = "${var.prefix}-env"
  location                   = azurerm_resource_group.pharmasignal.location
  resource_group_name        = azurerm_resource_group.pharmasignal.name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.pharmasignal.id

  tags = {
    project = "pharmasignal-ai"
  }
}

# ── POSTGRESQL FLEXIBLE SERVER ──────────────────────────
resource "azurerm_postgresql_flexible_server" "pharmasignal" {
  name                   = "${var.prefix}-db"
  resource_group_name    = azurerm_resource_group.pharmasignal.name
  location               = azurerm_resource_group.pharmasignal.location
  version                = "16"
  administrator_login    = var.db_username
  administrator_password = var.db_password
  storage_mb             = 32768
  sku_name               = "B_Standard_B1ms"
  backup_retention_days  = 7

  tags = {
    project = "pharmasignal-ai"
  }
}

resource "azurerm_postgresql_flexible_server_database" "pharmasignal" {
  name      = "pharmasignal"
  server_id = azurerm_postgresql_flexible_server.pharmasignal.id
  collation = "en_US.utf8"
  charset   = "utf8"
}

# ── KEY VAULT ────────────────────────────────────────────
data "azurerm_client_config" "current" {}

resource "azurerm_key_vault" "pharmasignal" {
  name                = "${var.prefix}-kv"
  location            = azurerm_resource_group.pharmasignal.location
  resource_group_name = azurerm_resource_group.pharmasignal.name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  sku_name            = "standard"

  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = data.azurerm_client_config.current.object_id

    secret_permissions = [
      "Get", "List", "Set", "Delete"
    ]
  }

  tags = {
    project = "pharmasignal-ai"
  }
}

# Store Azure OpenAI key in Key Vault
resource "azurerm_key_vault_secret" "openai_key" {
  name         = "azure-openai-key"
  value        = var.azure_openai_key
  key_vault_id = azurerm_key_vault.pharmasignal.id
}
