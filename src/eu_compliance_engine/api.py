from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from eu_compliance_engine.llm_evaluator import evaluate_with_llm

app = FastAPI(title="EU Compliance Engine API")

# Enable CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class EvaluationRequest(BaseModel):
    description: str

@app.post("/evaluate")
async def evaluate_system(request: EvaluationRequest):
    if not request.description:
        raise HTTPException(status_code=400, detail="Description is required")

    try:
        result = evaluate_with_llm(request.description)
        if "error" in result and result.get("is_compliant") is False:
             # Just pass it through so the frontend can display the error niceley
             pass
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
