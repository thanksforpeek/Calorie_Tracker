from unittest.mock import patch
from fastapi import status
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

mock_user = {
    "id": 1,
    "email": "test@gmail.com",
    "password_hash": "hashed_secret_password",
    "weight_kg": None,
    "height_cm": None,
    "age": None,
    "activity_level": None,
    "target_calories": None,
    "target_protein": None,
    "target_carbs": None,
    "target_fats": None
}

@patch("routers.auth.utils.hash_password", return_value="hashed_secret_password")
def test_register_user_success(mock_hash_password, mock_db):
    mock_cursor, mock_get_db_cursor = mock_db

    user_response_data = dict(mock_user)
    user_response_data.pop("password_hash")

    mock_cursor.fetchone.side_effect = [None, user_response_data]

    payload = {
        "email": "test@gmail.com",
        "password": "secret_password"
    }

    response = client.post("/api/auth/register", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == user_response_data
    mock_hash_password.assert_called_once_with("secret_password")
    mock_get_db_cursor.assert_called_once()
    assert mock_cursor.fetchone.call_count == 2

def test_register_user_already_exists(mock_db):
    mock_cursor, mock_get_db_cursor = mock_db

    mock_cursor.fetchone.return_value = {"id": 1}

    payload = {
        "email": "test@gmail.com",
        "password": "secret_password"
    }

    response = client.post("/api/auth/register", json=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()['detail'] == "Email is already registered"
    assert mock_cursor.execute.call_count == 1

@patch("routers.auth.utils.verify_password", return_value=True)
def test_login_user_success(mock_verify_password, mock_db):
    mock_cursor, mock_get_db_cursor = mock_db
    mock_cursor.fetchone.return_value = dict(mock_user)

    payload = {
        "email": "test@gmail.com",
        "password": "secret_password"
    }

    response = client.post("/api/auth/login", json=payload)

    expected_response = dict(mock_user)
    expected_response.pop("password_hash")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_response
    assert "password_hash" not in response.json()
    mock_verify_password.assert_called_once_with("secret_password", "hashed_secret_password")

def test_login_user_not_found(mock_db):
    mock_cursor, mock_get_db_cursor = mock_db

    mock_cursor.fetchone.return_value = None

    payload = {
        "email": "test@gmail.com",
        "password": "secret_password"
    }

    response = client.post("/api/auth/login", json=payload)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()['detail'] == "Invalid email or password"

@patch("routers.auth.utils.verify_password", return_value=False)
def test_login_user_wrong_password(mock_verify_password, mock_db):
    mock_cursor, mock_get_db_cursor = mock_db

    mock_cursor.fetchone.return_value = dict(mock_user)

    payload = {
        "email": "test@gmail.com",
        "password": "secret_password"
    }

    response = client.post("/api/auth/login", json=payload)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()['detail'] == "Invalid email or password"
    mock_verify_password.assert_called_once_with("secret_password", "hashed_secret_password")