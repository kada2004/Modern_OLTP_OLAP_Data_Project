output "resource_group_name" {
  value       = azurerm_resource_group.rg.name
  description = "The name of the resource group"
}

output "storage_account_name" {
  value       = azurerm_storage_account.stg_account.name
  description = "The name of the storage account"
}

output "container_name" {
  value       = azurerm_storage_container.state_file.name
  description = "The name of the blob container"
}

output "synapse_workspace_name" {
  value       = azurerm_synapse_workspace.synapse.name
  description = "The name of the Synapse workspace"
}

output "data_factory_name" {
  value       = azurerm_data_factory.adf.name
  description = "The name of the Data Factory instance"
}
