import importlib.util
import json
import math
import threading
import time
import os
import pandas as pd
import paho.mqtt.client as mqtt
import pandera.pandas as pa
from pandera.errors import SchemaErrors
from utils import parse_pandera_errors

# InfluxDB specific imports
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS, ASYNCHRONOUS

# Prometheus specific import
from prometheus_client import Counter, Gauge, Enum


MESSAGES_PROCESSED = Counter(
    'mqtt_messages_processed_total',
    'Total number of processed MQTT messages',
    ['status', 'sensor_id', 'error_type']
)

# Counter for Actuator command/status messages.
ACTUATOR_MESSAGES_PROCESSED = Counter(
    'mqtt_actuator_messages_processed_total',
    'Total number of processed MQTT actuator messages',
    ['type', 'status', 'actuator_id', 'error_type'] # type: command | status
)



ACTUATOR_STATE = Enum(
    'actuator_last_known_state',
    'The last known state of an actuator',
    ['actuator_id', 'room'],
    states=['off', 'on', 'white', 'red', 'green', 'blue', 'unknown']
)


# --- InfluxDB Writer Class ---
class InfluxDBWriter:
    def __init__(self):
        self.url = os.getenv("INFLUXDB_URL")
        self.token = os.getenv("INFLUXDB_TOKEN")
        self.org = os.getenv("INFLUXDB_ORG")
        self.bucket = os.getenv("INFLUXDB_BUCKET")
        
        if not all([self.url, self.token, self.org, self.bucket]):
            print("[InfluxDB] Connection variables not fully set. Writer will be disabled.")
            self.client = None
            self.write_api = None
            return

        print(f"[InfluxDB] Initializing writer for bucket '{self.bucket}'...")
        self.client = InfluxDBClient(url=self.url, token=self.token, org=self.org)
        
        self.write_api = self.client.write_api(write_options=ASYNCHRONOUS)

    def write_validated_data(self, topic, data):
        if not self.write_api:
            return

        # Dynamically add fields from the data payload
        point = Point("mqtt_messages") \
            .tag("topic", topic) \
            .tag("status", "validated") \
            .tag("sensor_id", data.get("sensor_id", "unknown"))

        standard_keys = {"sensor_id", "timestamp"}
        for key, value in data.items():
            if key not in standard_keys and value is not None:
                # Ensure value is of a type InfluxDB can ingest (str, float, int, bool)
                if isinstance(value, (str, float, int, bool)):
                    point.field(key, value)
        


        self.write_api.write(bucket=self.bucket, org=self.org, record=point)

    def write_failed_data(self, topic, fail_report):
        if not self.write_api:
            return

        # Extract primary error for tagging
        primary_error = fail_report.get("errors", [{}])[0]
        error_type = primary_error.get("error_type", "unknown")
        error_column = primary_error.get("column", "unknown")


        clean_sensor_id = topic.strip("/")

        point = Point("mqtt_messages") \
            .tag("topic", topic) \
            .tag("status", "failed") \
            .tag("sensor_id", clean_sensor_id) \
            .tag("error_type", error_type) \
            .tag("error_column", error_column) \
            .field("full_error_report", json.dumps(fail_report))
        
        
            
        self.write_api.write(bucket=self.bucket, org=self.org, record=point)
        
    def close(self):
        if self.client:
            print("[InfluxDB] Closing client and flushing writer...")
            self.client.close()
            print("[InfluxDB] Writer closed.")

# Global variable to hold the MQTT client thread
mqtt_thread = None
stop_event = threading.Event()

