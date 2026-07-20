import os
import keyring
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

# Load .env file if present
load_dotenv()

def get_secret(key_name: str) -> str | None:
    """
    Retrieve a secret, prioritizing the OS credential store (keyring), 
    falling back to environment variables (including .env).
    """
    # 1. Try keyring
    try:
        secret = keyring.get_password("melissa-service", key_name)
        if secret:
            return secret
    except Exception as e:
        logger.warning(f"Failed to access keyring for {key_name}: {e}")
        
    # 2. Try environment variables
    secret = os.environ.get(key_name)
    if secret:
        return secret
        
    return None

def set_secret(key_name: str, value: str):
    """
    Store a secret in the OS credential store.
    """
    try:
        keyring.set_password("melissa-service", key_name, value)
    except Exception as e:
        logger.error(f"Failed to store secret {key_name} in keyring: {e}")
        raise
