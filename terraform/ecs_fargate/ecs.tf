resource "aws_ecs_cluster" "cluster" {
  name = "calorie-tracker-ecs-cluster"

  tags = {
    Name = "calorie-tracker-ecs-cluster"
  }
}

resource "aws_ecs_service" "frontend-service" {
  name             = "calorie-tracker-frontend-service"
  platform_version = "LATEST"
  launch_type      = "FARGATE"
  cluster          = aws_ecs_cluster.cluster.id
  task_definition  = aws_ecs_task_definition.frontend_task_definition.arn
  desired_count    = 1
  depends_on       = [aws_security_group.ecs_security_group, aws_iam_role_policy_attachment.policy_attachment, aws_cloudwatch_log_group.ecs_logs]

  load_balancer {
    target_group_arn = aws_lb_target_group.frontend_target_group.arn
    container_name   = "calorie-tracker-frontend"
    container_port   = 5173
  }

  network_configuration {
    assign_public_ip = true
    subnets          = [aws_subnet.subnet1.id, aws_subnet.subnet2.id]
    security_groups  = [aws_security_group.ecs_security_group.id]
  }
}

resource "aws_ecs_service" "backend-service" {
  name             = "calorie-tracker-backend-service"
  platform_version = "LATEST"
  launch_type      = "FARGATE"
  cluster          = aws_ecs_cluster.cluster.id
  task_definition  = aws_ecs_task_definition.backend_task_definition.arn
  desired_count    = 1
  depends_on       = [aws_security_group.ecs_security_group, aws_iam_role_policy_attachment.policy_attachment, aws_cloudwatch_log_group.ecs_logs]

  load_balancer {
    target_group_arn = aws_lb_target_group.backend_target_group.arn
    container_name   = "calorie-tracker-backend"
    container_port   = 8000
  }

  network_configuration {
    assign_public_ip = true
    subnets          = [aws_subnet.subnet1.id, aws_subnet.subnet2.id]
    security_groups  = [aws_security_group.ecs_security_group.id]
  }
}
