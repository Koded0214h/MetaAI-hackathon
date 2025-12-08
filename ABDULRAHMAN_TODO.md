# 🎯 Abdulrahman's Integration Guide

## Your Mission
Connect the **EYES** (scrapers) and **MOUTH** (WhatsApp) to Quadri's **BRAIN** (AI logic).

The brain is ready and waiting for your data! 🧠✅

---

## 📋 Your Checklist

### 1. Web Scrapers (`engine/scrapers.py`)

#### Jiji Scraper
```python
from playwright.sync_api import sync_playwright
from app.models import CompetitorPrice
from app.database import get_session
from datetime import datetime

def scrape_jiji(product_name: str, product_id: int):
    """
    Scrape Jiji.ng for product prices
    
    Target: https://jiji.ng/search?query=oraimo+power+bank
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Search for product
        search_url = f"https://jiji.ng/search?query={product_name.replace(' ', '+')}"
        page.goto(search_url)
        
        # Extract prices (adjust selectors based on actual HTML)
        listings = page.query_selector_all('.listing-item')
        
        with next(get_session()) as session:
            for listing in listings[:10]:  # Top 10 results
                try:
                    price_text = listing.query_selector('.price').inner_text()
                    price = float(price_text.replace('₦', '').replace(',', ''))
                    url = listing.query_selector('a').get_attribute('href')
                    
                    # Save to database
                    competitor_price = CompetitorPrice(
                        product_id=product_id,
                        source="Jiji",
                        price=price,
                        url=url,
                        scraped_at=datetime.utcnow()
                    )
                    session.add(competitor_price)
                except Exception as e:
                    print(f"Error parsing listing: {e}")
            
            session.commit()
        
        browser.close()

# TODO: Add similar functions for:
# - scrape_jumia()
# - scrape_instagram_ocr()
```

**Key Points**:
- Use Playwright for JavaScript-heavy sites
- Handle CAPTCHAs (use proxies if needed)
- Rotate User-Agents
- Store results in `CompetitorPrice` table
- Run every 30 minutes via Celery

---

### 2. WhatsApp Integration (`engine/whatsapp.py`)

#### Setup Meta Developer Account
1. Go to https://developers.facebook.com
2. Create app → WhatsApp Business
3. Get Phone Number ID and Access Token
4. Add to `.env`:
```bash
WHATSAPP_PHONE_ID=your_phone_id
WHATSAPP_ACCESS_TOKEN=your_token
```

#### Send Messages
```python
import requests
import os
from brain.prompts import PRICE_DROP_TEMPLATE, VALUE_REINFORCEMENT_TEMPLATE

def send_whatsapp_message(phone: str, message: str):
    """Send WhatsApp message via Meta API"""
    url = f"https://graph.facebook.com/v18.0/{os.getenv('WHATSAPP_PHONE_ID')}/messages"
    
    headers = {
        "Authorization": f"Bearer {os.getenv('WHATSAPP_ACCESS_TOKEN')}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "text",
        "text": {"body": message}
    }
    
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def send_price_drop_alert(customer_phone: str, customer_name: str, 
                          product_name: str, old_price: float, 
                          new_price: float, hours: int = 4):
    """Send price drop message"""
    message = PRICE_DROP_TEMPLATE.format(
        customer_name=customer_name,
        product_name=product_name,
        new_price=new_price,
        old_price=old_price,
        hours=hours
    )
    return send_whatsapp_message(customer_phone, message)

def send_value_message(customer_phone: str, customer_name: str,
                       product_name: str, price: float, 
                       model_year: str = "2024", 
                       warranty: str = "6-month",
                       extra_value: str = "Free delivery within Lagos"):
    """Send value reinforcement message"""
    message = VALUE_REINFORCEMENT_TEMPLATE.format(
        customer_name=customer_name,
        product_name=product_name,
        price=price,
        model_year=model_year,
        warranty=warranty,
        extra_value=extra_value
    )
    return send_whatsapp_message(customer_phone, message)

def update_whatsapp_catalog(product_id: int, new_price: float):
    """Update WhatsApp Business Catalog"""
    # TODO: Implement catalog API
    # https://developers.facebook.com/docs/whatsapp/cloud-api/guides/sell-products-and-services
    pass
```

---

### 3. Celery Workers (`engine/workers.py`)

#### Setup Celery
```python
from celery import Celery
from app.database import get_session
from app.models import Product, Customer, SalesLog
from brain.core_logic import PricingAgent
from engine.scrapers import scrape_jiji, scrape_jumia
from engine.whatsapp import send_price_drop_alert, send_value_message
from datetime import datetime, timedelta
from sqlmodel import select

# Initialize Celery
celery_app = Celery('naira_sniper', broker='redis://localhost:6379/0')

@celery_app.task
def scrape_all_products():
    """Run scrapers for all products"""
    with next(get_session()) as session:
        products = session.exec(select(Product)).all()
        
        for product in products:
            try:
                scrape_jiji(product.name, product.id)
                scrape_jumia(product.name, product.id)
            except Exception as e:
                print(f"Error scraping {product.name}: {e}")

@celery_app.task
def retarget_ghosted_customers():
    """Find and retarget customers who didn't buy"""
    agent = PricingAgent()
    
    with next(get_session()) as session:
        # Find inquiries from last 7 days without purchase
        cutoff = datetime.utcnow() - timedelta(days=7)
        
        inquiries = session.exec(
            select(SalesLog)
            .where(SalesLog.inquiry_date > cutoff)
            .where(SalesLog.purchased == False)
        ).all()
        
        for inquiry in inquiries:
            customer = session.get(Customer, inquiry.customer_id)
            product = session.get(Product, inquiry.product_id)
            
            # Get AI recommendation
            decision = agent.make_pricing_decision(session, product, customer)
            
            # Send appropriate message
            if decision["strategy"] == "price_drop":
                send_price_drop_alert(
                    customer.phone,
                    customer.name or "Customer",
                    product.name,
                    product.current_price,
                    decision["recommended_price"]
                )
            else:
                send_value_message(
                    customer.phone,
                    customer.name or "Customer",
                    product.name,
                    product.current_price
                )

# Schedule tasks
celery_app.conf.beat_schedule = {
    'scrape-every-30-minutes': {
        'task': 'engine.workers.scrape_all_products',
        'schedule': 1800.0,  # 30 minutes
    },
    'retarget-every-hour': {
        'task': 'engine.workers.retarget_ghosted_customers',
        'schedule': 3600.0,  # 1 hour
    },
}
```

