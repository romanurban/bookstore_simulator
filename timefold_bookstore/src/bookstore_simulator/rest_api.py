import logging
import threading
from datetime import datetime

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

def update_solution(problem_id: str, solution: RestockingSolution, is_final: bool = False):
    """Update solution and status when solver finishes or ends."""
    global solutions
    if problem_id in solutions:
        log.info(f"Updating solution {problem_id} (final: {is_final})")
        if solution is not None:
            log.info(f"Solution score: {solution.score}")
            solutions[problem_id].solution = solution
            # If final or feasible, mark as SOLVED
            if is_final or (solution.score and solution.score.hard_score >= 0):
                solutions[problem_id].status = SolutionStatus.SOLVED
                log.info(f"Updated status to SOLVED for {problem_id} with score {solution.score}")
            else:
                log.info(f"Intermediate solution: {solution.score}")

def background_solve(job_id: str, initial_solution: RestockingSolution):
    """Runs the solver in a thread, returns the final solution, and updates status."""
    log.info(f"Background solve started for job {job_id}")
    job = solver_manager.solve(job_id, initial_solution)  # Returns a SolverJob
    final_solution = job.get_final_best_solution()          # Fetch the final solution
    update_solution(job_id, final_solution, True)  # Pass is_final=True so status becomes SOLVED

@app.post("/optimize-restock")
async def optimize_restock(inventory: list[dict]) -> str:
    """Optimize restocking decisions"""
    try:
        log.info(f"Starting optimization for {len(inventory)} items")
        current_inventory = []
        
        # Extract current_date from first inventory item or use default
        current_date = None
        if inventory and "current_date" in inventory[0]:
            current_date = datetime.fromisoformat(inventory[0]["current_date"])
        else:
            current_date = datetime.now()
            
        for item in inventory:
            try:
                current_inventory.append(Book(**item))
            except ValidationError as e:
                return JSONResponse(
                    status_code=422,
                    content={"detail": e.errors()}
                )
        
        decisions = [
            RestockingDecision(
                isbn=book.isbn,
                author=book.author, 
                rating=book.rating,
                current_date=current_date,  # Add current_date to each decision
                restock_quantity=0
            ) 
            for book in current_inventory
        ]
        initial_solution = RestockingSolution(
            books=current_inventory,
            decisions=decisions,
            quantities=list(range(0, 21)),
            current_date=current_date  # Add current_date to solution
        )
        
        job_id = str(uuid4())
        log.info("Created job_id: %s", job_id)
        
        solutions[job_id] = SolutionState(
            solution=initial_solution,
            status=SolutionStatus.SOLVING
        )
        
        solving_thread = threading.Thread(target=background_solve, args=(job_id, initial_solution), daemon=True)
        solving_thread.start()
        
        log.info(f"Started solving job {job_id} in background thread")
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
    """Get current solution status"""
    if job_id not in solutions:
        raise HTTPException(status_code=404, detail="Solution not found")
    
    state = solutions[job_id]
    score = state.solution.score if state.solution else None
    
    response = {
        "status": state.status,
        "score": str(score) if score else None,
        "isSolving": state.status == SolutionStatus.SOLVING
    }
    
    log.info(f"Status request for {job_id}: {response}")
    return response

@app.get("/hello-world")
async def hello_world() -> str:
    return "hello-world"

app.mount("/", StaticFiles(directory="static", html=True), name="static")
