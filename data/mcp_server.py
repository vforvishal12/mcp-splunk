from fastapi import FastAPI

app = FastAPI()

def read_logs():
    with open("data/sample_logs.txt") as f:
        return f.read()

@app.get("/search_logs")
def search_logs():
    return {"logs": read_logs()}

@app.get("/service_health")
def health():
    return {"status": "OK"}