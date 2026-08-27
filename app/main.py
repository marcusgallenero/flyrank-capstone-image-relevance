from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {
        "name": "AI Image Understanding & Content Matching Engine",
        "version": "1.0",
    }


@app.get("/health")
def get_health():
    return {"status": "ok"}
