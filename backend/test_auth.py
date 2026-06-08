"""Test authentication to verify login is working."""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_admin_login():
    """Test admin login."""
    print("="  * 60)
    print("Testing Admin Login")
    print("=" * 60)
    
    url = f"{BASE_URL}/auth/login"
    data = {
        "email": "admin@omnipulse.ai",
        "password": "admin123"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Login Successful!")
            print(f"\nUser Details:")
            print(f"  - Name: {result['user']['name']}")
            print(f"  - Email: {result['user']['email']}")
            print(f"  - Role: {result['user']['role']}")
            print(f"  - Token: {result['access_token'][:50]}...")
            return result['access_token']
        else:
            print(f"❌ Login Failed!")
            print(f"Error: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend!")
        print("Please start the backend server:")
        print("  cd backend")
        print("  venv\\Scripts\\activate")
        print("  uvicorn app.main:app --reload")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def test_customer_login():
    """Test customer login."""
    print("\n" + "=" * 60)
    print("Testing Customer Login")
    print("=" * 60)
    
    url = f"{BASE_URL}/auth/login"
    data = {
        "email": "dhruv.bhat35@gmail.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Login Successful!")
            print(f"\nUser Details:")
            print(f"  - Name: {result['user']['name']}")
            print(f"  - Email: {result['user']['email']}")
            print(f"  - Role: {result['user']['role']}")
            print(f"  - Token: {result['access_token'][:50]}...")
            return result['access_token']
        else:
            print(f"❌ Login Failed!")
            print(f"Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def test_registration():
    """Test user registration."""
    print("\n" + "=" * 60)
    print("Testing User Registration")
    print("=" * 60)
    
    url = f"{BASE_URL}/auth/register"
    data = {
        "first_name": "Test",
        "last_name": "User",
        "email": f"testuser{__import__('random').randint(1000,9999)}@example.com",
        "password": "testpass123",
        "city": "Mumbai",
        "age": 25,
        "gender": "other"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Registration Successful!")
            print(f"\nUser Details:")
            print(f"  - Name: {result['user']['name']}")
            print(f"  - Email: {result['user']['email']}")
            print(f"  - Role: {result['user']['role']}")
            print(f"  - Token: {result['access_token'][:50]}...")
            return result['access_token']
        else:
            print(f"❌ Registration Failed!")
            print(f"Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def test_protected_endpoint(token):
    """Test accessing protected endpoint with token."""
    print("\n" + "=" * 60)
    print("Testing Protected Endpoint Access")
    print("=" * 60)
    
    url = f"{BASE_URL}/auth/me"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Token Valid!")
            print(f"\nProfile Data:")
            print(json.dumps(result, indent=2))
        else:
            print(f"❌ Token Invalid!")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("\n🧪 OmniPulse AI - Authentication Test Suite\n")
    
    # Test admin login
    admin_token = test_admin_login()
    
    # Test customer login
    customer_token = test_customer_login()
    
    # Test registration
    new_token = test_registration()
    
    # Test protected endpoint if we have a valid token
    if admin_token:
        test_protected_endpoint(admin_token)
    
    print("\n" + "=" * 60)
    print("Test Suite Complete!")
    print("=" * 60)
    print()
