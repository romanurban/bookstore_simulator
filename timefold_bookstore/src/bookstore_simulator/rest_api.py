from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from uuid import uuid4

#from .domain import EmployeeSchedule
#from .demo_data import DemoData, generate_demo_data
#from .solver import solver_manager, solution_manager
#from .solver import solver_manager

app = FastAPI(docs_url='/q/swagger-ui')

@app.get("/hello-world")
async def hello_world() -> str:
    return "hello-world"

app.mount("/", StaticFiles(directory="static", html=True), name="static")
