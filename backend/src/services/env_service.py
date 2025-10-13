import os
from dotenv import load_dotenv

class EnvService:
    """
    Loads environment variables from a .env file and provides access.
    Singleton-like usage recommended.
    """
    _loaded = False

    @classmethod
    def load_env(cls, env_file: str = ".env"):
        if not cls._loaded:
            load_dotenv(env_file)
            cls._loaded = True

    @classmethod
    def get(cls, key: str, default:str)-> str:
        # make sure the function returns a string otherwise throw an error
        
        if not cls._loaded:
            raise RuntimeError("Environment variables not loaded. Call load_env() first.")
        value = os.getenv(key, default)
        if value is None and default is None:
            raise KeyError(f"Environment variable '{key}' not found and no default provided.")
        if value is None:
            return default
        else:
            return value