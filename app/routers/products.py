from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.models import Product
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/product", tags=["products"])

class ProductCreate(BaseModel):
    name: str
    model: str
    current_price: float
    floor_price: float

class ProductResponse(BaseModel):
    id: int
    name: str
    model: str
    current_price: float
    floor_price: float

@router.post("/add", response_model=ProductResponse)
def add_product(
    product_data: ProductCreate,
    session: Session = Depends(get_session)
):
    """Add a new product to the catalog"""
    if product_data.floor_price > product_data.current_price:
        raise HTTPException(400, "Floor price cannot exceed current price")
    
    product = Product(
        name=product_data.name,
        model=product_data.model,
        current_price=product_data.current_price,
        floor_price=product_data.floor_price
    )
    session.add(product)
    session.commit()
    session.refresh(product)
    
    return product

@router.get("/list", response_model=List[ProductResponse])
def list_products(session: Session = Depends(get_session)):
    """List all products"""
    products = session.exec(select(Product)).all()
    return products

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, session: Session = Depends(get_session)):
    """Get a specific product"""
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    return product
