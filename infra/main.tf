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
  # Cloud Shell環境では自動登録がスムーズなので、この行はなくてもOKですが念のため
}

# 1. 共通のApp Service Plan (無料 F1 プラン)
resource "azurerm_service_plan" "free_plan" {
  name                = "plan-gemini-free"
  location            = "Korea Central"
  resource_group_name = "rg-my-ai-app" # ★ここを書き換えてください
  os_type             = "Linux"
  sku_name            = "F1"
}

# 2. 開発(dev), 検証(stg), 本番(prod) の3つのアプリを一気に作成
resource "azurerm_linux_web_app" "apps" {
  for_each            = toset(["dev", "stg", "prod"])
  
  # アプリ名は世界で重複不可なので、末尾にランダムな英数字や自分の名前を足すと確実です
  name                = "app-gemini-${each.key}-shotaro" 
  location            = "Korea Central"
  resource_group_name = "rg-my-ai-app" # ★ここを書き換えてください
  service_plan_id     = azurerm_service_plan.free_plan.id

  site_config {
    always_on = false
    application_stack {
      python_version = "3.11"
    }
  }
}