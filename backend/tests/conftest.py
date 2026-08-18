from unittest.mock import patch, MagicMock
import pytest

@pytest.fixture
def mock_db():
    with patch("routers.ai.get_db_cursor") as mock_ai_db, \
            patch("routers.auth.get_db_cursor") as mock_auth_db, \
            patch("routers.food.get_db_cursor") as mock_food_db, \
            patch("routers.food_log.get_db_cursor") as mock_food_log_db, \
            patch("routers.user.get_db_cursor") as mock_user_db:
        mock_cursor = MagicMock()
        mock_get_db_cursor = MagicMock()
        mock_get_db_cursor.return_value.__enter__.return_value = mock_cursor

        mock_ai_db.side_effect = mock_get_db_cursor
        mock_auth_db.side_effect = mock_get_db_cursor
        mock_food_db.side_effect = mock_get_db_cursor
        mock_food_log_db.side_effect = mock_get_db_cursor
        mock_user_db.side_effect = mock_get_db_cursor

        yield mock_cursor, mock_get_db_cursor