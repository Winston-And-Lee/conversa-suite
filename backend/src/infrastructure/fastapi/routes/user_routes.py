from typing import List, Optional, Dict
import logging

from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

from src.domain.models.user import User
from src.infrastructure.fastapi.schemas.user import (
    UserBase, UserCreate, UserResponse, UserUpdate, 
    UserLogin, UserLoginResponse, UserResetPassword,
    UserVerification, UserVerify, UserProfile,
    UserRefreshToken, UserRefreshResponse, TokenResponse
)
from src.usecase.user.user_usecase import UserUsecase
from src.usecase.user import get_user_usecase_async

# Create a logger for this module
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Simple test endpoint to verify routing
@router.get("/test")
async def test_endpoint():
    """Test endpoint to verify router is working."""
    logger.info("Test endpoint hit successfully")
    return {"message": "User routes test endpoint is working!"}

# Create OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")

# Create dependency for user_usecase that ensures database connection
async def get_user_usecase_dependency():
    """Dependency that provides the user usecase with database connection."""
    try:
        # Make sure we use the async version which handles DB connection
        user_usecase = await get_user_usecase_async()
        # Verify database connection
        if user_usecase.user_repository is None:
            from src.interface.repository.database.db_repository import ensure_db_connected
            await ensure_db_connected()
            from src.interface.repository.database.db_repository import user_repository
            user_usecase.user_repository = user_repository()
        return user_usecase
    except Exception as e:
        # Provide clear error message to client
        logger.error(f"Database connection error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service unavailable. Please try again later."
        )

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_usecase = Depends(get_user_usecase_dependency)
) -> User:
    """Get the current authenticated user."""
    user = await user_usecase.user_authentication(token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


# Auth endpoints

@router.post("/register", response_model=UserLoginResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    user_usecase = Depends(get_user_usecase_dependency)
):
    """
    Register a new user.
    
    Args:
        user_data: User registration data
        
    Returns:
        User info with access token
    """
    if not is_mongo_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service is not available"
        )
    
    try:
        auth_response = await user_usecase.register_user(user_data)
        
        if not auth_response.user or not auth_response.access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to register user"
            )
            
        # Log successful registration
        logger.info(f"User registered: {auth_response.user.email}")
        
        return UserLoginResponse(
            user=UserResponse(
                _id=str(auth_response.user.id),
                email=auth_response.user.email,
                first_name=auth_response.user.first_name,
                last_name=auth_response.user.last_name,
                is_active=auth_response.user.is_active,
                is_admin=auth_response.user.is_admin,
                created_at=auth_response.user.created_at,
                updated_at=auth_response.user.updated_at
            ),
            token=TokenResponse(
                access=auth_response.access_token,
                refresh=auth_response.refresh_token or ""
            )
        )
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user"
        )


class GoogleLoginRequest(BaseModel):
    token: str
    profile: Dict[str, str]


class MicrosoftLoginRequest(BaseModel):
    token: str
    profile: Dict[str, str]


@router.post("/login", response_model=UserLoginResponse)
async def login_user(
    login_json: Optional[UserLogin] = None,
    user_usecase = Depends(get_user_usecase_dependency)
):
    """
    Login a user.
    
    Args:
        login_json: Login data
        
    Returns:
        User info with access and refresh tokens
    """
    if not is_mongo_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service is not available"
        )
    
    if not login_json:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing login data"
        )
    
    try:
        auth_response = await user_usecase.user_login(
            login_json.email, 
            login_json.password
        )
        
        if not auth_response.user or not auth_response.access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Log successful login
        logger.info(f"User logged in: {auth_response.user.email}")
        
        return UserLoginResponse(
            user=UserResponse(
                _id=str(auth_response.user.id),
                email=auth_response.user.email,
                first_name=auth_response.user.first_name,
                last_name=auth_response.user.last_name,
                is_active=auth_response.user.is_active,
                is_admin=auth_response.user.is_admin,
                created_at=auth_response.user.created_at,
                updated_at=auth_response.user.updated_at
            ),
            token=TokenResponse(
                access=auth_response.access_token,
                refresh=auth_response.refresh_token
            )
        )
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/request-verification", status_code=status.HTTP_202_ACCEPTED)
async def request_verification(
    verification_data: UserVerification,
    user_usecase = Depends(get_user_usecase_dependency)
):
    """
    Request a verification code for email verification.
    
    Args:
        verification_data: Verification request data
        
    Returns:
        Verification reference token
    """
    try:
        verification_response = await user_usecase.user_request_verification(
            verification_data.email
        )
        
        if not verification_response.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to send verification code"
            )
            
        return {
            "reference_token": verification_response.reference_token,
            "message": "Verification code sent to email"
        }
        
    except Exception as e:
        logger.error(f"Verification request error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process verification request"
        )


