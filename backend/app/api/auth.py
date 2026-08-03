"""
Authentication Router
======================
Endpoints:
  POST /auth/login  — Accepts username+password, returns JWT access token
  POST /auth/logout — Client-side token discard (stateless)
  GET  /auth/me     — Returns current user profile from token

TODO: Implement login endpoint with user lookup + password verify
"""

from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login")
async def login():
    """TODO: Implement JWT login."""
    raise NotImplementedError


@router.get("/me")
async def me():
    """TODO: Return current user from JWT."""
    raise NotImplementedError
