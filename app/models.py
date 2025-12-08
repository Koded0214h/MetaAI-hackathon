from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class CustomerType(str, Enum):
    PRICE_SENSITIVE = "price_sensitive"
    QUALITY_SENSITIVE = "quality_sensitive"
    UNKNOWN = "unknown"

class Strategy(str, Enum):
    PRICE_DROP = "price_drop"
    VALUE_REINFORCEMENT = "value_reinforcement"

class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    model: str
    current_price: float
    floor_price: float  # Cost Price + Minimum Profit
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class CompetitorPrice(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id")
    source: str  # "Jiji", "Jumia", "Instagram"
    price: float
    url: Optional[str] = None
    scraped_at: datetime = Field(default_factory=datetime.utcnow)

class Customer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    phone: str = Field(unique=True, index=True)
    name: Optional[str] = None
    customer_type: CustomerType = Field(default=CustomerType.UNKNOWN)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_interaction: datetime = Field(default_factory=datetime.utcnow)

class CustomerTypeSignal(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    customer_id: int = Field(foreign_key="customer.id")
    signal_text: str
    signal_type: CustomerType
    confidence: float  # 0.0 to 1.0
    detected_at: datetime = Field(default_factory=datetime.utcnow)

class SalesLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    customer_id: int = Field(foreign_key="customer.id")
    product_id: int = Field(foreign_key="product.id")
    inquiry_date: datetime = Field(default_factory=datetime.utcnow)
    purchased: bool = Field(default=False)
    final_price: Optional[float] = None
    purchase_date: Optional[datetime] = None

class PricingDecision(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id")
    customer_id: Optional[int] = Field(default=None, foreign_key="customer.id")
    old_price: float
    new_price: float
    strategy: Strategy
    reasoning: str  # Why this decision was made
    market_avg_price: float
    lowest_competitor_price: float
    conversion_probability: float
    created_at: datetime = Field(default_factory=datetime.utcnow)
