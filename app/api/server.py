# app/api/server.py
# Minimal entry for uvicorn to run
from app.api.routes import app

# Run with: uvicorn app.api.server:app --reload
