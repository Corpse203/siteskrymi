import requests
import json
import time
from pprint import pprint

# Configuration
BASE_URL = "https://681b4991-7b0b-4cdf-a043-a8a60dec91b2.preview.emergentagent.com/api"
ADMIN_PASSWORD = "admin123"

# Test results tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "tests": []
}

def log_test(name, success, response=None, error=None):
    """Log test results"""
    status = "PASSED" if success else "FAILED"
    print(f"[{status}] {name}")
    
    if response:
        try:
            print(f"Response: {response.status_code}")
            print(json.dumps(response.json(), indent=2))
        except:
            print(f"Response: {response.status_code} - {response.text}")
    
    if error:
        print(f"Error: {error}")
    
    print("-" * 50)
    
    test_results["tests"].append({
        "name": name,
        "success": success,
        "details": error if error else ""
    })
    
    if success:
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1

def get_admin_session():
    """Create and return an authenticated admin session"""
    session = requests.Session()
    response = session.post(
        f"{BASE_URL}/login",
        json={"password": ADMIN_PASSWORD}
    )
    
    if response.status_code != 200:
        print("Failed to login as admin")
        print(response.text)
        return None
    
    return session

def test_get_offers():
    """Test GET /api/offers endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/offers")
        success = response.status_code == 200 and len(response.json()) == 7
        log_test("GET /api/offers - Get all offers", success, response)
        return response.json() if success else []
    except Exception as e:
        log_test("GET /api/offers - Get all offers", False, error=str(e))
        return []

def test_create_offer(session):
    """Test POST /api/offers endpoint (admin only)"""
    new_offer = {
        "title": "Test Casino",
        "bonus": "100% up to €500",
        "description": "Test casino description",
        "color": "linear-gradient(to right, #ff0000, #00ff00)",
        "logo": "https://example.com/logo.png",
        "link": "https://example.com",
        "tags": ["Test", "New"]
    }
    
    # Test with unauthenticated request (should fail)
    try:
        response = requests.post(f"{BASE_URL}/offers", json=new_offer)
        success = response.status_code == 403
        log_test("POST /api/offers - Unauthenticated (should fail)", success, response)
    except Exception as e:
        log_test("POST /api/offers - Unauthenticated (should fail)", False, error=str(e))
    
    # Test with authenticated request (should succeed)
    try:
        response = session.post(f"{BASE_URL}/offers", json=new_offer)
        success = response.status_code == 200 and "id" in response.json()
        log_test("POST /api/offers - Authenticated", success, response)
        return response.json().get("id") if success else None
    except Exception as e:
        log_test("POST /api/offers - Authenticated", False, error=str(e))
        return None

def test_update_offer(session, offer_id):
    """Test PUT /api/offers/{offer_id} endpoint (admin only)"""
    if not offer_id:
        log_test("PUT /api/offers/{offer_id} - Skipped (no offer ID)", False)
        return
    
    updated_offer = {
        "title": "Updated Test Casino",
        "bonus": "200% up to €1000",
        "description": "Updated test casino description",
        "color": "linear-gradient(to right, #0000ff, #ff00ff)",
        "logo": "https://example.com/updated-logo.png",
        "link": "https://example.com/updated",
        "tags": ["Test", "Updated"]
    }
    
    # Test with unauthenticated request (should fail)
    try:
        response = requests.put(f"{BASE_URL}/offers/{offer_id}", json=updated_offer)
        success = response.status_code == 403
        log_test(f"PUT /api/offers/{offer_id} - Unauthenticated (should fail)", success, response)
    except Exception as e:
        log_test(f"PUT /api/offers/{offer_id} - Unauthenticated (should fail)", False, error=str(e))
    
    # Test with authenticated request (should succeed)
    try:
        response = session.put(f"{BASE_URL}/offers/{offer_id}", json=updated_offer)
        success = response.status_code == 200 and response.json().get("title") == "Updated Test Casino"
        log_test(f"PUT /api/offers/{offer_id} - Authenticated", success, response)
    except Exception as e:
        log_test(f"PUT /api/offers/{offer_id} - Authenticated", False, error=str(e))

def test_delete_offer(session, offer_id):
    """Test DELETE /api/offers/{offer_id} endpoint (admin only)"""
    if not offer_id:
        log_test("DELETE /api/offers/{offer_id} - Skipped (no offer ID)", False)
        return
    
    # Test with unauthenticated request (should fail)
    try:
        response = requests.delete(f"{BASE_URL}/offers/{offer_id}")
        success = response.status_code == 403
        log_test(f"DELETE /api/offers/{offer_id} - Unauthenticated (should fail)", success, response)
    except Exception as e:
        log_test(f"DELETE /api/offers/{offer_id} - Unauthenticated (should fail)", False, error=str(e))
    
    # Test with authenticated request (should succeed)
    try:
        response = session.delete(f"{BASE_URL}/offers/{offer_id}")
        success = response.status_code == 200
        log_test(f"DELETE /api/offers/{offer_id} - Authenticated", success, response)
        
        # Verify the offer was deleted
        all_offers = requests.get(f"{BASE_URL}/offers").json()
        offer_exists = any(offer.get("id") == offer_id for offer in all_offers)
        log_test(f"Verify offer {offer_id} was deleted", not offer_exists)
    except Exception as e:
        log_test(f"DELETE /api/offers/{offer_id} - Authenticated", False, error=str(e))

def test_calls_endpoints():
    """Test calls-related endpoints"""
    # Test GET /api/calls
    try:
        response = requests.get(f"{BASE_URL}/calls")
        success = response.status_code == 200 and "calls" in response.json()
        log_test("GET /api/calls - Get all calls", success, response)
        initial_calls_count = len(response.json().get("calls", []))
    except Exception as e:
        log_test("GET /api/calls - Get all calls", False, error=str(e))
        initial_calls_count = 0
    
    # Test POST /api/calls (public)
    try:
        new_call = {
            "slot": "Book of Dead",
            "username": "TestUser123"
        }
        response = requests.post(f"{BASE_URL}/calls", json=new_call)
        success = response.status_code == 200 and response.json().get("success") == True
        log_test("POST /api/calls - Create new call (public)", success, response)
        
        # Verify the call was added
        response = requests.get(f"{BASE_URL}/calls")
        current_calls_count = len(response.json().get("calls", []))
        log_test("Verify call was added", current_calls_count > initial_calls_count, response)
    except Exception as e:
        log_test("POST /api/calls - Create new call (public)", False, error=str(e))
    
    # Get admin session for admin-only endpoints
    admin_session = get_admin_session()
    if not admin_session:
        log_test("Admin session creation failed, skipping admin-only calls tests", False)
        return
    
    # Test DELETE /api/calls/{call_index} (admin only)
    try:
        # Get current calls
        response = requests.get(f"{BASE_URL}/calls")
        calls = response.json().get("calls", [])
        
        if len(calls) > 0:
            # Test unauthenticated delete (should fail)
            response = requests.delete(f"{BASE_URL}/calls/0")
            success = response.status_code == 403
            log_test("DELETE /api/calls/0 - Unauthenticated (should fail)", success, response)
            
            # Test authenticated delete (should succeed)
            response = admin_session.delete(f"{BASE_URL}/calls/0")
            success = response.status_code == 200 and response.json().get("success") == True
            log_test("DELETE /api/calls/0 - Authenticated", success, response)
            
            # Verify call was deleted
            response = requests.get(f"{BASE_URL}/calls")
            new_calls_count = len(response.json().get("calls", []))
            log_test("Verify call was deleted", new_calls_count < current_calls_count, response)
        else:
            log_test("DELETE /api/calls/{call_index} - Skipped (no calls)", False)
    except Exception as e:
        log_test("DELETE /api/calls/{call_index}", False, error=str(e))
    
    # Test POST /api/calls/reorder (admin only)
    try:
        # Add two more calls for testing reorder
        requests.post(f"{BASE_URL}/calls", json={"slot": "Starburst", "username": "User1"})
        requests.post(f"{BASE_URL}/calls", json={"slot": "Gonzo's Quest", "username": "User2"})
        
        # Get current calls
        response = requests.get(f"{BASE_URL}/calls")
        calls = response.json().get("calls", [])
        
        if len(calls) >= 2:
            # Reorder calls (swap first two)
            new_order = list(calls)
            if len(new_order) >= 2:
                new_order[0], new_order[1] = new_order[1], new_order[0]
            
            # Test unauthenticated reorder (should fail)
            response = requests.post(f"{BASE_URL}/calls/reorder", json=new_order)
            success = response.status_code == 403
            log_test("POST /api/calls/reorder - Unauthenticated (should fail)", success, response)
            
            # Test authenticated reorder (should succeed)
            response = admin_session.post(f"{BASE_URL}/calls/reorder", json=new_order)
            success = response.status_code == 200 and response.json().get("success") == True
            log_test("POST /api/calls/reorder - Authenticated", success, response)
            
            # Verify reordering worked
            response = requests.get(f"{BASE_URL}/calls")
            reordered_calls = response.json().get("calls", [])
            if len(reordered_calls) >= 2 and len(calls) >= 2:
                reorder_success = (reordered_calls[0]["slot"] == calls[1]["slot"] and 
                                  reordered_calls[1]["slot"] == calls[0]["slot"])
                log_test("Verify calls were reordered", reorder_success, response)
            else:
                log_test("Verify calls were reordered - Skipped (not enough calls)", False)
        else:
            log_test("POST /api/calls/reorder - Skipped (not enough calls)", False)
    except Exception as e:
        log_test("POST /api/calls/reorder", False, error=str(e))
    
    # Test POST /api/calls/reset (admin only)
    try:
        # Test unauthenticated reset (should fail)
        response = requests.post(f"{BASE_URL}/calls/reset")
        success = response.status_code == 403
        log_test("POST /api/calls/reset - Unauthenticated (should fail)", success, response)
        
        # Test authenticated reset (should succeed)
        response = admin_session.post(f"{BASE_URL}/calls/reset")
        success = response.status_code == 200 and response.json().get("success") == True
        log_test("POST /api/calls/reset - Authenticated", success, response)
        
        # Verify all calls were deleted
        response = requests.get(f"{BASE_URL}/calls")
        calls = response.json().get("calls", [])
        log_test("Verify all calls were reset", len(calls) == 0, response)
    except Exception as e:
        log_test("POST /api/calls/reset", False, error=str(e))

def test_tracking_and_analytics():
    """Test tracking and analytics endpoints"""
    # Get offers to use for click tracking
    offers = requests.get(f"{BASE_URL}/offers").json()
    if not offers:
        log_test("Tracking tests - Skipped (no offers available)", False)
        return
    
    offer_id = offers[0].get("id")
    
    # Test POST /api/click
    try:
        click_data = {
            "offer_id": offer_id,
            "user_ip": "192.168.1.1"  # This will be overridden by the server
        }
        response = requests.post(f"{BASE_URL}/click", json=click_data)
        success = response.status_code == 200 and response.json().get("success") == True
        log_test("POST /api/click - Track click", success, response)
    except Exception as e:
        log_test("POST /api/click - Track click", False, error=str(e))
    
    # Test GET /api/analytics (admin only)
    admin_session = get_admin_session()
    if not admin_session:
        log_test("Admin session creation failed, skipping analytics test", False)
        return
    
    try:
        # Test unauthenticated analytics access (should fail)
        response = requests.get(f"{BASE_URL}/analytics")
        success = response.status_code == 403
        log_test("GET /api/analytics - Unauthenticated (should fail)", success, response)
        
        # Test authenticated analytics access (should succeed)
        response = admin_session.get(f"{BASE_URL}/analytics")
        success = (response.status_code == 200 and 
                  "offers_stats" in response.json() and 
                  "total_clicks" in response.json() and 
                  "total_calls" in response.json())
        log_test("GET /api/analytics - Authenticated", success, response)
        
        # Verify the click was counted
        if success:
            offer_stats = next((o for o in response.json().get("offers_stats", []) if o.get("id") == offer_id), None)
            if offer_stats:
                log_test(f"Verify click was counted for offer {offer_id}", offer_stats.get("clicks", 0) > 0, response)
            else:
                log_test(f"Verify click was counted for offer {offer_id}", False, error="Offer not found in analytics")
    except Exception as e:
        log_test("GET /api/analytics", False, error=str(e))

def test_authentication():
    """Test authentication endpoints"""
    # Test POST /api/login with correct password
    try:
        response = requests.post(f"{BASE_URL}/login", json={"password": ADMIN_PASSWORD})
        success = response.status_code == 200 and response.json().get("success") == True
        log_test("POST /api/login - Correct password", success, response)
        
        # Check if cookie was set
        admin_cookie = response.cookies.get("admin")
        log_test("Verify admin cookie was set", admin_cookie == "true")
    except Exception as e:
        log_test("POST /api/login - Correct password", False, error=str(e))
    
    # Test POST /api/login with incorrect password
    try:
        response = requests.post(f"{BASE_URL}/login", json={"password": "wrong_password"})
        success = response.status_code == 401
        log_test("POST /api/login - Incorrect password (should fail)", success, response)
    except Exception as e:
        log_test("POST /api/login - Incorrect password (should fail)", False, error=str(e))
    
    # Test POST /api/logout
    try:
        session = requests.Session()
        session.post(f"{BASE_URL}/login", json={"password": ADMIN_PASSWORD})
        
        response = session.post(f"{BASE_URL}/logout")
        success = response.status_code == 200 and response.json().get("success") == True
        log_test("POST /api/logout", success, response)
        
        # Verify cookie was removed
        admin_cookie = response.cookies.get("admin")
        log_test("Verify admin cookie was removed", admin_cookie is None)
        
        # Try to access admin-only endpoint after logout
        response = session.get(f"{BASE_URL}/analytics")
        success = response.status_code == 403
        log_test("Verify admin access revoked after logout", success, response)
    except Exception as e:
        log_test("POST /api/logout", False, error=str(e))

def test_logs_endpoint():
    """Test logs endpoint (admin only)"""
    # Test GET /api/logs
    try:
        # Test unauthenticated access (should fail)
        response = requests.get(f"{BASE_URL}/logs")
        success = response.status_code == 403
        log_test("GET /api/logs - Unauthenticated (should fail)", success, response)
        
        # Test authenticated access (should succeed)
        admin_session = get_admin_session()
        if not admin_session:
            log_test("Admin session creation failed, skipping logs test", False)
            return
        
        response = admin_session.get(f"{BASE_URL}/logs")
        success = response.status_code == 200 and isinstance(response.json(), list)
        log_test("GET /api/logs - Authenticated", success, response)
    except Exception as e:
        log_test("GET /api/logs", False, error=str(e))

def run_all_tests():
    """Run all API tests"""
    print("=" * 50)
    print("STARTING BACKEND API TESTS")
    print("=" * 50)
    
    # Test offers endpoints
    offers = test_get_offers()
    admin_session = get_admin_session()
    if admin_session:
        new_offer_id = test_create_offer(admin_session)
        if new_offer_id:
            test_update_offer(admin_session, new_offer_id)
            test_delete_offer(admin_session, new_offer_id)
    
    # Test calls endpoints
    test_calls_endpoints()
    
    # Test tracking and analytics
    test_tracking_and_analytics()
    
    # Test authentication
    test_authentication()
    
    # Test logs endpoint
    test_logs_endpoint()
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"TEST SUMMARY: {test_results['passed']} passed, {test_results['failed']} failed")
    print("=" * 50)
    
    return test_results

if __name__ == "__main__":
    run_all_tests()