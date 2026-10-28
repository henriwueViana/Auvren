
from fastapi import FastAPI

from app.api.routes.tickets import router as tickets_router

app = FastAPI(
    title="TriaArch IA",
    description="API de triagem inteligente de chamados de suporte técnico.",
    version="0.1.0",
)


@app.get("/health", tags=["Monitoramento"])
def health_check():
    return {
        "status": "healthy",
        "service": "TriaArch IA",
    }


app.include_router(tickets_router)
