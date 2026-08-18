from datetime import date
from fastapi import status
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

mock_log = {
    "id": 1,
    "meal_type": "breakfast",
    "serving_size_g": 150.0,
    "logged_at": "2026-08-07 10:00",
    "log_date": "2026-08-07",
    "food_name": "Apple",
    "calories_per_100g": 52.0,
    "protein_per_100g": 0.3,
    "carbs_per_100g": 14.0,
    "fat_per_100g": 0.2
}

def test_get_all_food_logs_with_date(mock_db):
    mock_cursor, mock_get_db_cursor = mock_db
    mock_cursor.fetchall.return_value = [mock_log]

    response = client.get("/api/food-logs/?user_id=1&date=2026-08-07")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [mock_log]

    mock_get_db_cursor.assert_called_once()
    mock_cursor.fetchall.assert_called_once()

    call_args = mock_cursor.execute.call_args[0]
    assert "WHERE fl.user_id = %s AND fl.log_date = %s" in call_args[0]
    assert call_args[1] == (1, date(2026, 8, 7))

def test_add_food_log_success(mock_db):
    mock_cursor, mock_get_db_cursor = mock_db

    created_log = {
        "id": 1,
        "user_id": 1,
        "food_id": 2,
        "meal_type": "lunch",
        "serving_size_g": 200.0,
        "log_date": "2026-08-07",
        "logged_at": "2026-08-07 12:30",
    }
    mock_cursor.fetchone.return_value = created_log

    payload = {
        "user_id": 1,
        "food_id": 2,
        "meal_type": "lunch",
        "serving_size_g": 200.0,
        "log_date": "2026-08-07",
    }

    response = client.post("/api/food-logs/", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == created_log

    call_args = mock_cursor.execute.call_args[0]
    assert "INSERT INTO food_logs" in call_args[0]
    assert call_args[1] == (1, 2, "lunch", 200.0, '2026-08-07')

def test_update_food_log_success(mock_db):
    mock_cursor, mock_get_db_cursor = mock_db

    updated_log = {
        "id": 1,
        "user_id": 1,
        "food_id": 2,
        "meal_type": "lunch",
        "serving_size_g": 250.0,
        "log_date": "2026-08-07",
        "logged_at": "2026-08-07 12:30",
    }
    mock_cursor.fetchone.return_value = updated_log

    response = client.put("/api/food-logs/1", json=updated_log)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == updated_log

    call_args = mock_cursor.execute.call_args[0]
    assert "UPDATE food_logs" in call_args[0]
    assert call_args[1] == (250.0, 1)

def test_update_food_log_not_found(mock_db):
    mock_cursor, mock_get_db_cursor = mock_db
    mock_cursor.fetchone.return_value = None

    response = client.put("/api/food-logs/999", json={"serving_size_g": 250.0})

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Log entry not found"

def test_delete_food_log_success(mock_db):
    mock_cursor, mock_get_db_cursor = mock_db
    mock_cursor.fetchone.return_value = {"id": 1}

    response = client.delete("/api/food-logs/1")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b""

    call_args = mock_cursor.execute.call_args[0]
    assert "DELETE FROM food_logs" in call_args[0]
    assert call_args[1] == (1,)


def test_delete_food_log_not_found(mock_db):
    mock_cursor, _ = mock_db
    mock_cursor.fetchone.return_value = None

    response = client.delete("/api/food-logs/999")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Log entry not found"

def test_get_weekly_summary(mock_db):
    mock_cursor, _ = mock_db
    mock_cursor.fetchall.return_value = [
        {"log_date": "2026-08-07", "total_calories": 520.4}
    ]

    response = client.get("/api/food-logs/weekly-summary?user_id=1&start_date=2026-08-07")

    assert response.status_code == status.HTTP_200_OK
    result = response.json()

    assert len(result) == 7
    assert result[0] == {"day": "Fri", "date": "2026-08-07", "calories": 520}
    assert result[1] == {"day": "Sat", "date": "2026-08-08", "calories": 0}