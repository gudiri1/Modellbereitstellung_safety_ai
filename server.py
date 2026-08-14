import asyncio
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, Field

app = FastAPI(title="Safety-Critical AI Model Server")

class SensorPayload(BaseModel):
    temperature: float
    pressure: float
    simulate_delay: bool = False  # Ermöglicht das Testen von Timeouts

class ModelResponse(BaseModel):
    status: str
    confidence: float
    action_required: bool

@app.post("/v1/analyze", response_model=ModelResponse)
async def analyze_data(payload: SensorPayload, authorization: str = Header(None)):
    # 1. Simpelste Authentisierungsprüfung
    if not authorization or "Bearer SAFE_TOKEN_123" not in authorization:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # 2. Timeout-Simulation für Client-Tests
    if payload.simulate_delay:
        await asyncio.sleep(3.0) 

    # 3. Die "KI"-Logik (Simuliert die Auswertung des Modells)
    if payload.temperature > 100.0 or payload.pressure > 2.0:
        return ModelResponse(status="RISK", confidence=0.98, action_required=True)
    
    return ModelResponse(status="SAFE", confidence=0.95, action_required=False)
