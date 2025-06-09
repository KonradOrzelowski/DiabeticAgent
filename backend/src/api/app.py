from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import agent_routing, glucose_reading
app = FastAPI()

app.include_router(agent_routing.router)
app.include_router(glucose_reading.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins
    allow_credentials=False,  # must be False when allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)
