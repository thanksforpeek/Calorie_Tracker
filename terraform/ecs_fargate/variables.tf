variable "google_api_key" {
  type        = string
  description = "Google Gemini API Key"
  sensitive   = true
}

variable "db_password" {
  type        = string
  description = "Password for database"
  sensitive   = true
}