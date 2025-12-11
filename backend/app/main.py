"""FastAPI application entry point"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Import API routers
from .api.gold_queries import router as gold_queries_router
from .api.evaluations import router as evaluations_router
from .api.metrics import router as metrics_router
from .api.charts import router as charts_router
from .api.export import router as export_router

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Text-to-SQL Evaluation API",
    description="API for evaluating text-to-SQL model performance",
    version="0.1.0"
)

# Configure CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(gold_queries_router)
app.include_router(evaluations_router)
app.include_router(metrics_router)
app.include_router(charts_router)
app.include_router(export_router)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "Text-to-SQL Evaluation API"}

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}
