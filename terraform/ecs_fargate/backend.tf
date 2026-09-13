terraform {
  backend "s3" {
    bucket  = "calorie-tracker-state-bucket"
    region  = "eu-north-1"
    key     = "ecs-fargate/terraform.tfstate"
    encrypt = true
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "6.36.0"
    }
  }
  required_version = ">= 1.2.0"
}
