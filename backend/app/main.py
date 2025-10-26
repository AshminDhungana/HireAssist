from fastapi import FastAPI


app = FastAPI()

@app.get("/")
def root():
    return {"message": "HireAssist Backend is running!"}
