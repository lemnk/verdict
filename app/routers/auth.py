from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.models.auth import UserLogin, UserRegister, UserResponse

router = APIRouter()
security = HTTPBearer()

@router.post("/login", response_model=UserResponse)
async def login(user_data: UserLogin):
    """Authenticate user and return access token"""
    # TODO: Implement actual authentication logic
    if user_data.email == "test@example.com" and user_data.password == "password":
        return UserResponse(
            id=1,
            email=user_data.email,
            name="Test User",
            access_token="dummy_token_123"
        )
    raise HTTPException(status_code=401, detail="Invalid credentials")

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserRegister):
    """Register new user account"""
    # TODO: Implement actual registration logic
    return UserResponse(
        id=1,
        email=user_data.email,
        name=user_data.name,
        access_token="dummy_token_123"
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user info"""
    # TODO: Implement token validation
    return UserResponse(
        id=1,
        email="test@example.com",
        name="Test User",
        access_token=credentials.credentials
    )