variable "aws_region" {
  description = "The AWS region to deploy resources in."
  type        = string
  default     = "us-east-1"
}

variable "account_id" {
  description = "AWS Account ID"
  type        = string
  default     = "301581146302"  # <-- your actual account ID as a string
}

variable "agent_name" {
  description = "Agent name"
  type        = string
  default     = "agentcore_babbel_data_team"  # <-- your actual agent name
} 