from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
import json
from pathlib import Path
import uvicorn
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from config import DATA_DIR
from run_analysis import run_main_pipeline

app = FastAPI(title="TabFM Trading Dashboard", version="1.0.0")

WEB_DIR = BASE_DIR / "web"

@app.get("/api/dashboard-data")
def get_dashboard_data():
    json_path = WEB_DIR / "backtest_dashboard_data.json"
    if not json_path.exists():
        json_path = DATA_DIR / "backtest_dashboard_data.json"
    
    if not json_path.exists():
        print("[Server] Dashboard data not found, running analysis pipeline...")
        _, data = run_main_pipeline()
        return data
    
    with open(json_path, "r") as f:
        data = json.load(f)
    return data

@app.post("/api/run-analysis")
def trigger_analysis():
    summary_df, data = run_main_pipeline()
    return {"status": "success", "summary": data["summary"]}

@app.get("/", response_class=HTMLResponse)
def serve_index():
    index_path = WEB_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return "<h1>Trading Dashboard Server is Running</h1>"

# Mount web static directory for /static prefix and root fallback
app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")
app.mount("/", StaticFiles(directory=str(WEB_DIR), html=True), name="root_static")

if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)

