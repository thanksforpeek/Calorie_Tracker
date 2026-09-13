resource "aws_ecs_task_definition" "frontend_task_definition" {
  family                   = "calorie-tracker-frontend-task-definition"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "1024"
  memory                   = "2048"
  execution_role_arn       = aws_iam_role.iam_role.arn

  container_definitions = jsonencode([
    {
      name      = "calorie-tracker-frontend"
      image     = "963348789430.dkr.ecr.eu-north-1.amazonaws.com/calorie-tracker-frontend:latest"
      essential = true
      portMappings = [
        {
          containerPort = 5173
          hostPort      = 5173
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/aws/ecs/calorie-tracker-ecs"
          "awslogs-region"        = "eu-north-1"
          "awslogs-stream-prefix" = "frontend"
        }
      }
    }
  ])
}

resource "aws_ecs_task_definition" "backend_task_definition" {
  family                   = "calorie-tracker-backend"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "1024"
  memory                   = "2048"
  execution_role_arn       = aws_iam_role.iam_role.arn
  task_role_arn            = aws_iam_role.iam_role.arn

  container_definitions = jsonencode([
    {
      name      = "calorie-tracker-backend"
      image     = "963348789430.dkr.ecr.eu-north-1.amazonaws.com/calorie-tracker-backend:latest"
      essential = true
      portMappings = [
        {
          containerPort = 8000
          hostPort      = 8000
        }
      ]
      environment = [
        { name = "GOOGLE_API_KEY", value = var.google_api_key },
        { name  = "DATABASE_URL", value = "postgresql://db_admin:${var.db_password}@${aws_db_instance.postgres.address}:5432/calorie_tracker"}
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/aws/ecs/calorie-tracker-ecs"
          "awslogs-region"        = "eu-north-1"
          "awslogs-stream-prefix" = "api"
        }
      }
    },
    {
      name      = "xray-daemon"
      image     = "public.ecr.aws/xray/aws-xray-daemon:latest"
      cpu       = 32
      memory    = 256
      essential = true
      portMappings = [
        {
          containerPort = 2000
          protocol      = "udp"
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/aws/ecs/calorie-tracker-ecs"
          "awslogs-region"        = "eu-north-1"
          "awslogs-stream-prefix" = "xray-daemon"
        }
      }
    }
  ])
}

