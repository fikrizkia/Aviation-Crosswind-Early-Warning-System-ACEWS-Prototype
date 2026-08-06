import math
import random
import time
import threading
from datetime import datetime
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Variabel global untuk menyimpan data sementara dari Node-RED / Simulasi
latest_data = {
    "Wind_Speed": 12.0,     # knot
    "Wind_Dir": 130.0,      # derajat
    "Runway_Head": 90.0,    # derajat (Runway 09/27)
    "Crosswind_Val": 7.7,   # knot
    "Headwind_Val": 9.2,    # knot
    "Alarm_Level": "SAFE",  # SAFE, CAUTION, WARNING, CRITICAL
    "Alarm_Message": "Kondisi angin aman untuk pendaratan.",
    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "Sim_Mode": False,
    "Sim_Scenario": "NORMAL"
}

# Variable kontrol thread simulasi otomatis di backend
auto_sim_active = False
sim_thread = None

def calculate_wind_components(wind_speed, wind_dir, runway_head):
    """Menghitung komponen Crosswind, Headwind, dan menentukan Level Alarm."""
    rad_diff = math.radians(wind_dir - runway_head)
    crosswind = abs(wind_speed * math.sin(rad_diff))
    headwind = wind_speed * math.cos(rad_diff)
    
    if crosswind < 10.0:
        level = "SAFE"
        msg = "Crosswind normal. Landasan aman untuk aktivitas aviasi."
    elif 10.0 <= crosswind < 15.0:
        level = "CAUTION"
        msg = "Perhatian: Komponen crosswind moderat. Pantau stabilitas pesawat."
    elif 15.0 <= crosswind < 20.0:
        level = "WARNING"
        msg = "Peringatan Dini: Crosswind tinggi! Diperlukan kewaspadaan tinggi."
    else:
        level = "CRITICAL"
        msg = "BAHAYA CRITICAL: Crosswind melebihi batas aman operasional!"

    return {
        "Crosswind_Val": round(crosswind, 1),
        "Headwind_Val": round(headwind, 1),
        "Alarm_Level": level,
        "Alarm_Message": msg
    }

def auto_simulation_loop():
    """Thread latar belakang untuk menghasilkan fluktuasi data angin otomatis."""
    global latest_data, auto_sim_active
    
    angle_step = 0.0
    while auto_sim_active:
        scenario = latest_data.get("Sim_Scenario", "NORMAL")
        rwy = latest_data.get("Runway_Head", 90.0)
        
        if scenario == "NORMAL":
            # Fluktuasi ringan 6 - 12 knots, sudut di sekitar 120° - 140°
            speed = 8.0 + math.sin(angle_step) * 3.0 + random.uniform(-1.0, 1.0)
            direction = (130.0 + math.cos(angle_step * 0.7) * 20.0 + random.uniform(-5.0, 5.0)) % 360
        elif scenario == "CAUTION":
            # Crosswind moderat 13 - 17 knots
            speed = 15.0 + math.sin(angle_step) * 4.0 + random.uniform(-1.5, 1.5)
            direction = (rwy + 45.0 + math.sin(angle_step * 0.5) * 15.0) % 360
        elif scenario == "STORM":
            # Badai & gust ekstrem 18 - 32 knots
            speed = 24.0 + math.sin(angle_step * 1.5) * 8.0 + random.uniform(-3.0, 5.0)
            direction = (rwy + 80.0 + math.cos(angle_step * 0.8) * 35.0) % 360
        elif scenario == "SWEEP":
            # Sudut angin berputar penuh 360 derajat secara kontinu
            speed = 16.0 + random.uniform(-2.0, 2.0)
            direction = (angle_step * 15.0) % 360
        else:
            speed = 12.0
            direction = 130.0

        angle_step += 0.1
        calc = calculate_wind_components(speed, direction, rwy)
        
        latest_data.update({
            "Wind_Speed": round(max(0, speed), 1),
            "Wind_Dir": round(direction, 1),
            "Runway_Head": round(rwy, 1),
            "Crosswind_Val": calc["Crosswind_Val"],
            "Headwind_Val": calc["Headwind_Val"],
            "Alarm_Level": calc["Alarm_Level"],
            "Alarm_Message": calc["Alarm_Message"],
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        time.sleep(1.0) # Update setiap 1 detik

@app.route('/')
def index():
    return render_template('index.html', data=latest_data)

# Endpoint API untuk menerima data dari Node-RED / Simulasi
@app.route('/update-data', methods=['POST'])
def update_data():
    global latest_data
    content = request.json or {}
    
    wind_speed = float(content.get("Wind_Speed", latest_data["Wind_Speed"]))
    wind_dir = float(content.get("Wind_Dir", latest_data["Wind_Dir"]))
    runway_head = float(content.get("Runway_Head", latest_data["Runway_Head"]))
    
    calc = calculate_wind_components(wind_speed, wind_dir, runway_head)
    
    latest_data.update({
        "Wind_Speed": round(wind_speed, 1),
        "Wind_Dir": round(wind_dir % 360, 1),
        "Runway_Head": round(runway_head % 360, 1),
        "Crosswind_Val": content.get("Crosswind_Val", calc["Crosswind_Val"]),
        "Headwind_Val": calc["Headwind_Val"],
        "Alarm_Level": calc["Alarm_Level"],
        "Alarm_Message": calc["Alarm_Message"],
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    
    return jsonify({"status": "success", "received": latest_data})

# Endpoint API untuk Mengaktifkan/Mematikan Mode Auto Simulation di Backend
@app.route('/api/sim/toggle', methods=['POST'])
def toggle_simulation():
    global auto_sim_active, sim_thread, latest_data
    content = request.json or {}
    
    enable = content.get("active", not auto_sim_active)
    scenario = content.get("scenario", latest_data.get("Sim_Scenario", "NORMAL"))
    
    latest_data["Sim_Scenario"] = scenario
    latest_data["Sim_Mode"] = enable
    
    if enable and not auto_sim_active:
        auto_sim_active = True
        sim_thread = threading.Thread(target=auto_simulation_loop, daemon=True)
        sim_thread.start()
    elif not enable and auto_sim_active:
        auto_sim_active = False

    return jsonify({
        "status": "success", 
        "auto_sim_active": auto_sim_active, 
        "scenario": scenario
    })

# Endpoint API agar halaman HTML bisa mengambil data secara *real-time* (AJAX/Fetch)
@app.route('/get-data')
def get_data():
    return jsonify(latest_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
