"""
Quick test script to verify the core system works
Run after starting the server: python main.py
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_add_product():
    print("\n1️⃣ Adding product...")
    response = requests.post(f"{BASE_URL}/product/add", json={
        "name": "Oraimo Power Bank 20000mAh",
        "model": "2024 Original",
        "current_price": 15000,
        "floor_price": 13000
    })
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()["id"]

def test_whatsapp_price_sensitive(product_id):
    print("\n2️⃣ Simulating price-sensitive customer...")
    response = requests.post(f"{BASE_URL}/webhook/whatsapp", json={
        "phone": "+2348012345678",
        "message": "How much last? Too cost. I see am for 14500 on Jiji",
        "customer_name": "Tunde",
        "product_id": product_id
    })
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Customer Type: {result['customer_type']}")
    print(f"Classification: {json.dumps(result['classification'], indent=2)}")
    return result["customer_id"]

def test_whatsapp_quality_sensitive(product_id):
    print("\n3️⃣ Simulating quality-sensitive customer...")
    response = requests.post(f"{BASE_URL}/webhook/whatsapp", json={
        "phone": "+2348087654321",
        "message": "Is it original? Which model? How long e go last?",
        "customer_name": "Chioma",
        "product_id": product_id
    })
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Customer Type: {result['customer_type']}")
    print(f"Classification: {json.dumps(result['classification'], indent=2)}")
    return result["customer_id"]

def test_market_analysis(product_id, customer_id, customer_name):
    print(f"\n4️⃣ Getting AI recommendation for {customer_name}...")
    response = requests.get(
        f"{BASE_URL}/market/analysis/{product_id}",
        params={"customer_id": customer_id}
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Strategy: {result['recommended_strategy']}")
    print(f"Recommended Price: ₦{result['recommended_price']}")
    print(f"Reasoning: {result['reasoning']}")
    print(f"Conversion Probability: {result['conversion_probability']:.2%}")

if __name__ == "__main__":
    print("🚀 Testing Naira Sniper System")
    print("=" * 50)
    
    try:
        # Test health
        health = requests.get(f"{BASE_URL}/health")
        print(f"✅ Server is running: {health.json()}")
        
        # Run tests
        product_id = test_add_product()
        
        customer_id_1 = test_whatsapp_price_sensitive(product_id)
        test_market_analysis(product_id, customer_id_1, "Tunde (Price-Sensitive)")
        
        customer_id_2 = test_whatsapp_quality_sensitive(product_id)
        test_market_analysis(product_id, customer_id_2, "Chioma (Quality-Sensitive)")
        
        print("\n" + "=" * 50)
        print("✅ All tests completed!")
        print("\n💡 Expected Results:")
        print("- Tunde should get 'price_drop' strategy")
        print("- Chioma should get 'value_reinforcement' strategy")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Server not running!")
        print("Start the server first: python main.py")
    except Exception as e:
        print(f"❌ Error: {e}")
