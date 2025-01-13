from fastapi.testclient import TestClient
from .rest_api import app
from .domain import Book, RestockingDecision, RestockingSolution

client = TestClient(app)

def test_hello_world():
    """Test basic API functionality with hello-world endpoint"""
    response = client.get("/hello-world")
    assert response.status_code == 200
    assert response.text == '"hello-world"'

def test_optimize_restock():
    """Test optimize-restock endpoint with test inventory"""
    mock_book = {
        "title": "Test Book",
        "isbn": "123-456-789",
        "price": 29.99,
        "current_stock": 10,
        "avg_daily_sales": 2.5
    }
    
    response = client.post("/optimize-restock", json=[mock_book])
    assert response.status_code == 200
    assert isinstance(response.json(), str)  # Should return job ID

def test_empty_inventory():
    """Test optimization with empty inventory"""
    response = client.post("/optimize-restock", json=[])
    assert response.status_code == 200

def test_invalid_book_data():
    """Test with invalid book data"""
    invalid_book = {
        "isbn": "123-456-789"  # Missing required fields
    }
    response = client.post("/optimize-restock", json=[invalid_book])
    assert response.status_code == 422

def test_budget_constraint():
    """Test budget constraint (should not exceed 1000)"""
    expensive_book = {
        "title": "Expensive Book",
        "isbn": "123-456-789",
        "price": 200.0,
        "current_stock": 0,
        "avg_daily_sales": 1.0
    }
    
    response = client.post("/optimize-restock", json=[expensive_book])
    assert response.status_code == 200
    job_id = response.json()
    
    # Wait for solution
    import time
    time.sleep(5)
    
    # Verify solution respects budget
    solution = client.get(f"/solutions/{job_id}").json()
    for decision in solution["decisions"]:
        assert decision["restockQuantity"] * 200.0 <= 1000

def test_storage_constraint():
    """Test storage capacity constraint"""
    book = {
        "title": "Test Book",
        "isbn": "123-456-789",
        "price": 10.0,
        "current_stock": 90,
        "avg_daily_sales": 1.0
    }
    
    response = client.post("/optimize-restock", json=[book])
    assert response.status_code == 200
    job_id = response.json()
    
    # Wait for solution
    import time
    time.sleep(5)
    
    # Verify solution respects storage
    solution = client.get(f"/solutions/{job_id}").json()
    for decision in solution["decisions"]:
        assert decision["restockQuantity"] + 90 <= 100

def test_solver_execution():
    """Test that solver actually produces results"""
    mock_book = {
        "title": "Test Book",
        "isbn": "123-456-789",
        "price": 29.99,
        "current_stock": 10,
        "avg_daily_sales": 2.5
    }
    
    response = client.post("/optimize-restock", json=[mock_book])
    job_id = response.json()
    
    import time
    time.sleep(5)
    
    solution = client.get(f"/solutions/{job_id}").json()
    assert "decisions" in solution
    assert len(solution["decisions"]) > 0

def test_constraint_validation():
    """Test all domain constraints"""
    test_books = [
        {
            "title": "Budget Test Book",
            "isbn": "111",
            "price": 500.0,
            "current_stock": 0,
            "avg_daily_sales": 2.0
        },
        {
            "title": "Storage Test Book",
            "isbn": "222",
            "price": 10.0,
            "current_stock": 90,
            "avg_daily_sales": 1.0
        }
    ]
    
    response = client.post("/optimize-restock", json=test_books)
    job_id = response.json()
    
    import time
    time.sleep(15)
    
    solution = client.get(f"/solutions/{job_id}").json()
    assert "decisions" in solution
    
    for decision in solution["decisions"]:
        if decision["isbn"] == "111":
            assert decision["restockQuantity"] * 500.0 <= 1000
        if decision["isbn"] == "222":
            assert decision["restockQuantity"] + 90 <= 100