from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, upload, search, parse, rag, metrics

app = FastAPI(
    title="VerdictVault",
    description="AI-powered legal precedent extractor",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(upload.router, prefix="/api/upload", tags=["document_upload"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(parse.router, prefix="/api/parse", tags=["document_parsing"])
app.include_router(rag.router, prefix="/api/rag", tags=["rag_inference"])
app.include_router(metrics.router, prefix="/api/metrics", tags=["metrics"])

@app.get("/")
async def root():
    return {"message": "VerdictVault API", "status": "operational"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}