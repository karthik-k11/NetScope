from fastapi import FastAPI

app = FastAPI(
    title="NetScope",
    description="Lightweight network diagnostics and monitoring application",
    version="0.1.0",
)


@app.get("/")
def root():
    return {"message": "NetScope is running"}