from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints.opd import router as opd_router
from app.api.endpoints.renstra_crud import router as renstra_crud_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API Perencanaan Pembangunan RENSTRA (Rencana Strategis Perangkat Daerah) Kota Tegal",
    version="1.0.0",
    root_path=settings.ROOT_PATH,
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for local dev flexibility while supporting explicit settings
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(opd_router, prefix="/api")
app.include_router(renstra_crud_router, prefix="/api")


@app.get("/api/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "app": settings.PROJECT_NAME,
        "tahun_anggaran": settings.TAHUN_ANGGARAN,
        "environment": settings.ENVIRONMENT,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=7878, reload=True)
