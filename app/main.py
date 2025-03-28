from fastapi import FastAPI
from app.api.endpoints import health
from app.core.settings import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)
app.include_router(health.router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    """
    Root endpoint with a pointer to API docs.
    """
    return {"message": "Vítejte v Cryptocurrency API. Dokumentaci najdete na /docs."}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
