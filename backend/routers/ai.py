import agent
import schemas
from pydantic_ai import BinaryContent
from database import get_db_cursor
from fastapi import status, APIRouter, HTTPException, UploadFile, File, Form

router = APIRouter(
    prefix="/api/ai",
    tags=["AI"]
)

@router.post("/foodanalyze", response_model=schemas.ChatResponse, status_code=status.HTTP_201_CREATED)
async def analyze_described_food(req: schemas.ChatRequest):
    try:
        ai_response = await agent.chat_agent.run(req.message)
        return ai_response.output
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/gapfiller", response_model=schemas.GapFillerResponse)
async def get_daily_gap_filler(req: schemas.GapFillerRequest):
    user_prompt = (
        f"I need to hit my remaining daily macro targets:\n"
        f"- Calories: {req.remaining_calories} kcal\n"
        f"- Protein: {req.remaining_protein} g\n"
        f"- Carbs: {req.remaining_carbs} g\n"
        f"- Fat: {req.remaining_fat} g\n\n"
        f"My dietary preferences and available ingredients: {req.user_preferences}.\n"
        f"Please suggest 2-3 suitable meal options."
    )

    try:
        ai_response = await agent.gap_filler_agent.run(user_prompt)
        return ai_response.output
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/foodscan", response_model=schemas.FoodResponse, status_code=status.HTTP_201_CREATED)
async def create_ai_analyzed_food(user_id: int = Form(...), file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )

    image_bytes = await file.read()

    ai_response = await agent.food_scan_agent.run([
        "Analyze this meal and calculate macros strictly per 100g:",
        BinaryContent(data=image_bytes, media_type=file.content_type)
    ])

    extracted_data: schemas.ChatScanResponse = ai_response.output

    query = """
            INSERT INTO foods (name, calories_per_100g, protein_per_100g, carbs_per_100g, fat_per_100g, is_custom, \
                                created_by_user_id)
            VALUES (%s, %s, %s, %s, %s, %s, \
                    %s) RETURNING id, name, calories_per_100g, protein_per_100g, carbs_per_100g, fat_per_100g, is_custom, created_by_user_id;
            """

    with get_db_cursor() as cursor:

        params = (
            extracted_data.name, extracted_data.calories_per_100g, extracted_data.protein_per_100g,
            extracted_data.carbs_per_100g, extracted_data.fat_per_100g, False, user_id
        )
        cursor.execute(query, params)
        return cursor.fetchone()