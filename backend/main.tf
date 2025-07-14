
locals {
  resource_group_name  = "data_platform"
  location             = "West Europe"
  storage_account_name = "datastorage${random_string.suffix.result}"
  container_name       = "terraform-state"
  #filesystem_name      = "data-lake"
}

resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}

resource "azurerm_resource_group" "rg" {
  name     = local.resource_group_name
  location = local.location
}

resource "azurerm_storage_account" "stg_account" {
  name                     = local.storage_account_name
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "StorageV2"
  is_hns_enabled           = true
}

resource "azurerm_storage_container" "state_file" {
  name                  = local.container_name
  storage_account_name  = azurerm_storage_account.stg_account.name
  container_access_type = "private"
}

