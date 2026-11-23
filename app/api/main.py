from fastapi import FastAPI

from app.api import auth, palavras, publicacoes

app = FastAPI(title="Monitor de Publicações", version="0.2.0")
app.include_router(auth.router)
app.include_router(palavras.router)
app.include_router(publicacoes.router)


@app.get("/health", tags=["infra"])
def health():
    return {"status": "ok"}
