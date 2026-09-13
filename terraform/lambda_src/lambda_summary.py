import json
import os
import boto3
from datetime import datetime, timedelta

sns = boto3.client("sns", region_name=os.getenv("AWS_REGION", "eu-north-1"))
SNS_TOPIC_ARN = os.getenv("SNS_TOPIC_ARN")


def handler(event, context):
    try:
        if "Records" in event and len(event["Records"]) > 0:
            body_raw = event["Records"][0].get("body", {})
        else:
            body_raw = event.get("body", {})

        if isinstance(body_raw, str):
            body = json.loads(body_raw)
        elif isinstance(body_raw, dict):
            body = body_raw
        else:
            body = {}

        rows = body.get("rows", [])
        start_date_str = body.get("start_date")

        if not start_date_str:
            raise ValueError("Missing required parameter: 'start_date'")

        start = datetime.strptime(start_date_str, "%Y-%m-%d").date()

        logged_data = {
            str(row["log_date"]): round(float(row.get("total_calories", 0)))
            for row in rows
        }

        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        result = []

        for i in range(7):
            current_day = start + timedelta(days=i)
            day_str = str(current_day)
            result.append({
                "day": days[current_day.weekday()],
                "date": day_str,
                "calories": logged_data.get(day_str, 0)
            })

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "X-Processed-By": "AWS-Lambda-Summary"
            },
            "body": json.dumps(result, ensure_ascii=False)
        }

    except Exception as e:
        error_message = f"Calorie Tracker Lambda Error!\n\nError details: {str(e)}\n\nIncoming event:\n{json.dumps(event, indent=2)}"

        try:
            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject="Alert: Calorie Tracker Lambda Failure",
                Message=error_message
            )
        except Exception as sns_err:
            print(f"Failed to send SNS alert: {str(sns_err)}")

        raise e