from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select
from app.database import get_session
from app.models import Customer, SalesLog, Product
from brain.profiler import CustomerProfiler
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/webhook", tags=["webhooks"])

class WhatsAppMessage(BaseModel):
    phone: str
    message: str
    customer_name: Optional[str] = None
    product_id: Optional[int] = None

class CustomerSignalRequest(BaseModel):
    customer_id: int
    message: str

@router.post("/whatsapp")
def handle_whatsapp_message(
    data: WhatsAppMessage,
    session: Session = Depends(get_session)
):
    """
    Handle incoming WhatsApp messages
    - Create/update customer
    - Classify customer type
    - Log interaction
    """
    # Get or create customer
    customer = session.exec(
        select(Customer).where(Customer.phone == data.phone)
    ).first()
    
    if not customer:
        customer = Customer(
            phone=data.phone,
            name=data.customer_name
        )
        session.add(customer)
        session.commit()
        session.refresh(customer)
    else:
        customer.last_interaction = datetime.utcnow()
        session.add(customer)
    
    # Classify customer type from message
    profiler = CustomerProfiler()
    classification = profiler.update_customer_profile(
        session, customer.id, data.message
    )
    
    # Log sales inquiry if product mentioned
    if data.product_id:
        product = session.get(Product, data.product_id)
        if product:
            sales_log = SalesLog(
                customer_id=customer.id,
                product_id=data.product_id
            )
            session.add(sales_log)
    
    session.commit()
    
    return {
        "customer_id": customer.id,
        "customer_type": customer.customer_type.value,
        "classification": classification,
        "message": "Message processed successfully"
    }

@router.post("/customer/signal")
def store_customer_signal(
    data: CustomerSignalRequest,
    session: Session = Depends(get_session)
):
    """Store and analyze customer signals"""
    customer = session.get(Customer, data.customer_id)
    if not customer:
        raise HTTPException(404, "Customer not found")
    
    profiler = CustomerProfiler()
    classification = profiler.update_customer_profile(
        session, data.customer_id, data.message
    )
    
    return {
        "customer_id": data.customer_id,
        "classification": classification,
        "updated_type": customer.customer_type.value
    }
