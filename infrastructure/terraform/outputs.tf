output "resource_group_name" {
  value = azurerm_resource_group.pharmasignal.name
}

output "container_registry_login_server" {
  value = azurerm_container_registry.pharmasignal.login_server
}

output "container_registry_name" {
  value = azurerm_container_registry.pharmasignal.name
}

output "postgresql_server_name" {
  value = azurerm_postgresql_flexible_server.pharmasignal.name
}

output "postgresql_connection_string" {
  value     = "postgresql://${var.db_username}:${var.db_password}@${azurerm_postgresql_flexible_server.pharmasignal.fqdn}/pharmasignal"
  sensitive = true
}

output "key_vault_name" {
  value = azurerm_key_vault.pharmasignal.name
}

output "container_app_environment_id" {
  value = azurerm_container_app_environment.pharmasignal.id
}
