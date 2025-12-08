from fastapi import FastAPI
from app.database import create_db_and_tables
from app.routers import products, market, webhooks
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create database tables
    create_db_and_tables()
    yield
    # Shutdown: cleanup if needed

app = FastAPI(
    title="Naira Sniper - Agentic Pricing System",
    description="AI-powered dynamic pricing for Nigerian MSMEs",
    version="1.0.0",
    lifespan=lifespan
)

# Include routers
app.include_router(products.router)
app.include_router(market.router)
app.include_router(webhooks.router)

@app.get("/")
def root():
    return {
        "message": "Naira Sniper API",
        "status": "active",
        "endpoints": {
            "products": "/product",
            "market_analysis": "/market",
            "webhooks": "/webhook"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
