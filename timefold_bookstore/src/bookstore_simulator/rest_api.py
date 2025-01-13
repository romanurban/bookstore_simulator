from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from uuid import uuid4

from .domain import Book, RestockingDecision, RestockingSolution
from .solver import solver_manager, solution_manager

app = FastAPI(docs_url='/q/swagger-ui')
data_sets: dict[str, RestockingSolution] = {}

@app.get("/hello-world") 
async def hello_world() -> str:
    return "hello-world"

def update_solution(problem_id: str, solution: RestockingSolution):
    global data_sets 
    data_sets[problem_id] = solution

@app.post("/optimize-restock")
async def optimize_restock(current_inventory: list[Book]) -> str:
    # Create initial solution
    decisions = [RestockingDecision(isbn=book.isbn) for book in current_inventory]
    initial_solution = RestockingSolution(
        books=current_inventory,
        decisions=decisions,
        quantities=list(range(101))
    )
    
    # Start solving
    job_id = str(uuid4())
    data_sets[job_id] = initial_solution
    solver_manager.solve_and_listen(job_id, initial_solution,
                                  lambda solution: update_solution(job_id, solution))
    return job_id

@app.get("/solutions/{job_id}", response_model_exclude_none=True)
async def get_solution(job_id: str) -> RestockingSolution:
    if job_id not in data_sets:
        raise HTTPException(status_code=404, detail="Solution not found")
    return data_sets[job_id]

app.mount("/", StaticFiles(directory="static", html=True), name="static")
