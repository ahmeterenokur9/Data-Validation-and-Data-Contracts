from contextlib import asynccontextmanager
import json
import uvicorn
import glob
import os
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from prometheus_client import make_asgi_app
import ast
import aiofiles

# Import the MQTT manager
from mqtt_manager import start_mqtt_client, restart_mqtt_client, stop_mqtt_client

# --- Lifespan and Connection Management ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup...")
    start_mqtt_client()
    yield
    print("Application shutdown...")
    stop_mqtt_client()

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()
app = FastAPI(lifespan=lifespan)

# Create a separate app for Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

CONFIG_FILE = "config.json"
SCHEMAS_DIR = "schemas"
os.makedirs(SCHEMAS_DIR, exist_ok=True)

# --- WebSocket Endpoint ---
@app.websocket("/ws/config-updates")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# --- Static Files and Favicon ---
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return PlainTextResponse("", status_code=204)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="static")

# --- Config Helper Functions ---
def read_config():
    if not os.path.exists(CONFIG_FILE):
        return {"mqtt_settings": {}, "topic_mappings": []}
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def write_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

# --- Web Page Routes ---
@app.get("/", response_class=HTMLResponse)
async def serve_dashboard_root(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def serve_dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/admin", response_class=HTMLResponse)
async def serve_admin(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})

# --- Main Configuration API Routes ---
@app.get("/api/mqtt-settings")
async def get_mqtt_settings():
    config = read_config()
    headers = {"Cache-Control": "no-store"}
    return JSONResponse(content=config.get("mqtt_settings", {}), headers=headers)

@app.post("/api/mqtt-settings")
async def update_mqtt_settings(request: Request):
    settings = await request.json()
    if not settings.get("broker") or not isinstance(settings.get("port"), int):
        raise HTTPException(status_code=400, detail="Invalid MQTT settings format.")
    
    config = read_config()
    config["mqtt_settings"] = settings
    write_config(config)
    
    restart_mqtt_client()
    await manager.broadcast("config_updated")
    return JSONResponse(content={"message": "MQTT settings updated successfully."})

@app.get("/api/topic-mappings")
async def get_topic_mappings():
    config = read_config()
    headers = {"Cache-Control": "no-store"}
    return JSONResponse(content=config.get("topic_mappings", []), headers=headers)

@app.post("/api/topic-mappings")
async def update_topic_mappings(request: Request):
    mappings = await request.json()
    config = read_config()
    config["topic_mappings"] = mappings
    write_config(config)
    restart_mqtt_client()
    await manager.broadcast("config_updated")
    return JSONResponse(content={"message": "Topic mappings updated successfully."})

# --- Schema File Management API Routes ---
@app.get("/api/schemas")
async def get_all_schema_files():
    """Returns a list of available schema file paths."""
    schema_files = [os.path.join(SCHEMAS_DIR, f).replace("\\", "/") for f in os.listdir(SCHEMAS_DIR) if f.endswith('.json')]
    headers = {"Cache-Control": "no-store"}
    return JSONResponse(content=sorted(schema_files), headers=headers)

@app.get("/api/schemas/{filename}")
async def get_schema_file_content(filename: str):
    """Returns the JSON content of a specific schema file."""
    if ".." in filename or filename.startswith("/"):
        raise HTTPException(status_code=400, detail="Invalid filename.")
    
    schema_path = os.path.join(SCHEMAS_DIR, filename)
    if not os.path.exists(schema_path):
        raise HTTPException(status_code=404, detail="Schema file not found.")
    
    headers = {"Cache-Control": "no-store"}
    with open(schema_path, "r") as f:
        content = json.load(f)
    return JSONResponse(content=content, headers=headers)


@app.post("/api/schemas")
async def create_schema(request: Request):
    """Creates a new schema file from JSON content."""
    try:
        data = await request.json()
        filename = data.get("filename")
        content_str = data.get("content")
        if not all([filename, isinstance(content_str, str)]):
            raise ValueError("Request body must have 'filename' and 'content' string.")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid request format. Expecting JSON with 'filename' and 'content' keys.")

    if ".." in filename or not filename.endswith(".json") or filename.startswith("/"):
        raise HTTPException(status_code=400, detail="Invalid or unsafe filename.")
        
    filepath = os.path.join(SCHEMAS_DIR, filename)
    if os.path.exists(filepath):
        raise HTTPException(status_code=400, detail=f"Schema file '{filename}' already exists.")

    try:
        # Validate that the content string is valid JSON
        parsed_json = json.loads(content_str)
        # Re-serialize with indentation to save it in a pretty format
        json_to_write = json.dumps(parsed_json, indent=4)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Schema content is not valid JSON.")

    try:
        async with aiofiles.open(filepath, "w") as f:
            await f.write(json_to_write)
        return JSONResponse({"message": f"Schema '{filename}' created successfully."})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write schema file: {e}")


@app.put("/api/schemas/{filename}")
async def update_schema(filename: str, request: Request):
    """Updates an existing schema file with raw JSON content."""
    if ".." in filename or not filename.endswith(".json") or filename.startswith("/"):
        raise HTTPException(status_code=400, detail="Invalid or unsafe filename.")
        
    filepath = os.path.join(SCHEMAS_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail=f"Schema file '{filename}' not found.")

    content_str = (await request.body()).decode('utf-8')

    try:
        # Validate that the content string is valid JSON and format it
        parsed_json = json.loads(content_str)
        json_to_write = json.dumps(parsed_json, indent=4)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Schema content is not valid JSON.")

    try:
        async with aiofiles.open(filepath, "w") as f:
            await f.write(json_to_write)
        
        restart_mqtt_client()
        
        return JSONResponse(
            {"message": f"Schema '{filename}' updated successfully."},
            headers={"Cache-Control": "no-store"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write schema file: {e}")


@app.delete("/api/schemas/{filename}")
async def delete_schema_file(filename: str):
    """Deletes a schema file and updates any mappings that use it."""
    file_path = os.path.join(SCHEMAS_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Schema file not found.")
        
    os.remove(file_path)
    
    config = read_config()
    schema_path_to_remove = os.path.join(SCHEMAS_DIR, filename).replace("\\", "/")
    updated = False
    for mapping in config.get("topic_mappings", []):
        if mapping.get("schema") == schema_path_to_remove:
            mapping["schema"] = ""
            updated = True
    
    if updated:
        write_config(config)
        restart_mqtt_client()
        await manager.broadcast("config_updated")
        
    return JSONResponse(content={"message": f"Schema file '{filename}' deleted and mappings updated."})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 