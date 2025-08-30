import paho.mqtt.client as mqtt
import json
import time
import os
import tkinter as tk
import requests

# --- Configuration ---
ACTUATOR_ID = "smart_lamp"
API_URL = "http://localhost:8000/api/actuator-mappings"


# --- GUI Class ---
class LampGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Lamp Simulator - House Plan")
        self.root.geometry("680x530") # Increased window size
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(self.root, width=680, height=530, bg='#2e2e2e') # Increased canvas size
        self.canvas.pack()
        
        # Room definitions scaled up for a larger view
        self.rooms = {
            "living_room": {"coords": (15, 15, 375, 300), "name": "Living Room"},
            "kitchen": {"coords": (390, 15, 660, 225), "name": "Kitchen"},
            "bedroom": {"coords": (15, 315, 375, 510), "name": "Bedroom"},
            "bathroom": {"coords": (390, 240, 660, 510), "name": "Bathroom"},
        }
        
        self.room_elements = {}
        for room_id, room_data in self.rooms.items():
            x0, y0, x1, y1 = room_data["coords"]
            # Draw room rectangle
            rect = self.canvas.create_rectangle(x0, y0, x1, y1, outline="white", width=2)
            # Draw room label with a larger font
            label = self.canvas.create_text((x0 + x1) / 2, y0 + 20, text=room_data["name"], fill="white", font=("Helvetica", 14, "bold"))
            # Draw a larger lamp bulb
            bulb_x, bulb_y, bulb_r = (x0 + x1) / 2, (y0 + y1) / 2, 30 # Increased bulb radius
            bulb = self.canvas.create_oval(bulb_x - bulb_r, bulb_y - bulb_r, bulb_x + bulb_r, bulb_y + bulb_r, fill="grey", outline="black")
            # Draw status text with a larger font
            status_text = self.canvas.create_text(bulb_x, bulb_y + bulb_r + 20, text="OFF", fill="#a0a0a0", font=("Helvetica", 12)) # Increased font and spacing
            
            self.room_elements[room_id] = {"rect": rect, "label": label, "bulb": bulb, "status_text": status_text}

    def update_state(self, room, state):
        # Schedule the GUI update to run in the main thread
        self.root.after(0, self._update_ui, room, state)
        
    def _update_ui(self, room, state):
        if room not in self.room_elements:
            print(f"[GUI Error] Room '{room}' not found.")
            return

        elements = self.room_elements[room]
        bulb = elements["bulb"]
        status_text = elements["status_text"]

        color_map = {
            "off": "grey", "white": "white", "red": "#ff4d4d",
            "green": "#73d13d", "blue": "#40a9ff"
        }
        
        bulb_color = color_map.get(state, "white")
        
        self.canvas.itemconfig(bulb, fill=bulb_color)
        
        if state == "off":
            self.canvas.itemconfig(status_text, text="OFF", fill="#a0a0a0")
        else:
            self.canvas.itemconfig(status_text, text=state.upper(), fill="white")


# --- Load Configuration via API ---
def fetch_config():
    """Fetches actuator mappings from the central configuration API."""
    try:
        response = requests.get(API_URL)
        response.raise_for_status()  # Raise an exception for bad status codes
        mappings = response.json()
        
        for mapping in mappings:
                if mapping.get("actuator_id") == ACTUATOR_ID:
                    print(f"Configuration found for '{ACTUATOR_ID}':")
                    print(f"  - Command Topic (Validated): {mapping.get('command_validated_topic')}")
                    print(f"  - Status Topic (Raw): {mapping.get('status_topic')}")
                    return mapping
                
        print(f"ERROR: No configuration mapping found for actuator_id '{ACTUATOR_ID}' in API response.")
        
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Could not fetch configuration from API: {e}")
    except json.JSONDecodeError:
        print("ERROR: Could not decode JSON from API response.")
        
    return None

class SmartLampSimulator:
    def __init__(self, config, gui):
        self.config = config
        self.gui = gui
        self.actuator_id = config["actuator_id"]
        self.command_topic = config["command_validated_topic"] # Listen to validated commands
        self.status_topic = config["status_topic"] # Publish raw status back
        
        # Initial state for all rooms is OFF
        self.room_states = {
            "kitchen": "off",
            "bathroom": "off",
            "living_room": "off",
            "bedroom": "off"
        }
        
        # --- MQTT Client Setup ---
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
        # NOTE: Using public broker for simulation. Replace with your actual broker.
        self.broker = "broker.hivemq.com"
        self.port = 1883

    def on_connect(self, client, userdata, flags, rc, props):
        if rc == 0:
            print("[Simulator] Connected to MQTT Broker.")
            # Subscribe to the specific validated command topic
            client.subscribe(self.command_topic)
            print(f"[Simulator] Subscribed to command topic: {self.command_topic}")
            # Publish initial state for all rooms and update GUI
            for room, state in self.room_states.items():
                self.gui.update_state(room, state)
                self.publish_status(room)
        else:
            print(f"[Simulator] Failed to connect, return code {rc}\n")

    def on_message(self, client, userdata, msg):
        print(f"[Simulator] Command received on '{msg.topic}': {msg.payload.decode()}")
        try:
            data = json.loads(msg.payload.decode())
            command = data.get("command")
            room = data.get("room")

            if not room or room not in self.room_states:
                print(f"[Simulator] Error: Invalid or missing room in command: '{room}'.")
                return

            # Treat "on" as a command to turn the light white
            if command == "on":
                command = "white"

            # Check if the new command is different from the current state for that room
            if command == self.room_states[room]:
                print(f"[Simulator] Lamp in '{room}' is already in state '{command}'. No change.")
                return

            # Update state for the specific room and publish
            self.room_states[room] = command
            print(f"[Simulator] Action: Changing lamp in '{room}' to state '{command}'.")
            self.gui.update_state(room, command)
            self.publish_status(room)

        except json.JSONDecodeError:
            print("[Simulator] Error: Could not decode incoming command JSON.")

    def publish_status(self, room):
        """Publishes the current state of the lamp for a specific room."""
        current_state = self.room_states.get(room, "off")
        payload = json.dumps({
            "actuator_id": self.actuator_id,
            "room": room,
            "status": current_state,
            "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        })
        self.client.publish(self.status_topic, payload)
        print(f"[Simulator] Status for '{room}' published to '{self.status_topic}': {payload}")

    def start(self):
        print(f"[Simulator] Starting '{self.actuator_id}'...")
        self.client.connect(self.broker, self.port, 60)
        # loop_start() runs the client in a background thread.
        self.client.loop_start()

if __name__ == "__main__":
    config = fetch_config()
    if config:
        # 1. Create the Tkinter root window and GUI instance
        root = tk.Tk()
        gui = LampGUI(root)
        
        # 2. Create and start the MQTT simulator
        simulator = SmartLampSimulator(config, gui)
        simulator.start()
        
        # 3. Start the Tkinter event loop (must be in the main thread)
        root.mainloop()
        
        # This part will run after the GUI window is closed
        print("[Simulator] GUI closed, shutting down MQTT client.")
        simulator.client.loop_stop()
        simulator.client.disconnect()
    else:
        print("[Simulator] Could not start due to configuration error.")
