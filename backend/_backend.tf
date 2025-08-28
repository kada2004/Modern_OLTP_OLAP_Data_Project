terraform {
  backend "azurerm" {
    resource_group_name  = "data_platform"
    storage_account_name = "datastorage7i4ws2"
    container_name       = "terraform-state"
    key                  = "terraform.tfstate"
  }
}