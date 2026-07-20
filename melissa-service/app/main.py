from fastapi import FastAPI

app = FastAPI(title="Melissa Service")

@app.get("/health")
def health_check():
    return {"status": "ok"}
