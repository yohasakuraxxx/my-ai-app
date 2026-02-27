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

# 0. Gemini APIキーを受け取るための変数定義
variable "google_api_key" {
  description = "Gemini API Key for the application"
  type        = string
  sensitive   = true # これを付けると、実行ログにキーが表示されなくなります
}

# 1. 共通のApp Service Plan (無料 F1 プラン)
resource "azurerm_service_plan" "free_plan" {
  name                = "plan-gemini-free"
  location            = "Korea Central"
  resource_group_name = "rg-my-ai-app"
  os_type             = "Linux"
  sku_name            = "F1"
}

# 2. 開発(dev), 検証(stg), 本番(prod) の3つのアプリを一気に作成
resource "azurerm_linux_web_app" "apps" {
  for_each            = toset(["dev", "stg", "prod"])
  
  name                = "app-gemini-${each.key}-shotaro" 
  location            = "Korea Central"
  resource_group_name = "rg-my-ai-app"
  service_plan_id     = azurerm_service_plan.free_plan.id

  site_config {
    always_on = false
    
    
    # ★ スタートアップコマンドを追記
    app_command_line = "gunicorn -w 4 -k uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000 app.main:app"

    application_stack {
      python_version = "3.11"
    }
  }

  # ★ 環境変数を追記
  app_settings = {
    "GOOGLE_API_KEY"                 = var.google_api_key
    "SCM_DO_BUILD_DURING_DEPLOYMENT" = "true" # Azure側でライブラリをインストールさせる
    "PYTHON_ENABLE_GUNICORN_MULTIWORKERS" = "true"
  }
}