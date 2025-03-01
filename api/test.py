from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "API is working!"}

@app.get("/api/test")
async def test():
    return JSONResponse(content={"status": "ok", "message": "Test endpoint is working!"})

def handler(request, context):
    """Handler for Vercel Serverless Functions"""
    return app(request.scope, request.receive, request.send) 