import schemas
from database import get_db_cursor
from fastapi import HTTPException, APIRouter

router = APIRouter(
    prefix="/api/users",
    tags=["User"],
)

@router.put("/{user_id}/targets", response_model=schemas.UserResponse)
def update_user_targets(user_id: int, targets: schemas.UserTargetsUpdate):
    with get_db_cursor() as cursor:
        query = """
                UPDATE users
                SET weight_kg       = %s,
                    height_cm       = %s,
                    age             = %s,
                    activity_level  = %s,
                    target_calories = %s,
                    target_protein  = %s,
                    target_carbs    = %s,
                    target_fats     = %s
                WHERE id = %s RETURNING id, email, weight_kg, height_cm, age, activity_level, target_calories, target_protein, target_carbs, target_fats;
                """
        params = (
            targets.weight_kg, targets.height_cm, targets.age, targets.activity_level,
            targets.target_calories, targets.target_protein, targets.target_carbs, targets.target_fats,
            user_id
        )
        cursor.execute(query, params)
        updated_user = cursor.fetchone()

        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        return updated_user