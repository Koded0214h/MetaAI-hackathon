# MetaAI-hackathon

# 🎯 Naira Sniper - Agentic Pricing System for Nigerian MSMEs

## The Problem
Nigerian vendors lose millions daily because they:
- Don't know market prices in real-time
- Can't identify if customers are price-sensitive or quality-focused
- Use rigid pricing that kills conversions

## The Solution
An AI agent that:
1. **Monitors** competitor prices 24/7
2. **Profiles** customers (price vs quality sensitive)
3. **Decides** autonomously: drop price OR reinforce value
4. **Retargets** ghosted customers via WhatsApp

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    NAIRA SNIPER SYSTEM                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐      ┌──────────────┐                   │
│  │   SCRAPERS   │─────▶│  COMPETITOR  │                   │
│  │ (Abdulrahman)│      │    PRICES    │                   │
│  └──────────────┘      └──────┬───────┘                   │
│                               │                            │
│                               ▼                            │
│  ┌──────────────┐      ┌──────────────┐                   │
│  │   WHATSAPP   │◀─────│  PRICING     │◀──── Llama 3     │
│  │   MESSAGES   │      │   AGENT      │      (Groq)       │
│  │ (Abdulrahman)│      │  (Quadri)    │                   │
│  └──────────────┘      └──────┬───────┘                   │
│         │                     │                            │
│         ▼                     ▼                            │
│  ┌──────────────┐      ┌──────────────┐                   │
│  │   CUSTOMER   │      │  PYTORCH     │                   │
│  │   PROFILER   │      │  PREDICTOR   │                   │
│  │  (Quadri)    │      │  (Quadri)    │                   │
│  └──────────────┘      └──────────────┘                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Add your GROQ_API_KEY

# Run server
python main.py

# Test system (in another terminal)
python test_system.py
```

## 📁 Project Structure

```
naira-sniper/
├── brain/              # 🧠 Quadri's Domain - AI Logic
│   ├── core_logic.py   # Main pricing decision engine
│   ├── llama_client.py # Groq/Llama 3 wrapper
│   ├── profiler.py     # Customer type classifier
│   ├── predictive.py   # PyTorch conversion predictor
│   └── prompts.py      # AI prompts & templates
│
├── app/                # 🏗️ Quadri's Domain - Architecture
│   ├── database.py     # SQLModel setup
│   ├── models.py       # Database schema (7 tables)
│   └── routers/        # FastAPI endpoints
│       ├── products.py
│       ├── market.py
│       └── webhooks.py
│
├── engine/             # ⚙️ Abdulrahman's Domain
│   ├── scrapers.py     # Jiji/Jumia/Instagram scrapers
│   ├── whatsapp.py     # WhatsApp Business API
│   ├── workers.py      # Celery background tasks
│   └── ocr.py          # Instagram price extraction
│
└── main.py             # FastAPI application entry
```

## 🎯 Key Features

### ✅ Implemented (Quadri)
- Dual-path AI reasoning (price drop vs value reinforcement)
- Customer profiling with signal tracking
- Llama 3 integration via Groq API
- PyTorch conversion probability prediction
- Floor price constraint enforcement
- Complete audit trail
- RESTful API with FastAPI

### 🚧 In Progress (Abdulrahman)
- Web scrapers (Jiji, Jumia)
- WhatsApp Business integration
- Celery task queue
- Instagram OCR

## 📚 Documentation

- [Quadri's Architecture Guide](QUADRI_README.md) - Detailed technical docs
- API Docs: `http://localhost:8000/docs` (when server running)

## 🤝 Team

**Quadri** - Systems Architect & AI Engineer  
Built: Brain (AI logic), Database, API skeleton

**Abdulrahman** - DevOps & Integration Engineer  
Building: Scrapers, WhatsApp, Task Queue, OCR

## 📊 Example Flow

1. Customer: "How much last? I see am for 14,500 on Jiji"
2. System classifies: **Price-Sensitive**
3. AI checks: Market avg = ₦14,000, Floor = ₦13,000
4. Decision: **Price Drop** to ₦13,900
5. WhatsApp: "Market price dropped! Now ₦13,900 for 4 hours"
6. Conversion probability: **78%**

---

**Built for Meta AI Hackathon 2024** 🚀