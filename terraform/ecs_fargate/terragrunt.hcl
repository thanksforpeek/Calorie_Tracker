remote_state {
  backend = "s3"
  config = {
    bucket  = "calorie-tracker-state-bucket"
    key     = "ecs-fargate/terraform.tfstate"
    region  = "eu-north-1"
    encrypt = true
  }
}

generate "provider" {
  path      = "provider.tf"
  if_exists = "overwrite_terragrunt"
  contents  = <<EOF
provider "aws" {
  region = "eu-north-1"
}
EOF
}