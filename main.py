from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "EC530 FDA API project"}