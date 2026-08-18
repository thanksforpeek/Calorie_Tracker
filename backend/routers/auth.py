import schemas, utils
from database import get_db_cursor
from fastapi import HTTPException, status, APIRouter

router = APIRouter(
    prefix="/api/auth",
    tags=["Auth"]
)

@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: schemas.UserRegister):
    hashed = utils.hash_password(user_data.password)

    with get_db_cursor() as cursor:
        cursor.execute("SELECT id FROM users WHERE email = %s;", (user_data.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email is already registered")

        query = """
                INSERT INTO users (email, password_hash)
                VALUES (%s, \
                        %s) RETURNING id, email, weight_kg, height_cm, age, activity_level, target_calories, target_protein, target_carbs, target_fats;
                """
        cursor.execute(query, (user_data.email, hashed))
        return cursor.fetchone()


@router.post("/login", response_model=schemas.UserResponse)
def login_user(credentials: schemas.UserLogin):
    with get_db_cursor() as cursor:
        query = """
                SELECT id, \
                       email, \
                       password_hash, \
                       weight_kg, \
                       height_cm, \
                       age,
                       activity_level, \
                       target_calories, \
                       target_protein, \
                       target_carbs, \
                       target_fats
                FROM users \
                WHERE email = %s;
                """
        cursor.execute(query, (credentials.email,))
        user_record = cursor.fetchone()

        if not user_record or not utils.verify_password(credentials.password, user_record["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        user_record.pop("password_hash", None)
        return user_record