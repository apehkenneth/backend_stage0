# app/main.py
import os
import logging
from datetime import datetime, timezone

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()

# Basic config with safe defaults
EMAIL = os.getenv("APP_EMAIL")
NAME = os.getenv("APP_NAME")
STACK = os.getenv("APP_STACK")
CATFACT_URL = os.getenv("CATFACT_URL")
CATFACT_TIMEOUT = float(os.getenv("CATFACT_TIMEOUT"))

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("backend-stage0")

app = FastAPI(title="HNG13 Backend Stage 0 - Profile Endpoint")

# Configure CORS (allow GET requests from anywhere)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

async def fetch_cat_fact(timeout: float = CATFACT_TIMEOUT) -> str:
    """
    Fetch a random cat fact from the external API.
    Returns a fallback string if the request fails.
    """
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(CATFACT_URL)
            resp.raise_for_status()
            data = resp.json()
            fact = data.get("fact")
            if not isinstance(fact, str) or not fact.strip():
                raise ValueError("Invalid fact in API response.")
            return fact.strip()
    except Exception as exc:
        logger.warning("Failed to fetch cat fact: %s", exc)
        return "Could not fetch a cat fact at the moment."

@app.get("/me")
async def me():
    """
    GET /me - Return profile + dynamic cat fact + current UTC timestamp.
    """
    fact = await fetch_cat_fact()
    response_payload = {
        "status": "success",
        "user": {
            "email": EMAIL,
            "name": NAME,
            "stack": STACK,
        },
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "fact": fact,
    }
    return JSONResponse(content=response_payload, status_code=status.HTTP_200_OK)
