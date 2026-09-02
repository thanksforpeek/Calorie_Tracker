terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.2.0"

  backend "s3" {
    bucket         = "calorie-tracker-tf-state-2026"
    key            = "dev/terraform.tfstate"
    region         = "eu-north-1"
    use_lockfile   = true
    encrypt        = true
  }
}

provider "aws" {
  region = "eu-north-1"
}

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_security_group" "app_sg" {
  name        = "calorie-tracker-tf-sg"
  description = "Security Group for CalorieTracker app"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "app_server" {
  ami                   = data.aws_ami.ubuntu.id
  instance_type         = "t3.micro"
  key_name              = "template_key"

  vpc_security_group_ids = [aws_security_group.app_sg.id]

  user_data = <<-EOF
              #!/bin/bash
              apt-get update
              apt-get install -y ca-certificates curl gnupg
              install -m 0755 -d /etc/apt/keyrings
              curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
              chmod a+r /etc/apt/keyrings/docker.asc

              echo \
                "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
                $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
                tee /etc/apt/sources.list.d/docker.list > /dev/null

              apt-get update
              apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
              usermod -aG docker ubuntu
              EOF

  root_block_device {
    volume_size = 16
    volume_type = "gp3"
  }

  tags = {
    Name = "CalorieTracker-TF"
  }
}

resource "aws_iam_role" "iam_role" {
  name = "lambda_execution_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_cloudwatch_log_group" "cloudwatch_log_ai" {
  name = "/aws/lambda/calorie_tracker_ai_service"
  retention_in_days = 14

  tags = {
    Environment = "dev"
    Application = "CalorieTracker"
  }
}

resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.iam_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

data "archive_file" "ai_lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/lambda_build"
  output_path = "${path.module}/ai_lambda.zip"
}

resource "aws_s3_object" "lambda_zip" {
  bucket = "calorie-tracker-tf-state-2026"
  key    = "builds/ai_lambda.zip"
  source = data.archive_file.ai_lambda_zip.output_path
  etag   = filemd5(data.archive_file.ai_lambda_zip.output_path)
}

resource "aws_lambda_function" "ai_service" {
  function_name    = "calorie_tracker_ai_service"
  role             = aws_iam_role.iam_role.arn
  handler          = "ai_handler.handler"
  runtime          = "python3.11"
  timeout          = 30

  s3_bucket        = aws_s3_object.lambda_zip.bucket
  s3_key           = aws_s3_object.lambda_zip.key
  source_code_hash = data.archive_file.ai_lambda_zip.output_base64sha256

  depends_on = [
    aws_iam_role_policy_attachment.lambda_logs,
    aws_cloudwatch_log_group.cloudwatch_log_ai
  ]

  environment {
    variables = {
      GOOGLE_API_KEY = var.google_api_key
    }
  }
}

resource "aws_lambda_function_url" "ai_service_url" {
  function_name      = aws_lambda_function.ai_service.function_name
  authorization_type = "NONE"

  cors {
    allow_origins = ["*"]
    allow_methods = ["POST", "GET"]
  }
}

output "ai_service_url" {
  value       = aws_lambda_function_url.ai_service_url.function_url
  description = "Public HTTP URL to invoke AI Lambda"
}

resource "aws_cloudwatch_log_group" "cloudwatch_log_summary" {
  name              = "/aws/lambda/calorie-tracker-summary"
  retention_in_days = 14

  tags = {
    Environment = "dev"
    Application = "CalorieTracker"
  }
}

data "archive_file" "summary_lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/lambda_build_summary"
  output_path = "${path.module}/summary_handler.zip"
}


resource "aws_lambda_function" "summary_handler" {
  filename         = data.archive_file.summary_lambda_zip.output_path
  function_name    = "calorie-tracker-summary"
  role             = aws_iam_role.iam_role.arn
  handler          = "lambda_summary.handler"
  runtime          = "python3.11"
  source_code_hash = data.archive_file.summary_lambda_zip.output_base64sha256

  depends_on = [
    aws_iam_role_policy_attachment.lambda_logs,
    aws_cloudwatch_log_group.cloudwatch_log_summary
  ]
}

resource "aws_lambda_function_url" "summary_lambda_url" {
  function_name      = aws_lambda_function.summary_handler.function_name
  authorization_type = "NONE"

  cors {
    allow_origins = ["*"]
    allow_methods = ["POST", "GET"]
  }
}

output "summary_lambda_url" {
  value       = aws_lambda_function_url.summary_lambda_url.function_url
  description = "Function URL for Weekly Summary Lambda"
}

output "public_ip" {
  value       = aws_instance.app_server.public_ip
  description = "Public IP of the EC2 instance"
}