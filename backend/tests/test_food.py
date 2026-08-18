from unittest.mock import patch, MagicMock
from pytest import fixture
from fastapi import status
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

mock_food = {
    "id": 1,
    "name": "Apple",
    "calories_per_100g": 52.0,
    "protein_per_100g": 0.3,
    "carbs_per_100g": 14.0,
    "fat_per_100g": 0.2,
    "is_custom": False,
    "created_by_user_id": None
}

def test_search_foods_without_query(mock_db):
    mock_cursor, mock_get_db_cursor = mock_db
    mock_cursor.fetchall.return_value = [mock_food]

    response = client.get("/api/foods/search")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [mock_food]
    mock_get_db_cursor.assert_called_once()
    mock_cursor.execute.assert_called_once()

    executed_sql = mock_cursor.execute.call_args[0][0]
    assert "LIMIT 50" in executed_sql

def test_search_foods_with_query(mock_db):
    mock_cursor, mock_get_db_cursor = mock_db
    mock_cursor.fetchall.return_value = [mock_food]

    search_term = "apple"
    response = client.get(f"/api/foods/search?q={search_term}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [mock_food]
    mock_get_db_cursor.assert_called_once()
    mock_cursor.execute.assert_called_once()

    call_args = mock_cursor.execute.call_args[0]
    assert "ILIKE %s" in call_args[0]
    assert call_args[1] == (f"%{search_term}%",)

def test_create_custom_food_success(mock_db):
    mock_cursor, mock_get_db_cursor = mock_db

    custom_food = dict(mock_food)
    custom_food["is_custom"] = True
    custom_food["created_by_user_id"] = 10
    mock_cursor.fetchone.return_value = custom_food

    payload = {
        "name": "Apple",
        "calories_per_100g": 52.0,
        "protein_per_100g": 0.3,
        "carbs_per_100g": 14.0,
        "fat_per_100g": 0.2,
        "is_custom": True,
        "created_by_user_id": 10
    }

    response = client.post("/api/foods/", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == custom_food
    mock_get_db_cursor.assert_called_once()
    mock_cursor.execute.assert_called_once()

    call_args = mock_cursor.execute.call_args[0]
    assert "INSERT INTO foods" in call_args[0]
    assert call_args[1] == ("Apple", 52.0, 0.3, 14.0, 0.2, True, 10)

def test_create_custom_food_validation_error(mock_db):
    payload = {
        "calories_per_100g": 52.0,
        "protein_per_100g": 0.3,
        "carbs_per_100g": 14.0,
        "fat_per_100g": 0.2,
        "is_custom": True,
    }

    response = client.post("/api/foods/", json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY