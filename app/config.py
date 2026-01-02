import os
from dotenv import load_dotenv

load_dotenv()

CREDENTIALS_PATH = os.getenv(
    "GOOGLE_CREDENTIALS_PATH",
    "app/credentials.json"  # fallback for local dev
)
