import torch
import torch.nn as nn
from typing import Dict

class ConversionPredictor(nn.Module):
    """Simple neural network to predict conversion probability"""
    def __init__(self):
        super(ConversionPredictor, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(5, 16),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(16, 8),
            nn.ReLU(),
            nn.Linear(8, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        return self.network(x)

class PredictiveEngine:
    def __init__(self):
        self.model = ConversionPredictor()
        # In production, load pre-trained weights
        # self.model.load_state_dict(torch.load('model_weights.pth'))
        self.model.eval()
    
    def predict_conversion_probability(
        self,
        current_price: float,
        new_price: float,
        market_avg: float,
        floor_price: float,
        customer_type_score: float  # 0.0 = price-sensitive, 1.0 = quality-sensitive
    ) -> float:
        """
        Predict probability of conversion given pricing parameters
        
        Returns: float between 0.0 and 1.0
        """
        # Normalize inputs
        price_drop_pct = (current_price - new_price) / current_price if current_price > 0 else 0
        price_vs_market = (new_price - market_avg) / market_avg if market_avg > 0 else 0
        margin_room = (new_price - floor_price) / floor_price if floor_price > 0 else 0
        
        # Create feature vector
        features = torch.tensor([
            price_drop_pct,
            price_vs_market,
            margin_room,
            customer_type_score,
            1.0 if new_price < market_avg else 0.0  # Below market flag
        ], dtype=torch.float32)
        
        with torch.no_grad():
            probability = self.model(features).item()
        
        return probability
    
    def calculate_heuristic_probability(
        self,
        current_price: float,
        new_price: float,
        market_avg: float,
        customer_type_score: float
    ) -> float:
        """
        Fallback heuristic-based probability calculation
        More interpretable than neural network
        """
        base_probability = 0.3
        
        # Price drop bonus
        if new_price < current_price:
            price_drop_pct = (current_price - new_price) / current_price
            base_probability += price_drop_pct * 0.4
        
        # Market competitiveness bonus
        if new_price < market_avg:
            market_advantage = (market_avg - new_price) / market_avg
            base_probability += market_advantage * 0.3
        
        # Customer type adjustment
        if customer_type_score < 0.5:  # Price-sensitive
            if new_price < market_avg:
                base_probability += 0.2
        else:  # Quality-sensitive
            # Less sensitive to price drops
            base_probability *= 0.8
        
        return min(base_probability, 0.95)