def build_schema_from_json(schema_json: dict) -> pa.DataFrameSchema:
    """
    Dynamically builds a Pandera DataFrameSchema from a JSON definition.
    This version is enhanced to support more DataFrameSchema properties like
    'index', 'ordered', 'unique', etc., by passing them as kwargs.
    """
    
    # Start with a copy of the schema definition to safely manipulate it.
    schema_kwargs = schema_json.copy()

    # The 'columns' key is processed separately and then removed.
    columns_config = schema_kwargs.pop("columns", {})
    columns = {}
    for col_name, col_props in columns_config.items():
        checks = []
        dtype_str = col_props.get("dtype", "str")

        # Use Pandera's native DateTime type for robust validation
        dtype = pa.DateTime if dtype_str == "datetime" else dtype_str
        
        # Checks are only relevant for non-datetime types in our UI
        if dtype_str != "datetime" and "checks" in col_props:
            for check_name, check_arg in col_props["checks"].items():
                # Ensure the check is a valid attribute of pa.Check
                if hasattr(pa.Check, check_name):
                    checks.append(getattr(pa.Check, check_name)(check_arg))
        
        columns[col_name] = pa.Column(
            dtype=dtype,
            checks=checks,
            nullable=col_props.get("nullable", True),
            # Also allow 'unique' and other properties at the Column level
            unique=col_props.get("unique", False),
            coerce=col_props.get("coerce", schema_kwargs.get("coerce", False))
        )
    
    # Handle Index and MultiIndex
    index_config = schema_kwargs.pop("index", None)
    if index_config:
        if isinstance(index_config, list): # It's a MultiIndex
            index_list = []
            for item in index_config:
                index_list.append(
                    pa.Index(
                        dtype=item.get("dtype"),
                        name=item.get("name")
                    )
                )
            schema_kwargs["index"] = pa.MultiIndex(index_list)
        else: # It's a single Index
             schema_kwargs["index"] = pa.Index(
                dtype=index_config.get("dtype"),
                name=index_config.get("name")
            )

    # All remaining keys in schema_kwargs are passed directly to the DataFrameSchema
    return pa.DataFrameSchema(
        columns=columns,
        **schema_kwargs
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
    def __init__(self, broker, port, topic_mappings, actuator_mappings, influx_writer):
        self.broker = broker
        self.port = port
        self.topic_mappings = {mapping['source']: mapping for mapping in topic_mappings}
        self.actuator_mappings = {mapping['actuator_id']: mapping for mapping in actuator_mappings} # New: Store actuator mappings
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.schemas = {}
        self.influx_writer = influx_writer # Store the writer instance

    def on_connect(self, client, userdata, flags, rc, props):
        if rc == 0:
            print("[MQTT] Connected successfully.")
            # Subscribe to all source topics from the sensor mappings
            for source_topic in self.topic_mappings.keys():
                client.subscribe(source_topic)
                print(f"[MQTT] Subscribed to SENSOR topic: {source_topic}")
            
            # New: Subscribe to all command and status topics from actuator mappings
            for mapping in self.actuator_mappings.values():
                command_topic = mapping.get("command_topic")
                status_topic = mapping.get("status_topic")
                if command_topic:
                    client.subscribe(command_topic)
                    print(f"[MQTT] Subscribed to ACTUATOR COMMAND topic: {command_topic}")
                if status_topic:
                    client.subscribe(status_topic)
                    print(f"[MQTT] Subscribed to ACTUATOR STATUS topic: {status_topic}")

        else:
            print(f"[MQTT] Failed to connect, return code {rc}")

    def on_message(self, client, userdata, msg):
        """
        Main message router. Determines the message type based on the topic
        and delegates to the appropriate handler.
        """
        topic = msg.topic
        payload = msg.payload.decode()

        # Check if it's a sensor message
        if topic in self.topic_mappings:
            self._handle_sensor_message(client, topic, payload, self.topic_mappings[topic])
            return

        # Check if it's an actuator command or status message
        for mapping in self.actuator_mappings.values():
            if topic == mapping.get("command_topic"):
                self._handle_actuator_command(client, topic, payload, mapping)
                return
            if topic == mapping.get("status_topic"):
                self._handle_actuator_status(client, topic, payload, mapping)
                return
        
   

    def _handle_sensor_message(self, client, topic, payload, mapping):
        """Handles incoming data from a sensor."""
        source_topic = topic # For clarity
        try:
            data = json.loads(payload)
            df = pd.DataFrame([data])
            
            schema_path = mapping.get("schema")
            if not schema_path:
                # If no schema is defined for the mapping, consider it valid
                client.publish(mapping["validated"], payload, retain=False)
                print(f"[NO-SCHEMA-VALID] {source_topic} -> {mapping['validated']}")
                # Write to InfluxDB
                self.influx_writer.write_validated_data(source_topic, data)
                # Increment Prometheus counter
                MESSAGES_PROCESSED.labels(
                    status='validated', 
                    sensor_id=data.get("sensor_id", "unknown"),
                    error_type='none'
                ).inc()
                return

            schema = self.schemas.get(schema_path) # Get schema by path, not topic
            if not schema:
                print(f"[MQTT] Schema '{schema_path}' not loaded for topic {source_topic}. Skipping validation.")
                # Optionally, treat as valid if schema file is missing or failed to load
                client.publish(mapping["validated"], payload, retain=False)
                # Write to InfluxDB
                self.influx_writer.write_validated_data(source_topic, data)
                # Increment Prometheus counter
                MESSAGES_PROCESSED.labels(
                    status='validated', 
                    sensor_id=data.get("sensor_id", "unknown"),
                    error_type='none'
                ).inc()
                return

            schema.validate(df, lazy=True)
            client.publish(mapping["validated"], payload, retain=False)
            print(f"[VALID] {source_topic} -> {mapping['validated']}")
            # Write to InfluxDB
            self.influx_writer.write_validated_data(source_topic, data)
            # Increment Prometheus counter
            MESSAGES_PROCESSED.labels(
                status='validated',
                sensor_id=data.get("sensor_id", "unknown"),
                error_type='none'
            ).inc()

        except json.JSONDecodeError:
            print(f"[ERROR] Could not decode JSON from {source_topic}")
            # Increment Prometheus counter for a specific error type
            MESSAGES_PROCESSED.labels(
                status='failed',
                sensor_id=source_topic.strip("/"),
                error_type='json_decode_error'
            ).inc()
        except SchemaErrors as e:
            errors = parse_pandera_errors(e)
            original_payload_data = json.loads(payload)
            fail_msg = {"sensor": source_topic.strip("/"), "errors": errors, "original_payload": original_payload_data}
            
            # Clean the message of any NaN values before publishing
            cleaned_fail_msg = replace_nan_with_none(fail_msg)

            client.publish(mapping["failed"], json.dumps(cleaned_fail_msg), retain=False)
            print(f"[INVALID] {source_topic} -> {mapping['failed']}")
            # Write to InfluxDB
            self.influx_writer.write_failed_data(source_topic, cleaned_fail_msg)
            
            # Increment Prometheus counter FOR EACH error found
            for error in cleaned_fail_msg.get("errors", []):
                MESSAGES_PROCESSED.labels(
                    status='failed',
                    sensor_id=cleaned_fail_msg.get("sensor", "unknown"),
                    error_type=error.get('error_type', 'unknown_schema_error')
                ).inc()
                
        except Exception as e:
            print(f"[ERROR] An unexpected error occurred in on_message: {e}")
            # Increment Prometheus counter for unexpected errors
            MESSAGES_PROCESSED.labels(
                status='failed',
                sensor_id=source_topic.strip("/"),
                error_type='unexpected_exception'
            ).inc()

    def _handle_actuator_command(self, client, topic, payload, mapping):
        """Validates a command and re-publishes it to the validated or failed topic."""
        try:
            data = json.loads(payload)
            df = pd.DataFrame([data])
            
            schema_path = mapping.get("command_schema")
            schema = self.schemas.get(schema_path)

            if not schema:
                print(f"[ERROR] Command schema not found: {schema_path}")
                # Potentially publish to a generic error topic if needed
                return

            schema.validate(df, lazy=True)
            
            # Re-publish to the VALIDATED command topic
            validated_topic = mapping.get("command_validated_topic")
            client.publish(validated_topic, payload, retain=False)
            print(f"[CMD_VALID] {topic} -> {validated_topic}")

        except (json.JSONDecodeError, SchemaErrors) as e:
            failed_topic = mapping.get("command_failed_topic")
            error_report = {}
            actuator_id = mapping.get("actuator_id", "unknown")
            
            if isinstance(e, json.JSONDecodeError):
                print(f"[CMD_INVALID] JSON Error on {topic}: {e}")
                error_report = {"error_type": "json_decode_error", "reason": str(e), "original_payload": payload}
                # Increment Prometheus counter for JSON error
                ACTUATOR_MESSAGES_PROCESSED.labels(
                    type='command', status='failed', actuator_id=actuator_id, error_type='json_decode_error'
                ).inc()
            else: # SchemaErrors
                print(f"[CMD_INVALID] Schema Error on {topic}")
                errors = parse_pandera_errors(e)
                original_payload_data = json.loads(payload)
                error_report = {"actuator_id": actuator_id, "errors": errors, "original_payload": original_payload_data}
                # Increment Prometheus counter for each schema error
                for error in errors:
                    ACTUATOR_MESSAGES_PROCESSED.labels(
                        type='command', status='failed', actuator_id=actuator_id, error_type=error.get('error_type', 'unknown')
                    ).inc()

            client.publish(failed_topic, json.dumps(error_report), retain=False)
            print(f"[CMD_INVALID] {topic} -> {failed_topic}")
        except Exception as e:
            print(f"[ERROR] Unexpected error in _handle_actuator_command: {e}")
            actuator_id = mapping.get("actuator_id", "unknown")
            ACTUATOR_MESSAGES_PROCESSED.labels(
                type='command', status='failed', actuator_id=actuator_id, error_type='unexpected_exception'
            ).inc()


    def _handle_actuator_status(self, client, topic, payload, mapping):
        """Validates a status message and re-publishes it, updating metrics."""
        try:
            data = json.loads(payload)
            df = pd.DataFrame([data])
            
            schema_path = mapping.get("status_schema")
            schema = self.schemas.get(schema_path)

            if not schema:
                print(f"[ERROR] Status schema not found: {schema_path}")
                return

            validated_df = schema.validate(df, lazy=True)
            
            # Re-publish to the VALIDATED status topic
            validated_topic = mapping.get("status_validated_topic")
            client.publish(validated_topic, payload, retain=False)
            print(f"[STATUS_VALID] {topic} -> {validated_topic}")
            
            # Update Prometheus Enum metric with new labels
            actuator_id = data.get("actuator_id", "unknown")
            room = data.get("room", "default")
            state = data.get("status", "unknown") # e.g., 'off', 'blue'
            
            # Set the Enum state
            ACTUATOR_STATE.labels(actuator_id=actuator_id, room=room).state(state)
            
            # Increment success counter
            ACTUATOR_MESSAGES_PROCESSED.labels(
                type='status', status='validated', actuator_id=actuator_id, error_type='none'
            ).inc()
            

        except (json.JSONDecodeError, SchemaErrors) as e:
            failed_topic = mapping.get("status_failed_topic")
            error_report = {}
            actuator_id = mapping.get("actuator_id", "unknown")
            
            if isinstance(e, json.JSONDecodeError):
                print(f"[STATUS_INVALID] JSON Error on {topic}: {e}")
                error_report = {"error_type": "json_decode_error", "reason": str(e), "original_payload": payload}
                ACTUATOR_MESSAGES_PROCESSED.labels(
                    type='status', status='failed', actuator_id=actuator_id, error_type='json_decode_error'
                ).inc()
            else: # SchemaErrors
                print(f"[STATUS_INVALID] Schema Error on {topic}")
                errors = parse_pandera_errors(e)
                original_payload_data = json.loads(payload)
                error_report = {"actuator_id": actuator_id, "errors": errors, "original_payload": original_payload_data}
                # Increment for each error
                for error in errors:
                    ACTUATOR_MESSAGES_PROCESSED.labels(
                        type='status', status='failed', actuator_id=actuator_id, error_type=error.get('error_type', 'unknown')
                    ).inc()

            client.publish(failed_topic, json.dumps(error_report), retain=False)
            print(f"[STATUS_INVALID] {topic} -> {failed_topic}")
        except Exception as e:
            print(f"[ERROR] Unexpected error in _handle_actuator_status: {e}")
            actuator_id = mapping.get("actuator_id", "unknown")
            ACTUATOR_MESSAGES_PROCESSED.labels(
                type='status', status='failed', actuator_id=actuator_id, error_type='unexpected_exception'
            ).inc()

    def start(self):
        global stop_event
        stop_event.clear()
        
        print(f"[MQTT] Loading schemas...")
        # Load all unique schema files defined in mappings
        sensor_schema_paths = {m['schema'] for m in self.topic_mappings.values() if m.get('schema')}
        actuator_cmd_schema_paths = {m['command_schema'] for m in self.actuator_mappings.values() if m.get('command_schema')}
        actuator_status_schema_paths = {m['status_schema'] for m in self.actuator_mappings.values() if m.get('status_schema')}
        
        unique_schema_paths = sensor_schema_paths.union(actuator_cmd_schema_paths, actuator_status_schema_paths)

        for path in unique_schema_paths:
            if path: # Ensure path is not empty
                schema = load_schema_from_file(path)
            if schema:
                self.schemas[path] = schema # Store schema by its path
                print(f"  - Loaded schema from {path}")
        
        print(f"[MQTT] Connecting to {self.broker}:{self.port}...")
        self.client.connect(self.broker, self.port, 60)
        
        while not stop_event.is_set():
            self.client.loop(timeout=1.0)
        
        print("[MQTT] Loop stopped.")
        self.influx_writer.close() # <-- ADD THIS LINE
        self.client.disconnect()
        print("[MQTT] Disconnected.")

def start_mqtt_client():
    global mqtt_thread
    
    from main import read_config, read_actuator_config # Local import to avoid circular dependency
    config = read_config()
    actuator_config = read_actuator_config() # New: Read actuator config

    mqtt_settings = config.get("mqtt_settings", {})
    topic_mappings = config.get("topic_mappings", [])
    actuator_mappings = actuator_config.get("actuator_mappings", []) # New: Get actuator mappings

    if not mqtt_settings.get("broker"):
        print("[MQTT] Broker not configured. MQTT client not starting.")
        return
    if not topic_mappings and not actuator_mappings:
        print("[MQTT] No sensor or actuator mappings configured. MQTT client not starting.")
        return

    # Create an instance of the InfluxDB writer
    influx_writer = InfluxDBWriter()

    client_instance = MQTTClient(
        broker=mqtt_settings["broker"],
        port=mqtt_settings["port"],
        topic_mappings=topic_mappings,
        actuator_mappings=actuator_mappings, # Pass actuator mappings
        influx_writer=influx_writer # Pass the writer to the client
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