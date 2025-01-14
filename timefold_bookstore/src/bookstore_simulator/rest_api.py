import logging

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from uuid import uuid4
from enum import Enum
from pydantic import BaseModel, ValidationError
from fastapi.responses import JSONResponse

from .domain import Book, RestockingDecision, RestockingSolution
from .solver import solver_manager

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

class SolutionStatus(str, Enum):
    SOLVING = "SOLVING"
    SOLVED = "SOLVED"

class SolutionState(BaseModel):
    solution: RestockingSolution
    status: SolutionStatus = SolutionStatus.SOLVING

app = FastAPI(docs_url='/q/swagger-ui')
solutions: dict[str, SolutionState] = {}

def update_solution(problem_id: str, solution: RestockingSolution):
    global solutions
    if problem_id in solutions:
        log.debug(f"Updating solution {problem_id} to SOLVED")
        solutions[problem_id] = SolutionState(
            solution=solution,
            status=SolutionStatus.SOLVED
        )
        log.debug(f"Solution {problem_id} updated: {solutions[problem_id].status}")

@app.post("/optimize-restock")
async def optimize_restock(inventory: list[dict]) -> str:
    """Optimize restocking decisions"""
    try:
        log.debug(f"Starting optimize-restock with inventory: {inventory}")
        current_inventory = []
        for item in inventory:
            try:
                current_inventory.append(Book(**item))
            except ValidationError as e:
                # Return 422 for validation errors
                return JSONResponse(
                    status_code=422,
                    content={"detail": e.errors()}
                )
        
        decisions = [
            RestockingDecision(
                isbn=book.isbn,
                author=book.author, 
                rating=book.rating,
                restock_quantity=5  # Start with 5 instead of 0
            ) 
            for book in current_inventory
        ]
        initial_solution = RestockingSolution(
            books=current_inventory,
            decisions=decisions,
            quantities=list(range(0, 21))  # Match the domain range
        )
        
        job_id = str(uuid4())
        log.debug("Created job_id: %s", job_id)
        
        solutions[job_id] = SolutionState(
            solution=initial_solution,
            status=SolutionStatus.SOLVING
        )
        
        try:
            solver_manager.solve_and_listen(
                job_id,
                initial_solution,
                lambda sol: update_solution(job_id, sol)
            )
        except Exception as e:
            log.error("Solver failed: %s", e)
            raise HTTPException(status_code=503, detail=str(e))
            
        return job_id
        
    except Exception as e:
        log.error(f"Optimization failed", exc_info=e)
        raise HTTPException(status_code=503, detail=str(e))

@app.get("/solutions/{job_id}")
async def get_solution(job_id: str):
    if job_id not in solutions:
        raise HTTPException(status_code=404, detail="Solution not found")
    
    state = solutions[job_id]
    return {
        "decisions": [
            {
                "isbn": d.isbn,
                "restockQuantity": d.restock_quantity  # Changed from quantity to restockQuantity
            } for d in state.solution.decisions
        ]
    }

@app.get("/solutions/{job_id}/status")
async def get_solution_status(job_id: str):
    if job_id not in solutions:
        raise HTTPException(status_code=404, detail="Solution not found")
    
    state = solutions[job_id]
    log.debug(f"Current state for {job_id}: {state.status}")
    return {"status": state.status}

@app.get("/hello-world")
async def hello_world() -> str:
    return "hello-world"

app.mount("/", StaticFiles(directory="static", html=True), name="static")
