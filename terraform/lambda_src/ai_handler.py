import json
import base64
import agent
from pydantic_ai import BinaryContent


def handler(event, context):
    try:
        body_raw = event.get("body", {})

        if isinstance(body_raw, str):
            try:
                body = json.loads(body_raw)
            except json.JSONDecodeError:
                body = {}
        elif isinstance(body_raw, dict):
            body = body_raw
        else:
            body = {}

        if not body and ("action" in event or "message" in event):
            body = event

        action = body.get("action", "foodanalyze")

        if action == "foodanalyze" or "message" in body:
            message = body.get("message") or body.get("prompt")
            if not message:
                return {
                    "statusCode": 400,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({"error": "Field 'message' or 'prompt' is required"})
                }

            res = agent.chat_agent.run_sync(message)

            output_data = res.output.model_dump() if hasattr(res.output, "model_dump") else str(res.output)
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(output_data, ensure_ascii=False)
            }

        elif action == "gapfiller":
            user_prompt = (
                f"I need to hit my remaining daily macro targets:\n"
                f"- Calories: {body.get('remaining_calories', 0)} kcal\n"
                f"- Protein: {body.get('remaining_protein', 0)} g\n"
                f"- Carbs: {body.get('remaining_carbs', 0)} g\n"
                f"- Fat: {body.get('remaining_fat', 0)} g\n\n"
                f"My dietary preferences and available ingredients: {body.get('user_preferences', 'None')}.\n"
                f"Please suggest 2-3 suitable meal options."
            )
            res = agent.gap_filler_agent.run_sync(user_prompt)
            output_data = res.output.model_dump() if hasattr(res.output, "model_dump") else str(res.output)
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(output_data, ensure_ascii=False)
            }

        elif action == "foodscan":
            image_b64 = body.get("image_b64")
            if not image_b64:
                return {
                    "statusCode": 400,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({"error": "Missing 'image_b64'"})
                }

            media_type = body.get("media_type", "image/jpeg")
            image_bytes = base64.b64decode(image_b64)

            res = agent.food_scan_agent.run_sync([
                "Analyze this meal and calculate macros strictly per 100g:",
                BinaryContent(data=image_bytes, media_type=media_type)
            ])
            output_data = res.output.model_dump() if hasattr(res.output, "model_dump") else str(res.output)
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(output_data, ensure_ascii=False)
            }

        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": f"Unknown action: {action}"})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e), "type": type(e).__name__})
        }