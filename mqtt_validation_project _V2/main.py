from contextlib import asynccontextmanager
import json
import uvicorn
import glob
import os
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

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
async def create_new_schema_file(request: Request):
    """Creates a new schema JSON file."""
    data = await request.json()
    filename = data.get("filename")
    content = data.get("content")

    if not filename or not filename.endswith(".json") or content is None:
        raise HTTPException(status_code=400, detail="Filename (must end in .json) and content are required.")
    
    file_path = os.path.join(SCHEMAS_DIR, filename)
    if os.path.exists(file_path):
        raise HTTPException(status_code=400, detail="Schema file with this name already exists.")
        
    with open(file_path, "w") as f:
        json.dump(content, f, indent=4)
        
    return JSONResponse(content={"message": f"Schema file '{filename}' created successfully."})

@app.put("/api/schemas/{filename}")
async def update_schema_file_content(filename: str, request: Request):
    """Updates the content of an existing schema file."""
    file_path = os.path.join(SCHEMAS_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Schema file not found.")

    new_content = await request.json()
    with open(file_path, "w") as f:
        json.dump(new_content, f, indent=4)

    restart_mqtt_client()
    await manager.broadcast("config_updated")
    return JSONResponse(content={"message": f"Schema file '{filename}' updated and client restarted."})

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