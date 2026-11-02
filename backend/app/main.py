from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.tickets import router as tickets_router
from app.api.routes.auth import router as auth_router
from app.api.routes.users import router as users_router
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

app = FastAPI(
    title="Auvren",
    description="API de triagem inteligente de chamados e automação de suporte.",
    version="0.1.0",
)

# Adicione esta configuração de CORS logo abaixo da criação do 'app'
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Permite o frontend Vite
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Permite todos os cabeçalhos
)
limiter = Limiter(key_func=get_remote_address)

app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)

@app.get("/health", tags=["Monitoramento"])
def health_check():
    return {"status": "healthy", "service": "Auvren"}


app.include_router(tickets_router)
app.include_router(auth_router)
app.include_router(users_router)