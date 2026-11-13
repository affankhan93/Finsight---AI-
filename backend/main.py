from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend import models
from backend.database import Base, engine
from backend.routers import auth_routes, ml_routes, rag_routes, data_routes

Base.metadata.create_all(bind = engine)

app = FastAPI(title="Financial AI Backend", version="1.0")

app.add_middleware(
    CORSMiddleware, 
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500"],
    allow_methods=["*"],
    allow_headers=["*"], 
)

app.include_router(auth_routes.router) # Authentication
app.include_router(ml_routes.router) # ML infernece APIs 
app.include_router(rag_routes.router) # RAG chat API
app.include_router(data_routes.router) # Data and User management

@app.get('/', tags=['Health'])
def health_check():
    return {'status' : "ok"}

