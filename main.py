from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "DrillFlow API is running"}

@app.get("/health")
async def health_check():
    return {"status": "ok"} 