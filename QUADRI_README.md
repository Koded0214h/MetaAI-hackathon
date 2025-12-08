# Naira Sniper - Quadri's Core Architecture

## 🧠 What I Built (The Brain & Skeleton)

### 1. Database Models (`app/models.py`)
Complete SQLModel schema with 7 tables:
- **Product**: Stores items with floor_price constraint
- **CompetitorPrice**: Market data from scrapers
- **Customer**: User profiles with CustomerType classification
- **CustomerTypeSignal**: Tracks price/quality sensitivity signals
- **SalesLog**: Inquiry and purchase tracking
- **PricingDecision**: Audit log of all AI decisions

### 2. The Brain (`brain/` folder)

#### `llama_client.py`
- Groq API wrapper for Llama 3.1-70B
- JSON response parsing with fallback handling

#### `prompts.py`
- **SALES_EXPERT_PROMPT**: Instructs Llama to choose price_drop vs value_reinforcement
- **INTENT_CLASSIFIER_PROMPT**: Classifies customer messages
- Message templates for WhatsApp

#### `profiler.py` - CustomerProfiler
- Analyzes messages for price/quality signals
- Updates customer type based on 30-day signal history
- Fallback keyword matching when AI unavailable

#### `predictive.py` - PredictiveEngine
- PyTorch neural network for conversion probability
- Heuristic fallback calculation
- Considers: price drop %, market position, customer type

#### `core_logic.py` - PricingAgent (THE CORE)
- **make_pricing_decision()**: Main orchestrator
  - Fetches market data
  - Calls Llama 3 with context
  - Enforces floor_price constraint
  - Calculates conversion probability
  - Logs decision to database
- **should_retarget_customer()**: Identifies ghosted customers

### 3. API Endpoints (`app/routers/`)

#### Products Router
- `POST /product/add` - Add product with floor price
- `GET /product/list` - List all products
- `GET /product/{id}` - Get specific product

#### Market Router
- `GET /market/analysis/{product_id}?customer_id=X`
  - Returns AI recommendation
  - Strategy (price_drop or value_reinforcement)
  - Recommended price
  - Conversion probability

#### Webhooks Router
- `POST /webhook/whatsapp` - Process incoming messages
  - Creates/updates customer
  - Classifies customer type
  - Logs sales inquiry
- `POST /webhook/customer/signal` - Manual signal storage

### 4. Main Application (`main.py`)
- FastAPI app with lifespan management
- Auto-creates database on startup
- All routers included

## 🚀 How to Run

```bash
# Install dependencies
pip install -r requirements.txt

# Set your Groq API key in .env
GROQ_API_KEY=your_key_here

# Run the server
python main.py
```

Server runs on `http://localhost:8000`
Docs at `http://localhost:8000/docs`

## 🧪 Test Flow

1. **Add a product**:
```bash
curl -X POST http://localhost:8000/product/add \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Oraimo Power Bank 20000mAh",
    "model": "2024",
    "current_price": 15000,
    "floor_price": 13000
  }'
```

2. **Simulate WhatsApp message** (price-sensitive):
```bash
curl -X POST http://localhost:8000/webhook/whatsapp \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+2348012345678",
    "message": "How much last? I see am for 14500 for Jiji",
    "customer_name": "Tunde",
    "product_id": 1
  }'
```

3. **Get AI recommendation**:
```bash
curl http://localhost:8000/market/analysis/1?customer_id=1
```

Response will show:
- Strategy: "price_drop" (because customer is price-sensitive)
- Recommended price
- Reasoning from Llama 3
- Conversion probability

## 🔗 Integration Points for Abdulrahman

### What You Need to Build:

1. **Scraper** → Populate `CompetitorPrice` table
```python
from app.models import CompetitorPrice
# Insert scraped prices
```

2. **WhatsApp Sender** → Use decisions from `/market/analysis`
```python
decision = requests.get(f"/market/analysis/{product_id}?customer_id={cust_id}")
if decision["recommended_strategy"] == "price_drop":
    send_price_drop_message(...)
else:
    send_value_message(...)
```

3. **Celery Tasks** → Periodic market checks
```python
@celery.task
def check_market_prices():
    # Scrape competitors
    # Call PricingAgent for each product
    # Send retargeting messages
```

## 📊 Database Schema

```
Product
├── id, name, model
├── current_price
└── floor_price (CONSTRAINT)

Customer
├── id, phone, name
├── customer_type (ENUM: price_sensitive, quality_sensitive, unknown)
└── last_interaction

CustomerTypeSignal
├── customer_id (FK)
├── signal_text
├── signal_type
└── confidence (0.0-1.0)

PricingDecision (Audit Log)
├── product_id, customer_id
├── old_price → new_price
├── strategy (price_drop / value_reinforcement)
├── reasoning (from Llama 3)
└── conversion_probability
```

## 🎯 Key Features Implemented

✅ Dual-path reasoning (price vs quality strategy)
✅ Floor price constraint enforcement
✅ Customer profiling with signal tracking
✅ Llama 3 integration via Groq
✅ PyTorch conversion prediction
✅ Complete audit trail
✅ RESTful API with FastAPI
✅ SQLModel ORM with type safety

## 🔥 Next Steps (For You, Abdulrahman)

1. Build scrapers in `engine/scrapers.py`
2. WhatsApp Business API integration in `engine/whatsapp.py`
3. Celery workers in `engine/workers.py`
4. OCR for Instagram in `engine/ocr.py`

The brain is ready. Now we need the eyes (scrapers) and mouth (WhatsApp)! 🚀
