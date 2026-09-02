from dotenv import load_dotenv
from pydantic_ai import Agent

import schemas

load_dotenv()

chat_agent = Agent(
    "google:gemini-3-flash-preview",
    output_type=schemas.ChatResponse,
    system_prompt=(
        "You are a precise meal and macro-tracking assistant. "
        "Analyze the food described by the user and calculate its nutritional contents."
    ),
)

food_scan_agent = Agent(
    "google:gemini-3-flash-preview",
    output_type=schemas.ChatScanResponse,
    system_prompt=(
        "You are a precise meal and macro-tracking assistant. Your sole task is to analyze "
        "photos of meals provided by the user and estimate their nutritional content.\n\n"
        "CRITICAL INSTRUCTIONS:\n"
        "1. Identify the meal shown in the image and generate a concise name for it.\n"
        "2. Calculate all nutritional values (Calories, Protein, Carbs, Fat) STRICTLY per 100 grams "
        "of the prepared food, NOT for the entire meal portion.\n"
        "3. Explicitly consider hidden ingredients like cooking oils, sauces, or dressings.\n"
        "4. Keep all estimates realistic based on standard nutritional data."
    ),
)

gap_filler_agent = Agent(
    "google:gemini-3-flash-preview",
    output_type=schemas.GapFillerResponse,
    system_prompt=(
        "You are an expert nutritionist assistant. "
        "Your task is to suggest 2-3 realistic meal options or snacks to help the user hit "
        "their remaining macro goals for the day.\n\n"
        "RULES:\n"
        "1. Strictly respect the user's dietary preferences and available ingredients (if provided).\n"
        "2. The total calories and macros of each suggested option should be as close as possible "
        "to the requested remaining target.\n"
        "3. Keep meal prep fast and simple for evening meals/snacks.\n"
        "4. Respond in the same language as the user's preferences."
    ),
)