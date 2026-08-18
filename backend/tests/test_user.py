from fastapi import status
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

mock_user = {
    "id": 1,
    "email": "test@gmail.com",
    "weight_kg": 70.0,
    "height_cm": 175.0,
    "age": 25,
    "activity_level": "moderate",
    "target_calories": 2000,
    "target_protein": 150,
    "target_carbs": 200,
    "target_fats": 70,
}

def test_update_user_targets_success(mock_db):
    mock_cursor, mock_get_db_cursor = mock_db

    mock_cursor.fetchone.return_value = dict(mock_user)

    payload = {
        "weight_kg": 70.0,
        "height_cm": 175.0,
        "age": 25,
        "activity_level": "moderate",
        "target_calories": 2000,
        "target_protein": 150,
        "target_carbs": 200,
        "target_fats": 70,
    }

    user_id = 1

    response = client.put(f"/api/users/{user_id}/targets", json=payload)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == mock_user
    mock_get_db_cursor.assert_called_once()
    mock_cursor.execute.assert_called_once()

    call_args = mock_cursor.execute.call_args[0]

    assert "UPDATE users" in call_args[0]
    assert call_args[1] == (70.0, 175.0, 25, "moderate", 2000, 150, 200, 70, user_id)

def test_update_user_targets_not_found(mock_db):
    mock_cursor, mock_get_db_cursor = mock_db

    mock_cursor.fetchone.return_value = None

    payload = {
        "weight_kg": 70.0,
        "height_cm": 175.0,
        "age": 25,
        "activity_level": "moderate",
        "target_calories": 2000,
        "target_protein": 150,
        "target_carbs": 200,
        "target_fats": 70,
    }

    response = client.put("/api/users/999/targets", json=payload)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "User not found"
    mock_get_db_cursor.assert_called_once()
    mock_cursor.execute.assert_called_once()

def test_update_user_targets_validation_error(mock_db):
    payload = {
        "height_cm": 180.0,
        "age": 26,
    }

    response = client.put("/api/users/1/targets", json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_update_user_targets_invalid_user_id_type(mock_db):
    payload = {
        "weight_kg": 75.0,
        "height_cm": 180.0,
        "age": 26,
        "activity_level": "active",
        "target_calories": 2500,
        "target_protein": 180,
        "target_carbs": 250,
        "target_fats": 80,
    }

    response = client.put("/api/users/not-an-int/targets", json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY