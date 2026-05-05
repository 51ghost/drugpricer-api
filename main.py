"""DrugPricer API — CMS Drug Pricing + FDA NDC Data"""
import os, logging, time, json
from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, HTTPException, Query, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from data_pipeline import DRUGS_DB, search_drugs, get_drug_price, get_formulary, find_alternatives, PLANS_DB

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("drugpricer")

app = FastAPI(title="DrugPricer API", version="1.0.0", description="Real CMS Drug Pricing + FDA NDC database — 200+ drugs with tier pricing, formularies, and alternatives")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

API_KEYS = {os.environ.get("INTERNAL_API_KEY", "demo-key")}

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if request.url.path in ["/health", "/docs", "/openapi.json"]:
        return await call_next(request)
    key = request.headers.get("x-api-key", "")
    if key not in API_KEYS:
        from fastapi.responses import JSONResponse
        return JSONResponse({"detail": "Invalid or missing API key"}, status_code=401)
    return await call_next(request)

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "DrugPricer API", "version": "1.0.0", "drugs_count": len(DRUGS_DB)}

@app.get("/v1/drugs/search")
async def search(q: str = Query("", description="Search drug name or NDC"), limit: int = Query(20, le=100)):
    results = search_drugs(q, limit)
    return {"total": len(results), "results": results}

@app.get("/v1/drugs/{ndc}")
async def drug_detail(ndc: str):
    drug = DRUGS_DB.get(ndc)
    if not drug: raise HTTPException(404, f"Drug NDC {ndc} not found")
    return drug

@app.get("/v1/drugs/{ndc}/price")
async def price(ndc: str, plan_id: str = Query("standard"), pharmacy: str = Query("retail")):
    result = get_drug_price(ndc, plan_id, pharmacy)
    if not result: raise HTTPException(404, f"No pricing for NDC {ndc}")
    return result

@app.get("/v1/formulary/{plan_id}")
async def formulary(plan_id: str, tier: Optional[int] = Query(None)):
    result = get_formulary(plan_id, tier)
    if "error" in result: raise HTTPException(404, result["error"])
    return result

@app.get("/v1/drugs/{ndc}/alternatives")
async def alternatives(ndc: str, plan_id: Optional[str] = Query(None)):
    result = find_alternatives(ndc, plan_id)
    if "error" in result: raise HTTPException(404, result["error"])
    return result

@app.get("/v1/plans")
async def list_plans():
    return {"plans": [{"id": k, "name": v["name"], "type": v["type"]} for k, v in PLANS_DB.items()]}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
