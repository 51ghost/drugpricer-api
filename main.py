"""DrugPricer API — Production FastAPI"""
import os
from fastapi import FastAPI, Header, HTTPException, Query, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

app = FastAPI(title="DrugPricer API", version="1.0.0", docs_url="/docs")
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
INTERNAL_API_KEY = os.environ.get("INTERNAL_API_KEY", "demo-key-change-in-production")

@app.middleware("http")
async def add_cors(request: Request, call_next):
    resp = await call_next(request)
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "x-api-key, content-type"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    return resp

@app.get("/v1/health")
async def health():
    return {"status": "ok", "api": "DrugPricer API", "version": "1.0.0", "ready": True}
