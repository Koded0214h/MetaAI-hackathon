# 🏗️ Naira Sniper - System Architecture

## 🎯 The Agentic Loop

```
┌─────────────────────────────────────────────────────────────────┐
│                     PHASE 1: WATCHTOWER                         │
│                    (Data Ingestion)                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Scrapers Monitor:                                              │
│  • Jiji.ng → "Oraimo 20000mAh" = ₦14,500                      │
│  • Jumia → "Oraimo 20000mAh" = ₦14,800                         │
│  • Instagram (OCR) → Competitor posts = ₦14,200                │
│                                                                 │
│  Stored in: CompetitorPrice table                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                     PHASE 2: THE BRAIN                          │
│                  (Llama 3 + PyTorch)                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Step 1: Constraint Checking                                    │
│  ├─ Current Price: ₦15,000                                     │
│  ├─ Floor Price: ₦13,000 (HARD LIMIT)                         │
│  ├─ Market Avg: ₦14,500                                        │
│  └─ Lowest Competitor: ₦14,200                                 │
│                                                                 │
│  Step 2: Customer Profiling                                     │
│  ├─ Message: "How much last? Too cost"                         │
│  ├─ Classification: PRICE_SENSITIVE (confidence: 0.85)         │
│  └─ Stored in: CustomerTypeSignal table                        │
│                                                                 │
│  Step 3: Llama 3 Reasoning                                      │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ Prompt:                                                   │ │
│  │ "You are a sales expert. Market avg = ₦14,500.          │ │
│  │  Floor = ₦13,000. Customer is price-sensitive.          │ │
│  │  Should I drop price or reinforce value?"               │ │
│  │                                                           │ │
│  │ Response:                                                 │ │
│  │ {                                                         │ │
│  │   "strategy": "price_drop",                              │ │
│  │   "recommended_price": 13900,                            │ │
│  │   "reasoning": "Customer is price-sensitive and we       │ │
│  │                 have room to drop to ₦13,900 while      │ │
│  │                 staying above floor price",              │ │
│  │   "message_angle": "Best price in market right now"      │ │
│  │ }                                                         │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  Step 4: PyTorch Prediction                                     │
│  ├─ Input Features:                                             │
│  │  • Price drop %: 7.3%                                       │
│  │  • Price vs market: -4.1% (below average)                  │
│  │  • Margin room: 6.9%                                        │
│  │  • Customer type: 0.0 (price-sensitive)                    │
│  │  • Below market flag: 1.0                                   │
│  │                                                             │
│  └─ Output: Conversion Probability = 78%                       │
│                                                                 │
│  Stored in: PricingDecision table (audit log)                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                     PHASE 3: THE ATTACK                         │
│                   (WhatsApp CRM)                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Step 1: Catalog Update                                         │
│  └─ WhatsApp Business Catalog: ₦15,000 → ₦13,900             │
│                                                                 │
│  Step 2: Find Targets                                           │
│  Query: Customers who:                                          │
│  ├─ Asked about this product                                   │
│  ├─ Within last 7 days                                         │
│  └─ Did NOT purchase                                           │
│                                                                 │
│  Step 3: Smart Retargeting                                      │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ For PRICE-SENSITIVE customers:                            │ │
│  │                                                           │ │
│  │ "Hello Tunde!                                             │ │
│  │                                                           │ │
│  │ Good news! Market price dropped today.                    │ │
│  │                                                           │ │
│  │ Oraimo Power Bank 20000mAh                                │ │
│  │ Now ₦13,900 (was ₦15,000)                               │ │
│  │                                                           │ │
│  │ This offer is valid for the next 4 hours.                │ │
│  │ Let me reserve one for you?"                             │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ For QUALITY-SENSITIVE customers:                          │ │
│  │                                                           │ │
│  │ "Hello Chioma!                                            │ │
│  │                                                           │ │
│  │ Oraimo Power Bank 20000mAh - ₦15,000                    │ │
│  │                                                           │ │
│  │ This is the original 2024 model with 6-month warranty.   │ │
│  │ Cheaper ones you're seeing are mostly old stock or       │ │
│  │ clones. This is why our price stays at ₦15,000.         │ │
│  │                                                           │ │
│  │ Available now. Should I reserve one for you?"            │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 🗄️ Database Schema

```sql
-- Products with floor price constraint
CREATE TABLE product (
    id INTEGER PRIMARY KEY,
    name VARCHAR NOT NULL,
    model VARCHAR,
    current_price FLOAT NOT NULL,
    floor_price FLOAT NOT NULL,  -- NEVER go below this
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Market intelligence
CREATE TABLE competitorprice (
    id INTEGER PRIMARY KEY,
    product_id INTEGER REFERENCES product(id),
    source VARCHAR,  -- "Jiji", "Jumia", "Instagram"
    price FLOAT,
    url VARCHAR,
    scraped_at TIMESTAMP
);

-- Customer profiles
CREATE TABLE customer (
    id INTEGER PRIMARY KEY,
    phone VARCHAR UNIQUE NOT NULL,
    name VARCHAR,
    customer_type VARCHAR,  -- "price_sensitive", "quality_sensitive", "unknown"
    created_at TIMESTAMP,
    last_interaction TIMESTAMP
);

-- Behavioral signals
CREATE TABLE customertypesignal (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER REFERENCES customer(id),
    signal_text VARCHAR,
    signal_type VARCHAR,
    confidence FLOAT,  -- 0.0 to 1.0
    detected_at TIMESTAMP
);

-- Sales tracking
CREATE TABLE saleslog (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER REFERENCES customer(id),
    product_id INTEGER REFERENCES product(id),
    inquiry_date TIMESTAMP,
    purchased BOOLEAN DEFAULT FALSE,
    final_price FLOAT,
    purchase_date TIMESTAMP
);

-- Audit trail
CREATE TABLE pricingdecision (
    id INTEGER PRIMARY KEY,
    product_id INTEGER REFERENCES product(id),
    customer_id INTEGER REFERENCES customer(id),
    old_price FLOAT,
    new_price FLOAT,
    strategy VARCHAR,  -- "price_drop", "value_reinforcement"
    reasoning TEXT,
    market_avg_price FLOAT,
    lowest_competitor_price FLOAT,
    conversion_probability FLOAT,
    created_at TIMESTAMP
);
```

## 🔄 API Flow

### 1. Product Management
```http
POST /product/add
{
  "name": "Oraimo Power Bank 20000mAh",
  "model": "2024",
  "current_price": 15000,
  "floor_price": 13000
}
```

### 2. WhatsApp Webhook (Incoming Message)
```http
POST /webhook/whatsapp
{
  "phone": "+2348012345678",
  "message": "How much last? Too cost",
  "customer_name": "Tunde",
  "product_id": 1
}

Response:
{
  "customer_id": 1,
  "customer_type": "price_sensitive",
  "classification": {
    "customer_type": "price_sensitive",
    "confidence": 0.85,
    "key_signals": ["how much last", "too cost"]
  }
}
```

### 3. Get AI Recommendation
```http
GET /market/analysis/1?customer_id=1

Response:
{
  "product_id": 1,
  "product_name": "Oraimo Power Bank 20000mAh",
  "current_price": 15000,
  "floor_price": 13000,
  "market_avg_price": 14500,
  "lowest_competitor_price": 14200,
  "recommended_strategy": "price_drop",
  "recommended_price": 13900,
  "reasoning": "Customer is price-sensitive...",
  "conversion_probability": 0.78
}
```

## 🧠 AI Components

### 1. Customer Profiler (brain/profiler.py)
**Input**: Customer message  
**Output**: Classification + confidence

```python
profiler = CustomerProfiler()
result = profiler.classify_message("How much last? Too cost")

# Result:
{
  "customer_type": "price_sensitive",
  "confidence": 0.85,
  "key_signals": ["how much last", "too cost"]
}
```

### 2. Pricing Agent (brain/core_logic.py)
**Input**: Product + Customer + Market Data  
**Output**: Strategy + Price + Reasoning

```python
agent = PricingAgent()
decision = agent.make_pricing_decision(session, product, customer)

# Decision:
{
  "strategy": "price_drop",
  "recommended_price": 13900,
  "reasoning": "...",
  "conversion_probability": 0.78
}
```

### 3. Predictive Engine (brain/predictive.py)
**Input**: Pricing parameters  
**Output**: Conversion probability

```python
predictor = PredictiveEngine()
prob = predictor.calculate_heuristic_probability(
    current_price=15000,
    new_price=13900,
    market_avg=14500,
    customer_type_score=0.0  # price-sensitive
)
# prob = 0.78
```

## 🚀 Deployment Checklist

### Quadri's Checklist ✅
- [x] Database models (7 tables)
- [x] Llama 3 client (Groq API)
- [x] Customer profiler
- [x] PyTorch predictor
- [x] Core pricing logic
- [x] FastAPI endpoints
- [x] Test suite

### Abdulrahman's Checklist 🚧
- [ ] Jiji scraper
- [ ] Jumia scraper
- [ ] Instagram OCR
- [ ] WhatsApp Business API
- [ ] Celery workers
- [ ] Redis setup
- [ ] Message templates
- [ ] Catalog sync

## 📊 Success Metrics

1. **Conversion Rate**: % of retargeted customers who purchase
2. **Price Optimization**: Average margin maintained vs sales volume
3. **Customer Classification Accuracy**: % correctly identified
4. **Response Time**: Time from market change to customer message
5. **Profit Protection**: % of decisions respecting floor price

---

**The system is LIVE and ready for integration! 🎉**
