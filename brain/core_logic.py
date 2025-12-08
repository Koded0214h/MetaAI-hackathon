from brain.llama_client import LlamaClient
from brain.prompts import SALES_EXPERT_PROMPT
from brain.predictive import PredictiveEngine
from app.models import (
    Product, Customer, CustomerType, Strategy, 
    PricingDecision, CompetitorPrice
)
from sqlmodel import Session, select, func
from typing import Dict, Optional
from datetime import datetime

class PricingAgent:
    """The Core Brain: Dual-Path Pricing Decision Engine"""
    
    def __init__(self):
        self.llama = LlamaClient()
        self.predictor = PredictiveEngine()
    
    def get_market_data(self, session: Session, product_id: int) -> Dict[str, float]:
        """Get average and lowest competitor prices"""
        prices = session.exec(
            select(CompetitorPrice)
            .where(CompetitorPrice.product_id == product_id)
        ).all()
        
        if not prices:
            return {"avg": 0, "lowest": 0}
        
        price_values = [p.price for p in prices]
        return {
            "avg": sum(price_values) / len(price_values),
            "lowest": min(price_values)
        }
    
    def make_pricing_decision(
        self,
        session: Session,
        product: Product,
        customer: Optional[Customer] = None
    ) -> Dict:
        """
        Core decision-making logic
        Returns: {strategy, price, reasoning, message_angle, conversion_prob}
        """
        market_data = self.get_market_data(session, product.id)
        
        customer_type = customer.customer_type if customer else CustomerType.UNKNOWN
        customer_type_str = customer_type.value
        
        # Build prompt for Llama 3
        prompt = SALES_EXPERT_PROMPT.format(
            product_name=product.name,
            current_price=product.current_price,
            floor_price=product.floor_price,
            market_avg_price=market_data["avg"] or product.current_price,
            lowest_competitor_price=market_data["lowest"] or product.current_price,
            customer_type=customer_type_str
        )
        
        # Get AI recommendation
        ai_decision = self.llama.generate_json(prompt)
        
        if not ai_decision:
            # Fallback to rule-based logic
            ai_decision = self._fallback_decision(
                product, market_data, customer_type
            )
        
        # Validate floor price constraint
        recommended_price = ai_decision.get("recommended_price", product.current_price)
        if recommended_price < product.floor_price:
            recommended_price = product.floor_price
            ai_decision["reasoning"] += " (Adjusted to floor price)"
        
        # Calculate conversion probability
        customer_type_score = 0.0 if customer_type == CustomerType.PRICE_SENSITIVE else 1.0
        conversion_prob = self.predictor.calculate_heuristic_probability(
            current_price=product.current_price,
            new_price=recommended_price,
            market_avg=market_data["avg"] or product.current_price,
            customer_type_score=customer_type_score
        )
        
        # Log decision
        decision_log = PricingDecision(
            product_id=product.id,
            customer_id=customer.id if customer else None,
            old_price=product.current_price,
            new_price=recommended_price,
            strategy=Strategy(ai_decision["strategy"]),
            reasoning=ai_decision["reasoning"],
            market_avg_price=market_data["avg"] or 0,
            lowest_competitor_price=market_data["lowest"] or 0,
            conversion_probability=conversion_prob
        )
        session.add(decision_log)
        session.commit()
        
        return {
            "strategy": ai_decision["strategy"],
            "recommended_price": recommended_price,
            "reasoning": ai_decision["reasoning"],
            "message_angle": ai_decision.get("message_angle", ""),
            "conversion_probability": conversion_prob,
            "market_data": market_data
        }
    
    def _fallback_decision(
        self,
        product: Product,
        market_data: Dict,
        customer_type: CustomerType
    ) -> Dict:
        """Rule-based fallback when AI is unavailable"""
        market_avg = market_data["avg"] or product.current_price
        lowest = market_data["lowest"] or product.current_price
        
        if customer_type == CustomerType.PRICE_SENSITIVE:
            # Try to match or beat lowest competitor
            target_price = max(lowest - 100, product.floor_price)
            if target_price < product.current_price:
                return {
                    "strategy": "price_drop",
                    "recommended_price": target_price,
                    "reasoning": f"Price-sensitive customer. Dropped to ₦{target_price} to compete.",
                    "message_angle": "Best price in the market right now"
                }
        
        # Quality-sensitive or unknown: reinforce value
        return {
            "strategy": "value_reinforcement",
            "recommended_price": product.current_price,
            "reasoning": "Maintaining price and emphasizing quality/warranty.",
            "message_angle": "Original product with warranty"
        }
    
    def should_retarget_customer(
        self,
        session: Session,
        customer_id: int,
        product_id: int,
        days_since_inquiry: int = 7
    ) -> bool:
        """Check if customer should be retargeted"""
        from app.models import SalesLog
        from datetime import timedelta
        
        # Find recent inquiries without purchase
        cutoff_date = datetime.utcnow() - timedelta(days=days_since_inquiry)
        
        inquiry = session.exec(
            select(SalesLog)
            .where(SalesLog.customer_id == customer_id)
            .where(SalesLog.product_id == product_id)
            .where(SalesLog.inquiry_date > cutoff_date)
            .where(SalesLog.purchased == False)
        ).first()
        
        return inquiry is not None
