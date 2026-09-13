resource "aws_db_subnet_group" "rds_subnet_group" {
  name        = "calorie-tracker-rds-subnet-group"
  subnet_ids  = [aws_subnet.subnet1.id, aws_subnet.subnet2.id]

  tags = {
    Name = "RDS Subnet Group"
  }
}

resource "aws_db_instance" "postgres" {
  identifier             = "calorie-tracker-db"
  engine                 = "postgres"
  engine_version         = "18.6"
  instance_class         = "db.t4g.micro"
  allocated_storage      = 20
  max_allocated_storage  = 50

  db_name                = "calorie_tracker"
  username               = "db_admin"
  password               = var.db_password

  db_subnet_group_name   = aws_db_subnet_group.rds_subnet_group.name
  vpc_security_group_ids = [aws_security_group.ecs_security_group.id]

  skip_final_snapshot    = true
  publicly_accessible    = false
}

output "rds_endpoint" {
  value = aws_db_instance.postgres.endpoint
}
