#!/usr/bin/env python3
"""
Debug script to test token encoding/decoding
"""

import sys
import os

# Print Python path
print(f"Current directory: {os.getcwd()}")
print(f"Python path: {sys.path}")

try:
    from app.core.security import TokenManager
    from app.core.config import settings
except Exception as e:
    print(f"ERROR importing: {e}")
    sys.exit(1)

print("=" * 70)
print("TOKEN ENCODING/DECODING DEBUG")
print("=" * 70)

print(f"\nSettings:")
print(f"  SECRET_KEY: {settings.SECRET_KEY[:30]}...")
print(f"  ALGORITHM: {settings.ALGORITHM}")
print(f"  ACCESS_TOKEN_EXPIRE_MINUTES: {settings.ACCESS_TOKEN_EXPIRE_MINUTES}")

try:
    # Test 1: Create a token with string sub (JWT spec requirement)
    print(f"\n[1] Creating token with string 'sub'...")
    test_data = {"sub": "5"}  # String, not integer
    token = TokenManager.create_access_token(test_data)
    print(f"Token created: {token[:50]}...")

    # Test 2: Decode the token
    print(f"\n[2] Decoding token immediately...")
    try:
        decoded = TokenManager.decode_token(token)
        print(f"Token decoded successfully!")
        print(f"Payload: {decoded}")
    except Exception as e:
        print(f"ERROR decoding token: {e}")
        import traceback
        traceback.print_exc()

    # Test 3: Get user ID from token
    print(f"\n[3] Extracting user ID from token...")
    user_id = TokenManager.get_user_id_from_token(token)
    print(f"User ID: {user_id}")

    # Test 4: Check if token is expired
    print(f"\n[4] Checking if token is expired...")
    is_expired = TokenManager.is_token_expired(token)
    print(f"Is expired: {is_expired}")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