@router.post("/verify", status_code=status.HTTP_200_OK)
async def verify_user(
    verify_data: UserVerify,
    user_usecase = Depends(get_user_usecase_dependency)
):
    """
    Verify a user using a verification code.
    
    Args:
        verify_data: Verification data
        
    Returns:
        User info if verification is successful
    """
    try:
        verification_response = await user_usecase.user_verify(
            verify_data.email,
            verify_data.code
        )
        
        if not verification_response.success or not verification_response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification code"
            )
            
        user = verification_response.user
        return {
            "user": UserResponse(
                _id=str(user.id),
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                is_active=user.is_active,
                is_admin=user.is_admin,
                created_at=user.created_at,
                updated_at=user.updated_at
            ),
            "message": "User verified successfully"
        }
        
    except Exception as e:
        logger.error(f"User verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify user"
        )


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    reset_data: UserResetPassword,
    current_user: User = Depends(get_current_user),
    user_usecase = Depends(get_user_usecase_dependency)
):
    """
    Reset a user's password.
    
    Args:
        reset_data: Password reset data
        current_user: Current authenticated user
        
    Returns:
        Success message if password reset is successful
    """
    try:
        reset_response = await user_usecase.reset_password(
            str(current_user.id),
            reset_data.current_password,
            reset_data.new_password
        )
        
        if not reset_response.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=reset_response.message
            )
            
        # Get updated user info
        profile_response = await user_usecase.get_user_profile(str(current_user.id))
        
        if not profile_response.success or not profile_response.user:
            # Password was reset but couldn't fetch updated profile
            return {
                "message": "Password reset successfully"
            }
            
        user = profile_response.user
        return {
            "message": "Password reset successfully",
            "user": UserResponse(
                _id=str(user.id),
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                is_active=user.is_active,
                is_admin=user.is_admin,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
        }
        
    except Exception as e:
        logger.error(f"Password reset error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset password"
        )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout_user(
    refresh_token: str = Header(..., description="Refresh token"),
    user_usecase = Depends(get_user_usecase_dependency)
):
    """Log out a user."""
    success = await user_usecase.user_logout(refresh_token)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to log out"
        )
    
    return {"message": "Logged out successfully"}


@router.post("/refresh", response_model=UserRefreshResponse)
async def refresh_token(
    token_data: UserRefreshToken,
    user_usecase = Depends(get_user_usecase_dependency)
):
    """
    Refresh an access token using a refresh token.
    
    Args:
        token_data: Refresh token
        
    Returns:
        New access token and refresh token
    """
    try:
        refresh_response = await user_usecase.user_refresh_token(token_data.refresh_token)
        
        if not refresh_response.user or not refresh_response.access_token or not refresh_response.refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        return UserRefreshResponse(
            token=TokenResponse(
                access=refresh_response.access_token,
                refresh=refresh_response.refresh_token
            )
        )
    except Exception as e:
        logger.error(f"Error refreshing token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh token"
        )


@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    user_usecase = Depends(get_user_usecase_dependency)
):
    """
    Get the current user's profile.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User profile information
    """
    try:
        profile_response = await user_usecase.get_user_profile(str(current_user.id))
        
        if not profile_response.success or not profile_response.user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
            
        user = profile_response.user
        return UserProfile(
            _id=str(user.id),
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
            is_admin=user.is_admin
        )
        
    except Exception as e:
        logger.error(f"Error retrieving user profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user profile"
        )


@router.post("/login/google", response_model=UserLoginResponse)
async def login_with_google(
    login_data: GoogleLoginRequest,
    user_usecase = Depends(get_user_usecase_dependency)
):
    """
    Login with Google OAuth
    
    Args:
        login_data: Google token and profile data
        
    Returns:
        User info with access and refresh tokens
    """
    if not is_mongo_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service is not available"
        )
    
    try:
        # Extract profile data
        profile = login_data.profile
        email = profile.get("email", "")
        first_name = profile.get("first_name", "")
        last_name = profile.get("last_name", "")
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is required"
            )
        
        auth_response = await user_usecase.user_login_via_google(
            email,
            login_data.token,
            first_name,
            last_name
        )
        
        if not auth_response.user or not auth_response.access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Google login failed",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Log successful login
        logger.info(f"User logged in via Google: {auth_response.user.email}")
        
        return UserLoginResponse(
            user=UserResponse(
                _id=str(auth_response.user.id),
                email=auth_response.user.email,
                first_name=auth_response.user.first_name,
                last_name=auth_response.user.last_name,
                is_active=auth_response.user.is_active,
                is_admin=auth_response.user.is_admin,
                created_at=auth_response.user.created_at,
                updated_at=auth_response.user.updated_at
            ),
            token=TokenResponse(
                access=auth_response.access_token,
                refresh=auth_response.refresh_token
            )
        )
        
    except Exception as e:
        logger.error(f"Google login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google login failed"
        )


@router.post("/login/microsoft", response_model=UserLoginResponse)
async def login_with_microsoft(
    login_data: MicrosoftLoginRequest,
    user_usecase = Depends(get_user_usecase_dependency)
):
    """
    Login with Microsoft OAuth
    
    Args:
        login_data: Microsoft token and profile data
        
    Returns:
        User info with access and refresh tokens
    """
    if not is_mongo_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service is not available"
        )
    
    try:
        # Extract profile data
        profile = login_data.profile
        email = profile.get("email", "")
        first_name = profile.get("first_name", "")
        last_name = profile.get("last_name", "")
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is required"
            )
            
        auth_response = await user_usecase.user_login_via_microsoft(
            email,
            login_data.token,
            first_name,
            last_name
        )
        
        if not auth_response.user or not auth_response.access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Microsoft login failed",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Log successful login
        logger.info(f"User logged in via Microsoft: {auth_response.user.email}")
        
        return UserLoginResponse(
            user=UserResponse(
                _id=str(auth_response.user.id),
                email=auth_response.user.email,
                first_name=auth_response.user.first_name,
                last_name=auth_response.user.last_name,
                is_active=auth_response.user.is_active,
                is_admin=auth_response.user.is_admin,
                created_at=auth_response.user.created_at,
                updated_at=auth_response.user.updated_at
            ),
            token=TokenResponse(
                access=auth_response.access_token,
                refresh=auth_response.refresh_token
            )
        )
        
    except Exception as e:
        logger.error(f"Microsoft login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Microsoft login failed"
        )


def is_mongo_available() -> bool:
    """Check if MongoDB connection is available."""
    try:
        # This is a simple check - in a real application, we would 
        # check the actual connection status
        return True
    except Exception as e:
        logger.error(f"MongoDB connection error: {str(e)}")
        return False 