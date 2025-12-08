# 🚀 Quick Start Guide - Naira Sniper

## Prerequisites
- Python 3.9+
- Groq API Key (get from https://console.groq.com)

## Installation (5 minutes)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Configure Environment
Edit `.env` file and add your Groq API key:
```bash
GROQ_API_KEY=gsk_your_actual_key_here
DATABASE_URL=sqlite:///./naira_sniper.db
REDIS_URL=redis://localhost:6379/0
```

### Step 3: Start the Server
```bash
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### Step 4: Test the System
Open a new terminal and run:
```bash
python test_system.py
```

## 🎯 Manual Testing

### 1. Open API Docs
Visit: http://localhost:8000/docs

### 2. Add a Product
```bash
curl -X POST http://localhost:8000/product/add \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Oraimo Power Bank 20000mAh",
    "model": "2024 Original",
    "current_price": 15000,
    "floor_price": 13000
  }'
```

Response:
```json
{
  "id": 1,
  "name": "Oraimo Power Bank 20000mAh",
  "model": "2024 Original",
  "current_price": 15000,
  "floor_price": 13000
}
```

### 3. Simulate Price-Sensitive Customer
```bash
curl -X POST http://localhost:8000/webhook/whatsapp \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+2348012345678",
    "message": "How much last? I see am for 14500 on Jiji",
    "customer_name": "Tunde",
    "product_id": 1
  }'
```

Response:
```json
{
  "customer_id": 1,
  "customer_type": "price_sensitive",
  "classification": {
    "customer_type": "price_sensitive",
    "confidence": 0.85,
    "key_signals": ["how much last", "I see am for"]
  }
}
```

### 4. Get AI Recommendation
```bash
curl "http://localhost:8000/market/analysis/1?customer_id=1"
```

Response:
```json
{
  "product_id": 1,
  "product_name": "Oraimo Power Bank 20000mAh",
  "current_price": 15000,
  "floor_price": 13000,
  "market_avg_price": 0,
  "lowest_competitor_price": 0,
  "recommended_strategy": "price_drop",
  "recommended_price": 13000,
  "reasoning": "Price-sensitive customer. Dropped to ₦13000 to compete.",
  "conversion_probability": 0.72
}
```

### 5. Test Quality-Sensitive Customer
```bash
curl -X POST http://localhost:8000/webhook/whatsapp \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+2348087654321",
    "message": "Is it original? Which model? How long e go last?",
    "customer_name": "Chioma",
    "product_id": 1
  }'
```

Then get recommendation:
```bash
curl "http://localhost:8000/market/analysis/1?customer_id=2"
```

Expected: `"recommended_strategy": "value_reinforcement"` (no price drop!)

## 🔍 Verify Database

```bash
# Install SQLite browser or use command line
sqlite3 naira_sniper.db

# Check tables
.tables

# View products
SELECT * FROM product;

# View customers
SELECT * FROM customer;

# View pricing decisions
SELECT * FROM pricingdecision;
```

## 📊 Understanding the Results

### Price-Sensitive Customer Flow
1. Message contains: "how much last", "too cost", "cheaper"
2. System classifies: `customer_type = "price_sensitive"`
3. AI Strategy: `"price_drop"`
4. Action: Lower price (respecting floor price)
5. Message: "Market price dropped! Now ₦X for 4 hours"

### Quality-Sensitive Customer Flow
1. Message contains: "original", "warranty", "which model"
2. System classifies: `customer_type = "quality_sensitive"`
3. AI Strategy: `"value_reinforcement"`
4. Action: Keep price, emphasize quality
5. Message: "Original 2024 model with warranty. Cheaper ones are clones"

## 🐛 Troubleshooting

### Error: "GROQ_API_KEY not found"
- Make sure `.env` file exists
- Check that `GROQ_API_KEY=gsk_...` is set correctly
- Restart the server after editing `.env`

### Error: "Connection refused"
- Make sure server is running: `python main.py`
- Check port 8000 is not in use

### Error: "Module not found"
- Run: `pip install -r requirements.txt`
- Make sure you're in the correct directory

### No AI responses / Fallback logic used
- Check Groq API key is valid
- Check internet connection
- System will use rule-based fallback if AI unavailable

## 🎓 Next Steps

1. **Add Competitor Prices** (manually for now):
```python
from app.models import CompetitorPrice
from app.database import get_session

with next(get_session()) as session:
    price = CompetitorPrice(
        product_id=1,
        source="Jiji",
        price=14500,
        url="https://jiji.ng/..."
    )
    session.add(price)
    session.commit()
```

2. **Monitor Decisions**:
```sql
SELECT 
    p.name,
    pd.old_price,
    pd.new_price,
    pd.strategy,
    pd.conversion_probability,
    pd.reasoning
FROM pricingdecision pd
JOIN product p ON pd.product_id = p.id
ORDER BY pd.created_at DESC;
```

3. **Test Different Scenarios**:
- Customer asks about price multiple times
- Market price drops below floor price
- Multiple customers for same product
- Customer switches from price to quality focus

## 📚 Documentation

- [README.md](README.md) - Project overview
- [ARCHITECTURE.md](ARCHITECTURE.md) - System design
- [QUADRI_README.md](QUADRI_README.md) - Technical deep dive
- API Docs: http://localhost:8000/docs

## 🆘 Need Help?

Check the logs in the terminal where you ran `python main.py`

---

**You're all set! The AI brain is running. Now Abdulrahman needs to connect the scrapers and WhatsApp! 🚀**
