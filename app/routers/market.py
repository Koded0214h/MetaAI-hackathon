from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.models import Product, CompetitorPrice
from brain.core_logic import PricingAgent
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/market", tags=["market"])

class MarketAnalysisResponse(BaseModel):
    product_id: int
    product_name: str
    current_price: float
    floor_price: float
    market_avg_price: float
    lowest_competitor_price: float
    recommended_strategy: str
    recommended_price: float
    reasoning: str
    conversion_probability: float

@router.get("/analysis/{product_id}", response_model=MarketAnalysisResponse)
def get_market_analysis(
    product_id: int,
    customer_id: Optional[int] = None,
    session: Session = Depends(get_session)
):
    """Get AI-powered market analysis and pricing recommendation"""
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    
    customer = None
    if customer_id:
        from app.models import Customer
        customer = session.get(Customer, customer_id)
    
    agent = PricingAgent()
    decision = agent.make_pricing_decision(session, product, customer)
    
    return MarketAnalysisResponse(
        product_id=product.id,
        product_name=product.name,
        current_price=product.current_price,
        floor_price=product.floor_price,
        market_avg_price=decision["market_data"]["avg"],
        lowest_competitor_price=decision["market_data"]["lowest"],
        recommended_strategy=decision["strategy"],
        recommended_price=decision["recommended_price"],
        reasoning=decision["reasoning"],
        conversion_probability=decision["conversion_probability"]
    )
