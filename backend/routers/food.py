import schemas
from database import get_db_cursor
from fastapi import status, APIRouter
from typing import List, Optional

router = APIRouter(
    prefix="/api/foods",
    tags=["Food"]
)

@router.get("/search", response_model=List[schemas.FoodResponse])
def search_foods(q: Optional[str] = None):
    with get_db_cursor() as cursor:
        if q:
            query = """
                    SELECT id, \
                           name, \
                           calories_per_100g, \
                           protein_per_100g, \
                           carbs_per_100g, \
                           fat_per_100g, \
                           is_custom, \
                           created_by_user_id
                    FROM foods \
                    WHERE name ILIKE %s;
                    """
            cursor.execute(query, (f"%{q}%",))
        else:
            query = """
                    SELECT id, \
                           name, \
                           calories_per_100g, \
                           protein_per_100g, \
                           carbs_per_100g, \
                           fat_per_100g, \
                           is_custom, \
                           created_by_user_id
                    FROM foods LIMIT 50;
                    """
            cursor.execute(query)
        return cursor.fetchall()


@router.post("/", response_model=schemas.FoodResponse, status_code=status.HTTP_201_CREATED)
def create_custom_food(food: schemas.CustomFoodCreate):
    with get_db_cursor() as cursor:
        query = """
                INSERT INTO foods (name, calories_per_100g, protein_per_100g, carbs_per_100g, fat_per_100g, is_custom, \
                                   created_by_user_id)
                VALUES (%s, %s, %s, %s, %s, %s, \
                        %s) RETURNING id, name, calories_per_100g, protein_per_100g, carbs_per_100g, fat_per_100g, is_custom, created_by_user_id;
                """
        params = (
            food.name, food.calories_per_100g, food.protein_per_100g,
            food.carbs_per_100g, food.fat_per_100g, food.is_custom, food.created_by_user_id
        )
        cursor.execute(query, params)
        return cursor.fetchone()


