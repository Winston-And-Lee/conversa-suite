import os
import jwt
import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Tuple, Dict, Any
import bcrypt
from pydantic import BaseModel, Field
import logging
import secrets
import string

from src.domain.models.user import User
from src.domain.models.user_verification import UserVerification
from src.config import settings
from src.domain.entity.user import (
    UserCreate,
    AuthResponse,
    RefreshTokenResponse,
    VerificationRequestResponse,
    VerificationResponse,
    ProfileResponse,
    PasswordResetResponse
)
from src.domain.repository.user_repository import UserRepository
from src.domain.repository.user_verification_repository import UserVerificationRepository
from src.interface.repository.database.db_repository import user_repository, user_verification_repository

logger = logging.getLogger(__name__)

class UserUsecase:
    """User use case implementation following the Go structure."""

    def __init__(self):
        """Initialize with repositories."""
        # Repositories will be injected later
        self.user_repository = None
        self.user_verification_repository = None
        
        # JWT settings
        self.jwt_secret_key = os.getenv("JWT_SECRET_KEY", "")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.jwt_expiration_minutes = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        
        # Postmark settings
        self.postmark_api_token = os.getenv("POSTMARK_API_TOKEN", "")
        self.postmark_sender_email = os.getenv("POSTMARK_SENDER_EMAIL", "no-reply@example.com")

    async def register_user(self, user_data) -> AuthResponse:
        """
        Register a new user.
        
        Args:
            user_data: User data including email and password
            
        Returns:
            AuthResponse with the created user and access token
        """
        # Check if email already exists
        existing_user = await self.user_repository.get_by_email(user_data.email)
        if existing_user:
            return AuthResponse.error()
        
        # Hash password
        password = user_data.password
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        
        # Create user
        user = User(
            email=user_data.email,
            password_hash=hashed_password.decode('utf-8'),
            first_name=user_data.first_name or "",
            last_name=user_data.last_name or "",
            is_active=True,
            is_admin=False,
        )
        
        # Save user
        created_user = await self.user_repository.create(user)
        
        # Create access token
        access_token = self._create_access_token(str(created_user.id))
        
        return AuthResponse.create(created_user, access_token, None)

    async def user_request_verification(self, email: str) -> VerificationRequestResponse:
        """
        Request email verification for a user.
        
        Args:
            email: User email
            
        Returns:
            VerificationRequestResponse with reference token if successful
        """
        # Check if user exists
        user = await self.user_repository.get_by_email(email)
        if not user:
            return VerificationRequestResponse.error()
        
        # Generate verification code
        verification_code = ''.join(secrets.choice(string.digits) for _ in range(6))
        
        # Store verification code
        success = await self.user_repository.store_verification_code(user.id, verification_code)
        if not success:
            return VerificationRequestResponse.error()
        
        # Send verification email
        email_sent = await self._send_verification_email(email, verification_code)
        if not email_sent:
            return VerificationRequestResponse.error()
        
        # Generate reference token
        reference_token = str(uuid.uuid4())
        
        return VerificationRequestResponse.create(reference_token)

    async def user_verify(self, email: str, code: str) -> VerificationResponse:
        """
        Verify a user with the provided verification code.
        
        Args:
            email: User email
            code: Verification code
            
        Returns:
            Verified user or None if verification fails
        """
        # Check if user exists
        user = await self.user_repository.get_by_email(email)
        if not user:
            return VerificationResponse.error()
        
        # Verify code
        if not await self.user_repository.verify_code(user.id, code):
            return VerificationResponse.error()
        
        # Mark verification as verified
        await self.user_repository.mark_as_verified(user.id)
        
        # Update user verification status
        await self.user_repository.update(user.id, {"is_verified": True})
        
        # Get updated user
        return VerificationResponse.create(await self.user_repository.get_by_id(user.id))

    async def get_user_detail(self, user_id: str) -> ProfileResponse:
        """
        Get detailed user information.
        
        Args:
            user_id: User ID
            
        Returns:
            User or None
        """
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            return ProfileResponse.error()
            
        return ProfileResponse.create(user)

    async def user_authentication(self, token: str) -> Optional[User]:
        """
        Authenticate a user with JWT token.
        
        Args:
            token: JWT access token
            
        Returns:
            Authenticated user or None
        """
        try:
            payload = jwt.decode(token, self.jwt_secret_key, algorithms=[self.jwt_algorithm])
            user_id = payload.get("sub")
            if not user_id:
                return None
            
            # Get user by ID
            user = await self.user_repository.get_by_id(user_id)
            return user
        except jwt.PyJWTError:
            return None

    async def user_login(self, email: str, password: str) -> AuthResponse:
        """
        Login a user.
        
        Args:
            email: Email address
            password: Password
            
        Returns:
            AuthResponse with user, access token, and refresh token, or None if authentication fails
        """
        # Get user by email
        user = await self.user_repository.get_by_email(email)
        if not user:
            return AuthResponse.error()
        
        # Check password
        if not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            return AuthResponse.error()
        
        # Generate token
        access_token = self._create_access_token(str(user.id))
        
        # Store refresh token
        refresh_token = str(uuid.uuid4())
        await self.user_repository.store_refresh_token(user.id, refresh_token)
        
        return AuthResponse.create(user, access_token, refresh_token)

    async def user_refresh_token(self, refresh_token: str) -> RefreshTokenResponse:
        """
        Generate a new access token and refresh token using a refresh token.
        
        Args:
            refresh_token: The refresh token to use
            
        Returns:
            RefreshTokenResponse with user, new access token, and new refresh token, or None values if refresh token is invalid
        """
        # Get user ID from refresh token
        user_id = await self.user_repository.get_user_id_by_refresh_token(refresh_token)
        if not user_id:
            return RefreshTokenResponse.error()
        
        # Get user by ID
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            return RefreshTokenResponse.error()
        
        # Generate a new access token
        access_token = self._create_access_token(user_id)
        
        # Generate and store a new refresh token
        new_refresh_token = str(uuid.uuid4())
        
        # Invalidate the old refresh token
        await self.user_repository.invalidate_refresh_token(refresh_token)
        
        # Store the new refresh token
        await self.user_repository.store_refresh_token(user_id, new_refresh_token)
        
        return RefreshTokenResponse.create(user, access_token, new_refresh_token)

    async def user_logout(self, refresh_token: str) -> bool:
        """
        Logout a user by invalidating their refresh token.
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            True if successful, False otherwise
        """
        return await self.user_repository.invalidate_refresh_token(refresh_token)

    async def reset_password(self, user_id: str, current_password: str, new_password: str) -> PasswordResetResponse:
        """
        Reset a user's password.
        
        Args:
            user_id: User ID
            current_password: Current password
            new_password: New password
            
        Returns:
            PasswordResetResponse indicating success or failure
        """
        # Get user
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            return PasswordResetResponse.error("User not found")
        
        # Check current password
        if not bcrypt.checkpw(current_password.encode('utf-8'), user.password_hash.encode('utf-8')):
            return PasswordResetResponse.error("Current password is incorrect")
        
        # Hash new password
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), salt)
        
        # Update password
        updated_user = await self.user_repository.update(user_id, {
            "password_hash": hashed_password.decode('utf-8')
        })
        
        return PasswordResetResponse.create() if updated_user is not None else PasswordResetResponse.error("Failed to update password")

    async def get_user_profile(self, user_id: str) -> ProfileResponse:
        """
        Get a user's profile information.
        
        Args:
            user_id: ID of the user to retrieve
            
        Returns:
            User object if found, None otherwise
        """
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            return ProfileResponse.error()
            
        return ProfileResponse.create(user)

    def has_permission(self, user: User, permissions: List[str], is_any: bool = False) -> bool:
        """
        Check if a user has the specified permissions.
        
        Args:
            user: User to check
            permissions: List of permission names
            is_any: If True, user only needs one of the permissions, otherwise needs all
            
        Returns:
            True if user has permissions, False otherwise
        """
        # For demo purposes, admin users have all permissions
        if user.is_admin:
            return True
            
        # In a real implementation, we would check against stored user permissions
        # This is a placeholder
        return False

    async def user_login_via_google(self, email: str, token: str, first_name: str = "", last_name: str = "") -> AuthResponse:
        """
        Authenticate a user using Google OAuth.
        
        Args:
            email: Email from Google
            token: Google token for verification
            first_name: First name from Google profile
            last_name: Last name from Google profile
            
        Returns:
            AuthResponse with user, access token, and refresh token or None if authentication fails
        """
        # In a production environment, we would verify the Google token here
        # For demo/testing purposes, we'll trust the token and email
        
        # Check if user exists with this email
        user = await self.user_repository.get_by_email(email)
        
        if user is None:
            # Create new user
            user = User(
                id=None,  # MongoDB will generate
                email=email,
                username=email.split('@')[0],  # Simple username derivation
                password_hash="",  # No password for OAuth users
                first_name=first_name,
                last_name=last_name,
                is_active=True,
                is_admin=False,
                is_verified=True,  # OAuth users are pre-verified
                google_id=token,  # Not ideal, but for demo purposes
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            user = await self.user_repository.create(user)
        
        # Generate token
        access_token = self._create_access_token(str(user.id))
        
        # Store refresh token
        refresh_token = str(uuid.uuid4())
        await self.user_repository.store_refresh_token(user.id, refresh_token)
        
        return AuthResponse.create(user, access_token, refresh_token)

    async def user_login_via_microsoft(self, email: str, token: str, first_name: str = "", last_name: str = "") -> AuthResponse:
        """
        Authenticate a user using Microsoft OAuth.
        
        Args:
            email: Email from Microsoft
            token: Microsoft token for verification
            first_name: First name from Microsoft profile
            last_name: Last name from Microsoft profile
            
        Returns:
            AuthResponse with user, access token, and refresh token or None if authentication fails
        """
        # In a production environment, we would verify the Microsoft token here
        # For demo/testing purposes, we'll trust the token and email
        
        # Check if user exists with this email
        user = await self.user_repository.get_by_email(email)
        
        if user is None:
            # Create new user
            user = User(
                id=None,  # MongoDB will generate
                email=email,
                username=email.split('@')[0],  # Simple username derivation
                password_hash="",  # No password for OAuth users
                first_name=first_name,
                last_name=last_name,
                is_active=True,
                is_admin=False,
                is_verified=True,  # OAuth users are pre-verified
                microsoft_id=token,  # Not ideal, but for demo purposes
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            user = await self.user_repository.create(user)
        
        # Generate token
        access_token = self._create_access_token(str(user.id))
        
        # Store refresh token
        refresh_token = str(uuid.uuid4())
        await self.user_repository.store_refresh_token(user.id, refresh_token)
        
        return AuthResponse.create(user, access_token, refresh_token)

    def _create_access_token(self, user_id: str, additional_claims: Dict[str, Any] = None) -> str:
        """
        Create a JWT access token.
        
        Args:
            user_id: User ID to include in the token
            additional_claims: Additional data to encode in the token
            
        Returns:
            JWT token string
        """
        to_encode = {"sub": user_id}
        if additional_claims:
            to_encode.update(additional_claims)
            
        expire = datetime.utcnow() + timedelta(minutes=self.jwt_expiration_minutes)
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(to_encode, self.jwt_secret_key, algorithm=self.jwt_algorithm)
        return encoded_jwt

    async def _send_verification_email(self, email: str, verification_code: str) -> bool:
        """
        Send a verification email via Postmark.
        
        Args:
            email: Recipient email
            verification_code: Verification code
            
        Returns:
            True if email was sent successfully, False otherwise
        """
        if not self.postmark_api_token:
            # Log that Postmark is not configured
            print("Postmark API token not configured. Skipping email sending.")
            return False
            
        try:
            import requests
            
            url = "https://api.postmarkapp.com/email"
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "X-Postmark-Server-Token": self.postmark_api_token
            }
            payload = {
                "From": self.postmark_sender_email,
                "To": email,
                "Subject": "Verify your email address",
                "HtmlBody": f"""
                <html>
                <body>
                    <h1>Email Verification</h1>
                    <p>Your verification code is: <strong>{verification_code}</strong></p>
                    <p>This code will expire in 24 hours.</p>
                </body>
                </html>
                """,
                "TextBody": f"Your verification code is: {verification_code}. This code will expire in 24 hours.",
                "MessageStream": "outbound"
            }
            
            response = requests.post(url, headers=headers, json=payload)
            return response.status_code == 200
        except Exception as e:
            # Log the error
            print(f"Error sending verification email: {str(e)}")
            return False 