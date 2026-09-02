import json
from datetime import datetime, timedelta

def handler(event, context):
    try:
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
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing 'start_date'"})
            }

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
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }