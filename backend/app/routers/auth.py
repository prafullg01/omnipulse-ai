"""Authentication Router — Register, Login, Logout, Profile.

Every auth action:
1. Saves to database
2. Creates event
3. Creates/closes session
4. Broadcasts via WebSocket
5. Triggers AI intelligence update
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.database.connection import get_db
from app.models.models import Customer, CustomerProfile, Event
from app.models.realtime_models import CustomerSession
from app.utils.auth import hash_password, verify_password, create_access_token, get_current_user, decode_token
from app.websocket.manager import manager
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()

# Optional bearer scheme (auto_error=False means it doesn't raise 401 for missing tokens)
optional_security = HTTPBearer(auto_error=False)


def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(optional_security),
    db: Session = Depends(get_db),
):
    """Get current user if authenticated, None otherwise."""
    if credentials is None:
        return None
    try:
        payload = decode_token(credentials.credentials)
        customer_id = payload.get("sub")
        if not customer_id:
            return None
        user = db.query(Customer).filter(Customer.customer_id == customer_id).first()
        return user
    except Exception:
        return None


class RegisterRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    phone: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    city: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


def _extract_device_info(request: Request) -> dict:
    """Extract device/browser info from request headers."""
    user_agent = request.headers.get("user-agent", "Unknown")
    
    # Simple device detection
    ua_lower = user_agent.lower()
    if "mobile" in ua_lower or "android" in ua_lower or "iphone" in ua_lower:
        device = "mobile"
    elif "tablet" in ua_lower or "ipad" in ua_lower:
        device = "tablet"
    else:
        device = "desktop"
    
    # Simple browser detection
    if "chrome" in ua_lower and "edg" not in ua_lower:
        browser = "Chrome"
    elif "firefox" in ua_lower:
        browser = "Firefox"
    elif "safari" in ua_lower and "chrome" not in ua_lower:
        browser = "Safari"
    elif "edg" in ua_lower:
        browser = "Edge"
    else:
        browser = "Other"
    
    # Get IP
    ip = request.headers.get("x-forwarded-for", request.client.host if request.client else "127.0.0.1")
    
    return {"device": device, "browser": browser, "ip": ip, "user_agent": user_agent}


@router.post("/register", response_model=AuthResponse)
async def register(req: RegisterRequest, request: Request, db: Session = Depends(get_db)):
    # Check if email exists
    existing = db.query(Customer).filter(Customer.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    hashed_pw = hash_password(req.password)
    
    # Create customer
    customer = Customer(
        first_name=req.first_name,
        last_name=req.last_name,
        email=req.email,
        password_hash=hashed_pw,
        phone=req.phone,
        gender=req.gender,
        age=req.age,
        city=req.city,
        role="customer",
        status="active",
    )
    db.add(customer)
    db.flush()
    
    # Create empty intelligence profile
    profile = CustomerProfile(
        customer_id=customer.customer_id,
        trust_score=50.0,
        happiness_score=50.0,
        engagement_score=50.0,
        segment="new",
    )
    db.add(profile)
    
    # Create USER_REGISTERED event
    event = Event(
        customer_id=customer.customer_id,
        event_type="USER_REGISTERED",
        event_value=f"{customer.first_name} {customer.last_name}",
        metadata_json={
            "email": customer.email,
            "city": customer.city,
            "gender": customer.gender,
            "age": customer.age,
        },
        timestamp=datetime.utcnow()
    )
    db.add(event)
    
    # Create session
    device_info = _extract_device_info(request)
    session = CustomerSession(
        customer_id=customer.customer_id,
        login_time=datetime.utcnow(),
        device=device_info["device"],
        browser=device_info["browser"],
        ip_address=device_info["ip"],
        user_agent=device_info["user_agent"],
        is_active=True,
    )
    db.add(session)
    
    try:
        db.commit()
        db.refresh(customer)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")
    
    # Create token
    token = create_access_token({"sub": customer.customer_id, "role": customer.role})
    
    customer_name = f"{customer.first_name} {customer.last_name}"
    
    # Broadcast USER_REGISTERED to admin
    await manager.broadcast({
        "type": "customer_activity",
        "event_type": "USER_REGISTERED",
        "customer_id": customer.customer_id,
        "customer_name": customer_name,
        "event_value": customer_name,
        "message": f"🆕 {customer_name} registered",
        "timestamp": datetime.utcnow().isoformat(),
        "metadata": {
            "email": customer.email,
            "city": customer.city,
            "gender": customer.gender,
        }
    }, room="admin")
    
    return AuthResponse(
        access_token=token,
        user={
            "customer_id": customer.customer_id,
            "name": customer_name,
            "email": customer.email,
            "role": customer.role,
        },
    )


@router.post("/login", response_model=AuthResponse)
async def login(req: LoginRequest, request: Request, db: Session = Depends(get_db)):
    # Find customer by email
    customer = db.query(Customer).filter(Customer.email == req.email).first()
    
    if not customer:
        raise HTTPException(status_code=401, detail="Invalid credentials - user not found")
    
    # Verify password
    password_valid = verify_password(req.password, customer.password_hash)
    if not password_valid:
        raise HTTPException(status_code=401, detail="Invalid credentials - incorrect password")
    
    # Create token
    token = create_access_token({"sub": customer.customer_id, "role": customer.role})
    
    customer_name = f"{customer.first_name} {customer.last_name}"
    
    # Create USER_LOGIN event
    event = Event(
        customer_id=customer.customer_id,
        event_type="USER_LOGIN",
        event_value=customer_name,
        metadata_json={"email": customer.email},
        timestamp=datetime.utcnow()
    )
    db.add(event)
    
    # Create session
    device_info = _extract_device_info(request)
    session = CustomerSession(
        customer_id=customer.customer_id,
        login_time=datetime.utcnow(),
        device=device_info["device"],
        browser=device_info["browser"],
        ip_address=device_info["ip"],
        user_agent=device_info["user_agent"],
        is_active=True,
    )
    db.add(session)
    
    db.commit()
    
    # Broadcast USER_LOGIN to admin
    await manager.broadcast({
        "type": "customer_activity",
        "event_type": "USER_LOGIN",
        "customer_id": customer.customer_id,
        "customer_name": customer_name,
        "event_value": customer_name,
        "message": f"🔑 {customer_name} logged in",
        "timestamp": datetime.utcnow().isoformat(),
        "metadata": {
            "email": customer.email,
            "city": customer.city,
            "device": device_info["device"],
            "browser": device_info["browser"],
        }
    }, room="admin")
    
    return AuthResponse(
        access_token=token,
        user={
            "customer_id": customer.customer_id,
            "name": customer_name,
            "email": customer.email,
            "role": customer.role,
        },
    )


@router.post("/logout")
async def logout(user: Customer = Depends(get_current_user), db: Session = Depends(get_db)):
    """Logout: close session, create event, broadcast."""
    customer_name = f"{user.first_name} {user.last_name}"
    
    # Close active sessions
    active_sessions = db.query(CustomerSession).filter(
        CustomerSession.customer_id == user.customer_id,
        CustomerSession.is_active == True
    ).all()
    
    for session in active_sessions:
        session.is_active = False
        session.logout_time = datetime.utcnow()
        if session.login_time:
            session.duration_seconds = int((datetime.utcnow() - session.login_time).total_seconds())
    
    # Create USER_LOGOUT event
    event = Event(
        customer_id=user.customer_id,
        event_type="USER_LOGOUT",
        event_value=customer_name,
        metadata_json={},
        timestamp=datetime.utcnow()
    )
    db.add(event)
    db.commit()
    
    # Broadcast USER_LOGOUT to admin
    await manager.broadcast({
        "type": "customer_activity",
        "event_type": "USER_LOGOUT",
        "customer_id": user.customer_id,
        "customer_name": customer_name,
        "event_value": customer_name,
        "message": f"👋 {customer_name} logged out",
        "timestamp": datetime.utcnow().isoformat(),
        "metadata": {}
    }, room="admin")
    
    return {"message": "Logged out successfully"}


@router.get("/me")
def get_me(user: Customer = Depends(get_current_user)):
    return {
        "customer_id": user.customer_id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "role": user.role,
        "city": user.city,
        "phone": user.phone,
        "avatar_url": user.avatar_url,
    }
