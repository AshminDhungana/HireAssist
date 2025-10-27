from fastapi import FastAPI
from app.api.v1 import resumes
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

@app.get("/")
def root():
    return {"message": "HireAssist Backend is running!"}

app.include_router(resumes.router, prefix="/api/v1/resumes", tags=["resumes"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)