from pydantic import BaseModel, Field
from typing import Optional, List

class UserData(BaseModel):
    email: str
    password: str

class UserRegister(UserData):
    pass
class UserLogin(UserData):
    pass

class UserTargetsUpdate(BaseModel):
    weight_kg: float
    height_cm: int
    age: int
    activity_level: str
    target_calories: int
    target_protein: int
    target_carbs: int
    target_fats: int

class FoodLogBase(BaseModel):
    meal_type: str
    serving_size_g: float
    log_date: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: str
    weight_kg: Optional[float] = None
    height_cm: Optional[int] = None
    age: Optional[int] = None
    activity_level: Optional[str] = None
    target_calories: Optional[int] = None
    target_protein: Optional[int] = None
    target_carbs: Optional[int] = None
    target_fats: Optional[int] = None

class MacrosPerHundredGrams(BaseModel):
    calories_per_100g: int
    protein_per_100g: float
    carbs_per_100g: float
    fat_per_100g: float

class CustomFoodCreate(MacrosPerHundredGrams):
    name: str
    is_custom: bool = True
    created_by_user_id: Optional[int] = None

class FoodResponse(MacrosPerHundredGrams):
    id: int
    name: str
    is_custom: bool
    created_by_user_id: Optional[int] = None

class FoodLogCreate(FoodLogBase):
    user_id: int
    food_id: int

class FoodLogUpdate(BaseModel):
    serving_size_g: float

class FoodLogReadResponse(MacrosPerHundredGrams, FoodLogBase):
    id: int
    logged_at: str
    food_name: str

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

class ChatScanResponse(BaseModel):
    name: str = Field(description="A concise and clear title of the meal (e.g., 'Grilled Chicken Breast with Rice')")
    calories_per_100g: int = Field(description="Total estimated energy content STRICTLY per 100 grams of the meal in kcal")
    protein_per_100g: float = Field(description="Total estimated protein content STRICTLY per 100 grams of the meal in grams")
    carbs_per_100g: float= Field(description="Total estimated carbohydrates content STRICTLY per 100 grams of the meal in grams")
    fat_per_100g: float = Field(description="Total estimated fat content STRICTLY per 100 grams of the meal in grams")


class GapFillerRequest(BaseModel):
    remaining_calories: int = Field(description="Calories left to reach daily target in kcal")
    remaining_protein: float = Field(description="Protein left to reach daily target in grams")
    remaining_carbs: float = Field(description="Carbohydrates left to reach daily target in grams")
    remaining_fat: float = Field(description="Fats left to reach daily target in grams")
    user_preferences: Optional[str] = Field(
        default="No specific restrictions, quick preparation",
        description="Dietary restrictions or available ingredients provided by the user"
    )

class MealIngredient(BaseModel):
    name: str = Field(description="Name of the ingredient, e.g., 'Cottage Cheese 5%'")
    weight_g: float = Field(description="Estimated weight in grams")

class MealOption(BaseModel):
    title: str = Field(description="Concise name of the meal or snack")
    description: str = Field(description="Short recipe or quick preparation instructions")
    ingredients: List[MealIngredient] = Field(description="List of required ingredients")
    estimated_calories: int = Field(description="Total estimated energy in kcal for this meal")
    estimated_protein: float = Field(description="Total estimated protein in grams for this meal")
    estimated_carbs: float = Field(description="Total estimated carbohydrates in grams for this meal")
    estimated_fat: float = Field(description="Total estimated fats in grams for this meal")

class GapFillerResponse(BaseModel):
    summary: str = Field(description="A brief encouraging comment (1 sentence)")
    options: List[MealOption] = Field(description="2-3 recommended meal options")