#### Run Celery
```bash
# Terminal 1: Start worker
celery -A engine.workers worker --loglevel=info

# Terminal 2: Start beat scheduler
celery -A engine.workers beat --loglevel=info
```

---

### 4. Instagram OCR (`engine/ocr.py`)

```python
from PIL import Image
import pytesseract
import re

def extract_price_from_image(image_path: str) -> float:
    """
    Extract price from Instagram screenshot using OCR
    
    Example: Image contains "₦14,500" or "N14500"
    """
    try:
        # Open image
        img = Image.open(image_path)
        
        # Extract text
        text = pytesseract.image_to_string(img)
        
        # Find price patterns
        patterns = [
            r'₦\s*(\d{1,3}(?:,\d{3})*)',  # ₦14,500
            r'N\s*(\d{1,3}(?:,\d{3})*)',   # N14500
            r'(\d{1,3}(?:,\d{3})*)\s*naira' # 14500 naira
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                price_str = match.group(1).replace(',', '')
                return float(price_str)
        
        return None
    except Exception as e:
        print(f"OCR Error: {e}")
        return None

def monitor_instagram_competitor(username: str, product_id: int):
    """
    Monitor competitor's Instagram for price posts
    
    TODO: Implement Instagram scraping
    - Use instaloader or similar
    - Download recent posts
    - Run OCR on images
    - Store prices in CompetitorPrice table
    """
    pass
```

---

## 🔗 Integration Points

### How to Use Quadri's Brain

#### 1. After Scraping, Trigger Analysis
```python
from brain.core_logic import PricingAgent
from app.database import get_session

# After you populate CompetitorPrice table
with next(get_session()) as session:
    agent = PricingAgent()
    product = session.get(Product, product_id)
    customer = session.get(Customer, customer_id)
    
    # Get AI decision
    decision = agent.make_pricing_decision(session, product, customer)
    
    # Use the decision
    if decision["strategy"] == "price_drop":
        # Send price drop message
        send_price_drop_alert(...)
    else:
        # Send value message
        send_value_message(...)
```

#### 2. Process Incoming WhatsApp Messages
```python
# Your webhook receives message from Meta
@app.post("/webhook/whatsapp/incoming")
def handle_incoming_message(data: dict):
    phone = data["from"]
    message = data["text"]["body"]
    
    # Forward to Quadri's endpoint
    response = requests.post("http://localhost:8000/webhook/whatsapp", json={
        "phone": phone,
        "message": message,
        "product_id": extract_product_id(message)  # Your logic
    })
    
    # Response contains customer_type classification
    return response.json()
```

---

## 📦 Dependencies to Add

```bash
pip install playwright
pip install celery[redis]
pip install pytesseract
pip install pillow
pip install instaloader  # For Instagram
```

---

## 🧪 Testing Your Work

### Test Scraper
```python
from engine.scrapers import scrape_jiji

# Should populate CompetitorPrice table
scrape_jiji("Oraimo Power Bank 20000mAh", product_id=1)

# Verify
from app.database import get_session
from app.models import CompetitorPrice
from sqlmodel import select

with next(get_session()) as session:
    prices = session.exec(
        select(CompetitorPrice).where(CompetitorPrice.product_id == 1)
    ).all()
    print(f"Found {len(prices)} competitor prices")
```

### Test WhatsApp
```python
from engine.whatsapp import send_whatsapp_message

send_whatsapp_message("+2348012345678", "Test message from Naira Sniper!")
```

### Test Full Flow
```python
# 1. Scrape prices
scrape_jiji("Oraimo Power Bank", 1)

# 2. Get AI decision
decision = agent.make_pricing_decision(session, product, customer)

# 3. Send message
if decision["strategy"] == "price_drop":
    send_price_drop_alert(...)
```

---

## 🎯 Priority Order

1. **WhatsApp Sending** (High Priority)
   - Get messages flowing out
   - Test with your own number first

2. **Jiji Scraper** (High Priority)
   - Most popular Nigerian marketplace
   - Provides market intelligence

3. **Celery Workers** (Medium Priority)
   - Automate the retargeting
   - Run scrapers periodically

4. **Jumia Scraper** (Medium Priority)
   - Additional market data

5. **Instagram OCR** (Low Priority)
   - Nice to have
   - More complex

---

## 🆘 Need Help?

**Quadri's endpoints are ready:**
- `POST /webhook/whatsapp` - Process messages
- `GET /market/analysis/{product_id}` - Get AI decisions
- `POST /product/add` - Add products

**Database tables are ready:**
- `CompetitorPrice` - Store your scraped prices
- `Customer` - Auto-created from WhatsApp messages
- `PricingDecision` - Auto-logged by the brain

**The brain is waiting for your data! Feed it and watch it work! 🚀**
