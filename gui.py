import tkinter as tk
from tkinter import ttk, messagebox
from paho.mqtt.client import Client
import time
import random

# MQTT Configuration
BROKER = "broker.hivemq.com"
TOPIC = "environment/data"
last_received_time = time.time()

# Generate sample data when no live data is received
def generate_sample_data():
    return f"{random.randint(15, 35)},{random.randint(30, 80)},{random.randint(100, 500)},{random.randint(50, 200)}"

# Callback function for MQTT messages
def on_message(client, userdata, msg):
    global last_received_time
    last_received_time = time.time()  
    data = msg.payload.decode()
    update_display(data, live_data=True)

# Function to update UI with received data or sample data
def update_display(data, live_data):
    try:
        values = data.split(",")

        if len(values) == 4:
            temp_label.config(text=f"🌡 {values[0]}°C", fg="red")
            hum_label.config(text=f"💧 {values[1]}%", fg="blue")
            light_label.config(text=f"💡 {values[2]}", fg="orange")
            air_label.config(text=f"🌬 {values[3]}", fg="green")

            status_label.config(text="✅ Live Data" if live_data else "⚠ Sample Data", foreground="green" if live_data else "red")
            status_indicator.config(bg="green" if live_data else "red")

            log_data(values)
            update_banner(float(values[0]), float(values[1]))
        else:
            status_label.config(text="⚠ Invalid Data!", foreground="red")
            status_indicator.config(bg="red")
    except Exception as e:
        status_label.config(text=f"❌ Error: {str(e)}", foreground="red")
        status_indicator.config(bg="red")

# Function to log data
def log_data(values):
    with open("environment_log.txt", "a") as file:
        file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Temp: {values[0]}°C, Hum: {values[1]}%, Light: {values[2]}, Air: {values[3]}\n")

# Function to update weather banner based on sensor data
def update_banner(temp, humidity):
    if temp > 35:
        banner_label.config(text="🔥 Hot Weather!", bg="#ff5733")
    elif temp < 15:
        banner_label.config(text="❄ Cold Weather!", bg="#3498db")
    elif humidity > 70:
        banner_label.config(text="🌧 High Humidity!", bg="#5dade2")
    else:
        banner_label.config(text="☀ Normal Weather", bg="#2ecc71")

# GUI Setup
root = tk.Tk()
root.title("🌍 4Casting - Smart Weather Station")
root.geometry("700x500")
root.configure(bg="#1e1e1e")

# Sidebar Frame
sidebar = tk.Frame(root, bg="#333", width=180, height=500)
sidebar.pack(side="left", fill="y")

# Sidebar Title
tk.Label(sidebar, text="📡 4Casting Station", font=("Arial", 14, "bold"), fg="cyan", bg="#333").pack(pady=10)

# Sidebar Buttons
buttons = [
    ("🔄 Refresh", lambda: mqtt_client.loop_read()),
    ("📜 View Logs", lambda: view_logs()),
    ("☀ Toggle Theme", lambda: toggle_theme()),
    ("❌ Exit", lambda: exit_app()),
]

for text, command in buttons:
    btn = ttk.Button(sidebar, text=text, command=command)
    btn.pack(fill="x", pady=5)

# Banner Label for Weather Condition
banner_label = tk.Label(root, text="☀ Normal Weather", font=("Arial", 16, "bold"), bg="#2ecc71", fg="white", width=40)
banner_label.pack(pady=10, padx=20)

# Data Display Frame
content_frame = tk.Frame(root, bg="#1e1e1e")
content_frame.pack(expand=True, fill="both", padx=20)

# Sensor Readings
sensor_frame = tk.Frame(content_frame, bg="#1e1e1e")
sensor_frame.pack()

temp_label = tk.Label(sensor_frame, text="🌡 --°C", font=("Arial", 14), fg="red", bg="#1e1e1e", width=20)
temp_label.grid(row=0, column=0, padx=10, pady=5)

hum_label = tk.Label(sensor_frame, text="💧 --%", font=("Arial", 14), fg="blue", bg="#1e1e1e", width=20)
hum_label.grid(row=0, column=1, padx=10, pady=5)

light_label = tk.Label(sensor_frame, text="💡 --", font=("Arial", 14), fg="orange", bg="#1e1e1e", width=20)
light_label.grid(row=1, column=0, padx=10, pady=5)

air_label = tk.Label(sensor_frame, text="🌬 --", font=("Arial", 14), fg="green", bg="#1e1e1e", width=20)
air_label.grid(row=1, column=1, padx=10, pady=5)

# Status Section
status_frame = tk.Frame(root, bg="#1e1e1e")
status_frame.pack(pady=10)

status_indicator = tk.Label(status_frame, text=" ", bg="gray", width=2, height=1)
status_indicator.pack(side="left", padx=10)

status_label = ttk.Label(status_frame, text="Waiting for data...", font=("Arial", 10))
status_label.pack(side="left")

# Function to toggle theme
def toggle_theme():
    if root["bg"] == "#1e1e1e":
        root.configure(bg="white")
        content_frame.config(bg="white")
        sidebar.config(bg="#ddd")
        banner_label.config(bg="blue", fg="white")
        temp_label.config(bg="white", fg="red")
        hum_label.config(bg="white", fg="blue")
        light_label.config(bg="white", fg="orange")
        air_label.config(bg="white", fg="green")
        status_label.config(foreground="black")
    else:
        root.configure(bg="#1e1e1e")
        content_frame.config(bg="#1e1e1e")
        sidebar.config(bg="#333")
        banner_label.config(bg="#2ecc71", fg="white")
        temp_label.config(bg="#1e1e1e", fg="red")
        hum_label.config(bg="#1e1e1e", fg="blue")
        light_label.config(bg="#1e1e1e", fg="orange")
        air_label.config(bg="#1e1e1e", fg="green")
        status_label.config(foreground="white")

# Function to view logs
def view_logs():
    try:
        with open("environment_log.txt", "r") as file:
            logs = file.read()
        messagebox.showinfo("📜 Data Logs", logs if logs else "No logs available.")
    except FileNotFoundError:
        messagebox.showwarning("⚠ No Logs", "No data logs found.")

# Function to exit app
def exit_app():
    mqtt_client.loop_stop()
    root.quit()

# MQTT Setup
mqtt_client = Client()
mqtt_client.on_message = on_message

try:
    mqtt_client.connect(BROKER, 1883)
    mqtt_client.subscribe(TOPIC)
    mqtt_client.loop_start()
except Exception as e:
    print("MQTT Connection Failed:", e)

# Function to update MQTT every second
def update_mqtt():
    global last_received_time

    if time.time() - last_received_time > 5:
        sample_data = generate_sample_data()
        update_display(sample_data, live_data=False)

    mqtt_client.loop_read()
    root.after(1000, update_mqtt)

update_mqtt()  
root.mainloop()