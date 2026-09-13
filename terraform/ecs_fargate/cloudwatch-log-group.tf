resource "aws_cloudwatch_log_group" "ecs_logs" {
  name              = "/aws/ecs/calorie-tracker-ecs"
  retention_in_days = 14

  tags = {
    Environment = "dev"
    Application = "CalorieTracker"
  }
}
