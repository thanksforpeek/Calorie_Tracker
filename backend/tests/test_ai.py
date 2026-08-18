from io import BytesIO
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi import status
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@patch("routers.ai.agent.chat_agent.run", new_callable=AsyncMock)
def test_analyze_described_food_success(mock_agent_run):
    mock_response = MagicMock()
    mock_response.output = {"response": "Parsed: 100g Chicken Breast (165 kcal)"}
    mock_agent_run.return_value = mock_response

    payload = {"message": "I ate 100g of chicken breast"}
    response = client.post("/api/ai/foodanalyze", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"response": "Parsed: 100g Chicken Breast (165 kcal)"}
    mock_agent_run.assert_called_once_with("I ate 100g of chicken breast")

@patch("routers.ai.agent.chat_agent.run", new_callable=AsyncMock)
def test_analyze_described_food_ai_error(mock_agent_run):
    mock_agent_run.side_effect = Exception("AI Provider Error")

    payload = {"message": "I ate an apple"}
    response = client.post("/api/ai/foodanalyze", json=payload)

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json()["detail"] == "AI Provider Error"

@patch("routers.ai.agent.gap_filler_agent.run", new_callable=AsyncMock)
def test_get_daily_gap_filler_success(mock_agent_run):
    mock_response = MagicMock()
    mock_response.output = {
        "summary": "Here are a few high-protein options to hit your remaining targets:",
        "options": [
            {
                "title": "Protein Oatmeal",
                "description": "Mix oats with whey protein and water/milk.",
                "ingredients": [
                    {"name": "Oats", "weight_g": 60.0},
                    {"name": "Whey Protein Powder", "weight_g": 30.0}
                ],
                "estimated_calories": 350,
                "estimated_protein": 30.0,
                "estimated_carbs": 40.0,
                "estimated_fat": 5.0
            },
            {
                "title": "Greek Yogurt Bowl",
                "description": "Combine low-fat Greek yogurt with fresh berries.",
                "ingredients": [
                    {"name": "Greek Yogurt 0%", "weight_g": 200.0},
                    {"name": "Blueberries", "weight_g": 50.0}
                ],
                "estimated_calories": 180,
                "estimated_protein": 20.0,
                "estimated_carbs": 15.0,
                "estimated_fat": 1.0
            }
        ]
    }

    mock_agent_run.return_value = mock_response

    payload = {
        "remaining_calories": 500,
        "remaining_protein": 30,
        "remaining_carbs": 50,
        "remaining_fat": 10,
        "user_preferences": "High protein, lactose-free",
    }

    response = client.post("/api/ai/gapfiller", json=payload)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == mock_response.output

    prompt_arg = mock_agent_run.call_args[0][0]
    assert "- Calories: 500 kcal" in prompt_arg
    assert "High protein, lactose-free" in prompt_arg

@patch("routers.ai.agent.gap_filler_agent.run", new_callable=AsyncMock)
def test_get_daily_gap_filler_ai_error(mock_agent_run):
    mock_agent_run.side_effect = Exception("GapFiller Agent Failed")

    payload = {
        "remaining_calories": 300,
        "remaining_protein": 20,
        "remaining_carbs": 20,
        "remaining_fat": 5,
        "user_preferences": "None",
    }

    response = client.post("/api/ai/gapfiller", json=payload)

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json()["detail"] == "GapFiller Agent Failed"

@patch("routers.ai.agent.food_scan_agent.run", new_callable=AsyncMock)
def test_create_ai_analyzed_food_success(mock_agent_run, mock_db):
    mock_cursor, mock_get_db_cursor = mock_db

    mock_ai_output = MagicMock()
    mock_ai_output.name = "Pizza Margherita"
    mock_ai_output.calories_per_100g = 266.0
    mock_ai_output.protein_per_100g = 11.0
    mock_ai_output.carbs_per_100g = 33.0
    mock_ai_output.fat_per_100g = 10.0

    mock_response = MagicMock()
    mock_response.output = mock_ai_output
    mock_agent_run.return_value = mock_response

    saved_food = {
        "id": 42,
        "name": "Pizza Margherita",
        "calories_per_100g": 266.0,
        "protein_per_100g": 11.0,
        "carbs_per_100g": 33.0,
        "fat_per_100g": 10.0,
        "is_custom": False,
        "created_by_user_id": 1,
    }
    mock_cursor.fetchone.return_value = saved_food

    fake_image_bytes = b"fake-image-bytes-data"
    files = {"file": ("test_food.jpeg", BytesIO(fake_image_bytes), "image/jpeg")}
    data = {"user_id": "1"}

    response = client.post("/api/ai/foodscan", data=data, files=files)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == saved_food

    db_call_args = mock_cursor.execute.call_args[0]
    assert "INSERT INTO foods" in db_call_args[0]
    assert db_call_args[1] == ("Pizza Margherita", 266.0, 11.0, 33.0, 10.0, False, 1)

def test_create_ai_analyzed_food_invalid_file_type():
    files = {"file": ("doc.txt", BytesIO(b"some text content"), "text/plain")}
    data = {"user_id": "1"}

    response = client.post("/api/ai/foodscan", data=data, files=files)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "File must be an image"