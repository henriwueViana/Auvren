from fastapi import FastAPI

from app.api.routes.tickets import router as tickets_router
from app.api.routes.auth import router as auth_router
from app.api.routes.users import router as users_router

app = FastAPI(
    title="Auvren",
    description="API de triagem inteligente de chamados e automação de suporte.",
    version="0.1.0",
)


@app.get("/health", tags=["Monitoramento"])
def health_check():
    return {"status": "healthy", "service": "Auvren"}


app.include_router(tickets_router)
app.include_router(auth_router)
app.include_router(users_router)