from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1.agreement_routes import router as agreement_router
from api.v1.contract_routes import router as contract_router
import uvicorn

app = FastAPI(
    title="Zé Empresta - Contract API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(agreement_router)
app.include_router(contract_router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5004,
        reload=True,
        access_log=False,
        log_level="info",
        use_colors=False
    )