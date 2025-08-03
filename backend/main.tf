# https://developer.hashicorp.com/terraform/language/values/locals

locals {
  resource_group_name    = "data_platform"
  location               = "West Europe"
  storage_account_name   = "datastorage${random_string.suffix.result}"
  container_name         = "terraform-state"
  bronze_container_name  = "bronze"
  silver_container_name  = "silver"
  synapse_workspace_name = "synapse-data-platform-${random_string.suffix.result}"
  data_factory_name      = "adf-data-platform"
  key_vault_name         = "kv-data-platform-${random_string.suffix.result}"
  dedicated_pool         = "synape_sql_pool"
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

resource "azurerm_storage_container" "bronze" {
  name                  = local.bronze_container_name
  storage_account_name  = azurerm_storage_account.stg_account.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "silver" {
  name                  = local.silver_container_name
  storage_account_name  = azurerm_storage_account.stg_account.name
  container_access_type = "private"
}

# https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/key_vault

resource "azurerm_key_vault" "kv" {
  name                       = local.key_vault_name
  location                   = azurerm_resource_group.rg.location
  resource_group_name        = azurerm_resource_group.rg.name
  tenant_id                  = data.azurerm_subscription.current.tenant_id
  sku_name                   = "standard"
  purge_protection_enabled   = false
  soft_delete_retention_days = 7
}

#https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/key_vault_access_policy
resource "azurerm_key_vault_access_policy" "terraform" {
  key_vault_id = azurerm_key_vault.kv.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = data.azurerm_client_config.current.object_id

  secret_permissions = ["Get", "Set", "List"]
}

resource "azurerm_key_vault_secret" "storage_key" {
  name         = "storage-key"
  value        = azurerm_storage_account.stg_account.primary_access_key
  key_vault_id = azurerm_key_vault.kv.id
}

resource "azurerm_key_vault_access_policy" "adf_access" {
  key_vault_id       = azurerm_key_vault.kv.id
  tenant_id          = data.azurerm_subscription.current.tenant_id
  object_id          = azurerm_data_factory.adf.identity[0].principal_id
  secret_permissions = ["Get", "List"]
}

resource "azurerm_key_vault_secret" "synapse_password" {
  name         = "synapse-sql-password"
  value        = var.synapse_sql_password
  key_vault_id = azurerm_key_vault.kv.id
}

resource "azurerm_synapse_workspace" "synapse" {
  name                                 = local.synapse_workspace_name
  resource_group_name                  = azurerm_resource_group.rg.name
  location                             = "northeurope" # Only Synapse in northeurope free subscription is not allowed to create synapse in westeurope
  storage_data_lake_gen2_filesystem_id = "https://${azurerm_storage_account.stg_account.name}.dfs.core.windows.net/${azurerm_storage_container.bronze.name}"
  sql_administrator_login              = "sqladminuser"
  sql_administrator_login_password     = var.synapse_sql_password

  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_synapse_firewall_rule" "allow_all" {
  name                 = "AllowAll"
  synapse_workspace_id = azurerm_synapse_workspace.synapse.id
  start_ip_address     = "0.0.0.0"
  end_ip_address       = "255.255.255.255"
}

resource "azurerm_synapse_spark_pool" "spark_pool" {
  name                 = "sparkpool01"
  synapse_workspace_id = azurerm_synapse_workspace.synapse.id
  node_size_family     = "MemoryOptimized"
  node_size            = "Small"
  #node_count             = 3
  spark_version = "3.3"


  auto_pause {
    delay_in_minutes = 10
  }
  auto_scale {
    min_node_count = 3
    max_node_count = 3
  }
}

# Adding dedicated sql pool to synapse
resource "azurerm_synapse_sql_pool" "dedicated_pool" {
  name                 = local.dedicated_pool
  synapse_workspace_id = azurerm_synapse_workspace.synapse.id
  sku_name             = "DW100c"
  create_mode          = "Default"
  storage_account_type = "LRS"
  lifecycle {
  ignore_changes = [
  storage_account_type      
    ]
  }
}

resource "azurerm_data_factory" "adf" {
  name                = local.data_factory_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  identity {
    type = "SystemAssigned"
  }
}


