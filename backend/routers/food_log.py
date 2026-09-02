import os
import schemas
import httpx
from database import get_db_cursor
from fastapi import HTTPException, status, APIRouter, Response
from typing import List, Optional
from datetime import date, datetime, timedelta

router = APIRouter(
    prefix="/api/food-logs",
    tags=["Food-log"]
)

@router.get("/", response_model=List[schemas.FoodLogReadResponse])
def get_all_food_logs(user_id: int, date: Optional[date] = None):
    if not date:
        date = date.today()

    with get_db_cursor() as cursor:
        query = """
                SELECT fl.id,
                       fl.meal_type,
                       fl.serving_size_g,
                       TO_CHAR(fl.logged_at, 'YYYY-MM-DD HH24:MI') AS logged_at,
                       TO_CHAR(fl.log_date, 'YYYY-MM-DD')         AS log_date,
                       f.name                                      AS food_name,
                       f.calories_per_100g,
                       f.protein_per_100g,
                       f.carbs_per_100g,
                       f.fat_per_100g
                FROM food_logs fl
                         JOIN foods f ON fl.food_id = f.id
                WHERE fl.user_id = %s AND fl.log_date = %s;
                """
        cursor.execute(query, (user_id, date))
        return cursor.fetchall()

@router.get("/weekly-summary")
def get_weekly_summary(user_id: int, start_date: str):
    summary_url = os.getenv("SUMMARY_LAMBDA_URL")
    if not summary_url:
        raise HTTPException(
            status_code=500,
            detail="SUMMARY_LAMBDA_URL is not set in environment"
        )

    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    end = start + timedelta(days=6)

    with get_db_cursor() as cursor:
        query = """
                SELECT fl.log_date AS log_date, SUM(f.calories_per_100g * (fl.serving_size_g / 100.0)) AS total_calories
                FROM food_logs fl
                         JOIN foods f ON fl.food_id = f.id
                WHERE fl.user_id = %s 
                  AND fl.log_date BETWEEN %s AND %s
                GROUP BY fl.log_date
                ORDER BY fl.log_date; 
                """
        cursor.execute(query, (user_id, start, end))
        rows = cursor.fetchall()

    logged_data = {str(row["log_date"]): round(row["total_calories"]) for row in rows}

    result = []
    for i in range(7):
        current_day = start + timedelta(days=i)
        day_str = str(current_day)
        result.append({
            "log_date": day_str,
            "total_calories": float(logged_data.get(day_str, 0))
        })

    with httpx.Client(timeout=10.0) as client:
        try:
            res = client.post(
                summary_url,
                json={"start_date": start_date, "rows": result}
            )
            res.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Lambda Error ({exc.response.status_code}): {exc.response.text}"
            )
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Connection to Lambda failed: {str(exc)}"
            )

        return res.json()

@router.post("/", status_code=status.HTTP_201_CREATED)
def add_food_log(log: schemas.FoodLogCreate):
    log_date_value = log.log_date if log.log_date else date.today()

    with get_db_cursor() as cursor:
        query = """
                INSERT INTO food_logs (user_id, food_id, meal_type, serving_size_g, log_date)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, user_id, food_id, meal_type, serving_size_g, log_date,
                          TO_CHAR(logged_at, 'YYYY-MM-DD HH24:MI') AS logged_at;
                """
        cursor.execute(query, (log.user_id, log.food_id, log.meal_type, log.serving_size_g, log_date_value))
        return cursor.fetchone()


@router.put("/{log_id}")
def update_food_log(log_id: int, log_update: schemas.FoodLogUpdate):
    with get_db_cursor() as cursor:
        query = """
                UPDATE food_logs
                SET serving_size_g = %s
                WHERE id = %s 
                RETURNING id, user_id, food_id, meal_type, serving_size_g, log_date,
                          TO_CHAR(logged_at, 'YYYY-MM-DD HH24:MI') AS logged_at;
                """
        cursor.execute(query, (log_update.serving_size_g, log_id))
        updated_row = cursor.fetchone()
        if not updated_row:
            raise HTTPException(status_code=404, detail="Log entry not found")
        return updated_row


@router.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_food_log(log_id: int):
    with get_db_cursor() as cursor:
        cursor.execute("DELETE FROM food_logs WHERE id = %s RETURNING id;", (log_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Log entry not found")
        return None