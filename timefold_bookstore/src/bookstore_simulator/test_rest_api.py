from fastapi.testclient import TestClient
from unittest import mock
import time
import requests
from .rest_api import app, solutions  # Add solutions import
from .domain import Book, RestockingDecision, RestockingSolution
import logging
from unittest.mock import patch, Mock
import pytest

log = logging.getLogger(__name__)

client = TestClient(app)

@pytest.fixture(autouse=True)
def cleanup_solutions():
    """Cleanup any existing solutions before and after each test"""
    solutions.clear()  # Now solutions is defined
    yield
    solutions.clear()

def test_hello_world():
    """Test basic API functionality with hello-world endpoint"""
    response = client.get("/hello-world")
    assert response.status_code == 200
    assert response.text == '"hello-world"'

def test_optimize_restock():
    """Test basic restock optimization"""
    test_books = [
        {
            "title": "Test Book 1",
            "isbn": "123-456-789",
            "price": 29.99,
            "current_stock": 0,
            "avg_daily_sales": 2.0,
            "author": "Test Author 1",
            "rating": 4.5
        },
        {
            "title": "Test Book 2", 
            "isbn": "987-654-321",
            "price": 19.99,
            "current_stock": 1,
            "avg_daily_sales": 1.5,
            "author": "Test Author 2",
            "rating": 4.0
        }
    ]

    response = client.post("/optimize-restock", json=test_books)
    assert response.status_code == 200
    
    job_id = response.json()
    assert isinstance(job_id, str)
    
    # Check solution status
    status_response = client.get(f"/solutions/{job_id}/status")
    assert status_response.status_code == 200
    assert status_response.json()["status"] in ["SOLVING", "SOLVED"]

def test_empty_inventory():
    """Test optimization with empty inventory"""
    response = client.post("/optimize-restock", json=[])
    assert response.status_code == 200

def test_invalid_book_data():
    """Test with invalid book data"""
    invalid_book = {
        "isbn": "123-456-789",
        "title": "Invalid Book",
        "price": 29.99,
        # Missing required fields: author, rating
    }
    response = client.post("/optimize-restock", json=[invalid_book])
    assert response.status_code == 422  # Unprocessable Entity
    
    error_detail = response.json()["detail"]
    assert any("author" in error["loc"] for error in error_detail)
    assert any("rating" in error["loc"] for error in error_detail)

def test_budget_constraint():
    """Test budget constraint (should not exceed 1000)"""
    expensive_book = {
        "title": "Expensive Book",
        "isbn": "123-456-789",
        "price": 200.0,
        "current_stock": 0,
        "avg_daily_sales": 1.0,
        "author": "Test Author",  # Add required field
        "rating": 4.5  # Add required field
    }

    response = client.post("/optimize-restock", json=[expensive_book])
    assert response.status_code == 200
    job_id = response.json()

    # Wait for solution with status check
    max_retries = 10
    for attempt in range(max_retries):
        status_response = client.get(f"/solutions/{job_id}/status")
        if status_response.json()["status"] == "SOLVED":
            break
        time.sleep(1)

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
        "avg_daily_sales": 1.0,
        "author": "Test Author",  # Add required field
        "rating": 4.5  # Add required field
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
        "avg_daily_sales": 2.5,
        "author": "Test Author",  # Add required field
        "rating": 4.5  # Add required field
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
            "avg_daily_sales": 2.0,
            "author": "Test Author",  # Add required field
            "rating": 4.5  # Add required field
        },
        {
            "title": "Storage Test Book",
            "isbn": "222",
            "price": 10.0,
            "current_stock": 90,
            "avg_daily_sales": 1.0,
            "author": "Sample Author",  # Add required field
            "rating": 3.0  # Add required field
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

def test_solution_timeout():
    """Test timeout handling during optimization"""
    mock_book = {
        "title": "Test Book",
        "isbn": "123-456-789",
        "price": 29.99,
        "current_stock": 10,
        "author": "Test Author",  # Add required field
        "rating": 4.5  # Add required field
    }
    
    # Start optimization
    response = client.post("/optimize-restock", json=[mock_book])
    assert response.status_code == 200
    job_id = response.json()
    
    # Test solution polling with status 
    max_retries = 35
    for attempt in range(max_retries):
        status_response = client.get(f"/solutions/{job_id}/status")
        assert status_response.status_code == 200
        
        state = status_response.json()
        if state["status"] == "SOLVED":
            solution = client.get(f"/solutions/{job_id}").json()
            assert "decisions" in solution
            return
        
        # Reduce polling frequency    
        time.sleep(0.5)  # Reduced from 1s to 0.5s
        
    pytest.fail("Solution timed out")  # Better than assert False

# Run with:
# pytest -vv --log-cli-level=DEBUG src/bookstore_simulator/test_rest_api.py::test_network_failures