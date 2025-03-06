import os
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple

import jwt

# Secret keys
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")  # For production, use env var
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


def create_access_token(data: Dict[str, Any]) -> str:
    """
    Create a new JWT access token.
    
    Args:
        data: The data to encode in the token
        
    Returns:
        The encoded JWT token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire.timestamp()})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Create a new JWT refresh token.
    
    Args:
        data: The data to encode in the token
        
    Returns:
        The encoded JWT token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire.timestamp()})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode a JWT token.
    
    Args:
        token: The JWT token to decode
        
    Returns:
        The decoded token data or None if invalid
    """
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None


def create_tokens(user_id: str) -> Tuple[str, str]:
    """
    Create both access and refresh tokens for a user.
    
    Args:
        user_id: The user ID to encode in the tokens
        
    Returns:
        A tuple of (access_token, refresh_token)
    """
    access_token = create_access_token({"sub": user_id})
    refresh_token = create_refresh_token({"sub": user_id})
    return access_token, refresh_token 