resource "aws_lb_target_group" "frontend_target_group" {
  name        = "calorie-tracker-frontend-tg"
  port        = "5173"
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = aws_vpc.vpc.id

  tags = {
    Name = "target_group"
  }
}

resource "aws_lb_target_group" "backend_target_group" {
  name        = "calorie-tracker-backend-tg"
  port        = "8000"
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = aws_vpc.vpc.id

  health_check {
    path                = "/docs"
    matcher             = "200"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 3
  }

  tags = {
    Name = "target_group"
  }
}
