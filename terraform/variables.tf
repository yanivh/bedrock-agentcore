variable "aws_region" {
  description = "The AWS region to deploy resources in."
  type        = string
  default     = "us-east-1"
}

variable "account_id" {
  description = "AWS Account ID"
  type        = string
  default     = "301581146302" # <-- your actual account ID as a string
}

variable "agent_name" {
  description = "Agent name"
  type        = string
  default     = "agentcore_babbel_data_team" # <-- your actual agent name
}

variable "test_user_email" {
  description = "Email for test user in Cognito"
  type        = string
  default     = "test@example.com"
}

variable "test_user_temp_password" {
  description = "Temporary password for test user"
  type        = string
  default     = "TempPass123!"
  sensitive   = true
}

variable "test_user_password" {
  description = "Permanent password for test user"
  type        = string
  default     = "SecurePass123!"
  sensitive   = true
} 