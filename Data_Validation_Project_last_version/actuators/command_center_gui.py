import tkinter as tk
from tkinter import scrolledtext, messagebox
import paho.mqtt.client as mqtt
import requests
import json
import threading
import time

# --- Configuration ---
API_BASE_URL = "http://localhost:8000/api"
ACTUATOR_ID_TO_FIND = "smart_lamp"

class CommandGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MQTT Command Center")
        self.root.geometry("800x600")

        self.client = None
        self.is_connected = False

        # --- Frames ---
        control_frame = tk.Frame(root, padx=10, pady=10)
        control_frame.pack(fill=tk.X)

        command_frame = tk.Frame(root, padx=10, pady=5)
        command_frame.pack(fill=tk.BOTH, expand=True)
        
        log_frame = tk.Frame(root, padx=10, pady=10)
        log_frame.pack(fill=tk.BOTH, expand=True)

        # --- Connection Controls ---
        tk.Label(control_frame, text="Broker:").grid(row=0, column=0, sticky="w")
        self.broker_entry = tk.Entry(control_frame, width=30, state="readonly")
        self.broker_entry.grid(row=0, column=1, padx=5)

        tk.Label(control_frame, text="Port:").grid(row=0, column=2, sticky="w")
        self.port_entry = tk.Entry(control_frame, width=10, state="readonly")
        self.port_entry.grid(row=0, column=3, padx=5)
        
        self.connect_button = tk.Button(control_frame, text="Connect", command=self.toggle_connection)
        self.connect_button.grid(row=0, column=4, padx=10)
        
        self.status_label = tk.Label(control_frame, text="Status: Disconnected", fg="red")
        self.status_label.grid(row=0, column=5, padx=10)

        # --- Command Publishing ---
        tk.Label(command_frame, text="Topic:").pack(anchor="w")
        self.topic_entry = tk.Entry(command_frame, state="readonly")
        self.topic_entry.pack(fill=tk.X, pady=2)
        
        tk.Label(command_frame, text="Message Payload (JSON):").pack(anchor="w")
        self.payload_entry = scrolledtext.ScrolledText(command_frame, height=5, wrap=tk.WORD)
        self.payload_entry.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.send_button = tk.Button(command_frame, text="Send Command", command=self.publish_message, state="disabled")
        self.send_button.pack(pady=5)

        # --- Example Commands ---
        tk.Label(command_frame, text="Example Commands:").pack(anchor="w", pady=(10, 2))
        self.examples_text = scrolledtext.ScrolledText(command_frame, height=8, wrap=tk.WORD, state="normal")
        self.examples_text.pack(fill=tk.BOTH, expand=True, pady=2)
        self.populate_examples()
        self.examples_text.config(state="disabled")

        # --- Log View ---
        tk.Label(log_frame, text="Logs:").pack(anchor="w")
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, wrap=tk.WORD, state="disabled")
        self.log_text.pack(fill=tk.BOTH, expand=True)

        self.fetch_config()

    def log(self, message):
        def _log():
            timestamp = time.strftime('%H:%M:%S')
            self.log_text.config(state="normal")
            self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
            self.log_text.config(state="disabled")
            self.log_text.see(tk.END)
        self.root.after(0, _log)

    def fetch_config(self):
        try:
            # Fetch MQTT Settings
            mqtt_response = requests.get(f"{API_BASE_URL}/mqtt-settings")
            mqtt_response.raise_for_status()
            mqtt_settings = mqtt_response.json()
            
            self.broker_entry.config(state="normal")
            self.broker_entry.delete(0, tk.END)
            self.broker_entry.insert(0, mqtt_settings.get("broker", "N/A"))
            self.broker_entry.config(state="readonly")
            
            self.port_entry.config(state="normal")
            self.port_entry.delete(0, tk.END)
            self.port_entry.insert(0, mqtt_settings.get("port", "N/A"))
            self.port_entry.config(state="readonly")
            self.log("Successfully fetched MQTT settings.")

            # Fetch Actuator Topic
            actuator_response = requests.get(f"{API_BASE_URL}/actuator-mappings")
            actuator_response.raise_for_status()
            actuator_mappings = actuator_response.json()
            
            topic = "N/A"
            for mapping in actuator_mappings:
                if mapping.get("actuator_id") == ACTUATOR_ID_TO_FIND:
                    # Corrected the topic key based on user feedback
                    topic = mapping.get("command_topic") or "N/A"
                    break
            
            self.topic_entry.config(state="normal")
            self.topic_entry.delete(0, tk.END)
            self.topic_entry.insert(0, topic)
            self.topic_entry.config(state="readonly")
            self.log(f"Found RAW command topic for '{ACTUATOR_ID_TO_FIND}': {topic}")

        except requests.exceptions.RequestException as e:
            self.log(f"Error fetching configuration: {e}")
            messagebox.showerror("Config Error", f"Could not fetch configuration from API.\nEnsure the main server is running.\n\nError: {e}")

    def populate_examples(self):
        examples = {
            "Living Room ON (White)": {"command": "on", "room": "living_room"},
            "Living Room OFF": {"command": "off", "room": "living_room"},
            "Kitchen ON (Red)": {"command": "red", "room": "kitchen"},
            "Kitchen OFF": {"command": "off", "room": "kitchen"},
            "Bedroom ON (Blue)": {"command": "blue", "room": "bedroom"},
            "Bedroom OFF": {"command": "off", "room": "bedroom"},
            "Bathroom ON (Green)": {"command": "green", "room": "bathroom"},
            "Bathroom OFF": {"command": "off", "room": "bathroom"},
        }
        for name, payload in examples.items():
            payload_str = json.dumps(payload)
            self.examples_text.insert(tk.END, f'--- {name} ---\n{payload_str}\n\n')

    def toggle_connection(self):
        if self.is_connected:
            self.mqtt_disconnect()
        else:
            broker = self.broker_entry.get()
            port_str = self.port_entry.get()
            if broker == "N/A" or port_str == "N/A":
                messagebox.showerror("Connection Error", "MQTT settings not loaded.")
                return
            try:
                port = int(port_str)
                threading.Thread(target=self.mqtt_connect, args=(broker, port), daemon=True).start()
            except ValueError:
                messagebox.showerror("Connection Error", "Invalid port number.")

    def mqtt_connect(self, broker, port):
        try:
            self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
            self.client.on_connect = self.on_connect
            self.client.on_disconnect = self.on_disconnect
            
            self.log(f"Connecting to {broker}:{port}...")
            self.client.connect(broker, port, 60)
            self.client.loop_forever()
        except Exception as e:
            self.log(f"MQTT Connection Error: {e}")
            self.root.after(0, lambda: messagebox.showerror("MQTT Error", f"Failed to connect: {e}"))

    def on_connect(self, client, userdata, flags, rc, props):
        if rc == 0:
            self.log("Successfully connected to MQTT broker.")
            self.is_connected = True
            self.root.after(0, self.update_ui_for_connection)
        else:
            self.log(f"Failed to connect, return code {rc}")

    def on_disconnect(self, client, userdata, rc, props):
        self.log("Disconnected from MQTT broker.")
        self.is_connected = False
        self.root.after(0, self.update_ui_for_disconnection)

    def mqtt_disconnect(self):
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            self.log("Disconnecting...")

    def update_ui_for_connection(self):
        self.status_label.config(text="Status: Connected", fg="green")
        self.connect_button.config(text="Disconnect")
        self.send_button.config(state="normal")

    def update_ui_for_disconnection(self):
        self.status_label.config(text="Status: Disconnected", fg="red")
        self.connect_button.config(text="Connect")
        self.send_button.config(state="disabled")

    def publish_message(self):
        topic = self.topic_entry.get()
        payload = self.payload_entry.get("1.0", tk.END).strip()
        
        if not self.is_connected:
            messagebox.showwarning("Warning", "Not connected to MQTT broker.")
            return
        if not topic or topic == "N/A":
            messagebox.showwarning("Warning", "MQTT topic not set.")
            return
        if not payload:
            messagebox.showwarning("Warning", "Payload is empty.")
            return
            
        try:
            json.loads(payload) # Validate JSON
            self.client.publish(topic, payload)
            self.log(f"Published to '{topic}': {payload}")
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Payload is not valid JSON.")
        except Exception as e:
            self.log(f"Failed to publish: {e}")
            messagebox.showerror("Error", f"Failed to publish message: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CommandGUI(root)
    root.mainloop()
