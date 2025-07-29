import importlib.util
import json
import math
import threading
import time
import pandas as pd
import paho.mqtt.client as mqtt
import pandera.pandas as pa
from pandera.errors import SchemaErrors
from utils import parse_pandera_errors

# Global variable to hold the MQTT client thread
mqtt_thread = None
stop_event = threading.Event()

def build_schema_from_json(schema_json: dict) -> pa.DataFrameSchema:
    """Dynamically builds a Pandera DataFrameSchema from a JSON definition."""
    columns = {}
    for col_name, col_props in schema_json.get("columns", {}).items():
        checks = []
        if "checks" in col_props:
            for check_name, check_arg in col_props["checks"].items():
                if hasattr(pa.Check, check_name):
                    checks.append(getattr(pa.Check, check_name)(check_arg))
        
        columns[col_name] = pa.Column(
            dtype=col_props.get("dtype", "str"),
            checks=checks,
            nullable=col_props.get("nullable", True),
            coerce=col_props.get("coerce", False)
        )
        
    return pa.DataFrameSchema(
        columns=columns,
        strict=schema_json.get("strict", False),
        coerce=schema_json.get("coerce", False)
    )

def load_schema_from_file(path: str):
    """Loads a schema from a JSON file and builds a Pandera schema."""
    try:
        with open(path, "r") as f:
            schema_definition = json.load(f)
        return build_schema_from_json(schema_definition)
    except FileNotFoundError:
        print(f"Error: Schema file not found at {path}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {path}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while loading schema from {path}: {e}")
        return None

def replace_nan_with_none(obj):
    """Recursively walk a dict or list and replace float('nan') with None."""
    if isinstance(obj, dict):
        return {k: replace_nan_with_none(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [replace_nan_with_none(elem) for elem in obj]
    elif isinstance(obj, float) and math.isnan(obj):
        return None
    return obj

class MQTTClient:
    def __init__(self, broker, port, topic_mappings):
        self.broker = broker
        self.port = port
        self.topic_mappings = {mapping['source']: mapping for mapping in topic_mappings}
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.schemas = {}

    def on_connect(self, client, userdata, flags, rc, props):
        if rc == 0:
            print("[MQTT] Connected successfully.")
            # Subscribe to all source topics from the mappings
            for source_topic in self.topic_mappings.keys():
                client.subscribe(source_topic)
                print(f"[MQTT] Subscribed to {source_topic}")
        else:
            print(f"[MQTT] Failed to connect, return code {rc}")

    def on_message(self, client, userdata, msg):
        source_topic = msg.topic
        
        # Find the corresponding mapping for the source topic
        mapping = self.topic_mappings.get(source_topic)
        if not mapping:
            print(f"[MQTT-DEBUG] No mapping found for topic '{source_topic}'. Ignoring message.")
            return

        # Debug log to show which mapping is being used
        print(f"[MQTT-DEBUG] Using mapping for '{source_topic}': Target-V: '{mapping['validated']}', Target-F: '{mapping['failed']}'")

        try:
            payload = msg.payload.decode()
            data = json.loads(payload)
            df = pd.DataFrame([data])
            
            schema_path = mapping.get("schema")
            if not schema_path:
                # If no schema is defined for the mapping, consider it valid
                client.publish(mapping["validated"], payload, retain=False)
                print(f"[NO-SCHEMA-VALID] {source_topic} -> {mapping['validated']}")
                return

            schema = self.schemas.get(schema_path) # Get schema by path, not topic
            if not schema:
                print(f"[MQTT] Schema '{schema_path}' not loaded for topic {source_topic}. Skipping validation.")
                # Optionally, treat as valid if schema file is missing or failed to load
                client.publish(mapping["validated"], payload, retain=False)
                return

            schema.validate(df, lazy=True)
            client.publish(mapping["validated"], payload, retain=False)
            print(f"[VALID] {source_topic} -> {mapping['validated']}")

        except json.JSONDecodeError:
            print(f"[ERROR] Could not decode JSON from {source_topic}")
        except SchemaErrors as e:
            errors = parse_pandera_errors(e)
            fail_msg = {"sensor": source_topic.strip("/"), "errors": errors, "original_payload": json.loads(payload)}
            
            # Clean the message of any NaN values before publishing
            cleaned_fail_msg = replace_nan_with_none(fail_msg)

            client.publish(mapping["failed"], json.dumps(cleaned_fail_msg), retain=False)
            print(f"[INVALID] {source_topic} -> {mapping['failed']}")
        except Exception as e:
            print(f"[ERROR] An unexpected error occurred in on_message: {e}")

    def start(self):
        global stop_event
        stop_event.clear()
        
        print(f"[MQTT] Loading schemas...")
        # Load all unique schema files defined in mappings
        unique_schema_paths = {m['schema'] for m in self.topic_mappings.values() if 'schema' in m}
        for path in unique_schema_paths:
            schema = load_schema_from_file(path)
            if schema:
                self.schemas[path] = schema # Store schema by its path
                print(f"  - Loaded schema from {path}")
        
        print(f"[MQTT] Connecting to {self.broker}:{self.port}...")
        self.client.connect(self.broker, self.port, 60)
        
        while not stop_event.is_set():
            self.client.loop(timeout=1.0)
        
        print("[MQTT] Loop stopped.")
        self.client.disconnect()
        print("[MQTT] Disconnected.")

def start_mqtt_client():
    global mqtt_thread
    
    from main import read_config # Local import to avoid circular dependency
    config = read_config()
    mqtt_settings = config.get("mqtt_settings", {})
    topic_mappings = config.get("topic_mappings", [])
    
    if not mqtt_settings.get("broker") or not topic_mappings:
        print("[MQTT] Broker or topic mappings not configured. MQTT client not starting.")
        return

    client_instance = MQTTClient(
        broker=mqtt_settings["broker"],
        port=mqtt_settings["port"],
        topic_mappings=topic_mappings
    )
    
    mqtt_thread = threading.Thread(target=client_instance.start)
    mqtt_thread.daemon = True
    mqtt_thread.start()
    print("[MQTT] Client thread started.")

def stop_mqtt_client():
    global mqtt_thread, stop_event
    if mqtt_thread and mqtt_thread.is_alive():
        print("[MQTT] Stopping client thread...")
        stop_event.set()
        mqtt_thread.join(timeout=5.0) # Wait for the thread to finish
        if mqtt_thread.is_alive():
            print("[MQTT] Warning: Thread did not stop gracefully.")
        else:
            print("[MQTT] Client thread stopped.")
    mqtt_thread = None

def restart_mqtt_client():
    stop_mqtt_client()
    print("[MQTT] Restarting client...")
    time.sleep(1) # Give a moment for resources to be released
    start_mqtt_client() 