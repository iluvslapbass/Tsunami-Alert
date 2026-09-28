import requests
import time
import winsound
import threading
import subprocess
import sys

# Global flag to queue the test
test_queued = False

def speak_message(message):
    safe_message = message.replace("'", "") 
    ps_command = f"Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('{safe_message}')"
    subprocess.Popen(["powershell", "-Command", ps_command], creationflags=subprocess.CREATE_NO_WINDOW)

def play_siren():
    # A much longer, attention-grabbing emergency siren (approx. 10-12 seconds)
    for _ in range(3): # Repeat the full cycle 3 times
        # 1. Upward frequency sweep (rising pitch)
        freq = 500
        while freq <= 1600:
            winsound.Beep(freq, 40)
            freq += 100
            
        # 2. Downward frequency sweep (falling pitch)
        freq = 1600
        while freq >= 500:
            winsound.Beep(freq, 40)
            freq -= 100
            
        # 3. High-low urgent alert bursts
        for _ in range(4):
            winsound.Beep(1800, 150)
            winsound.Beep(900, 150)

def show_eas_banner(message):
    safe_message = message.replace('"', '').replace("'", "")
    
    banner_code = f"""import tkinter as tk
root = tk.Tk()
root.overrideredirect(True)
root.attributes("-topmost", True)
w = root.winfo_screenwidth()
root.geometry(str(w) + "x60+0+0")
root.configure(bg="#cc0000")
lbl = tk.Label(root, text="🚨 EMERGENCY ALERT SYSTEM 🚨   ---   {safe_message}   ---   🚨 EMERGENCY ALERT SYSTEM 🚨", font=("Courier", 24, "bold"), fg="white", bg="#cc0000")
lbl.place(x=w, y=10)
loops = 0
def scroll():
    global loops
    x = lbl.winfo_x()
    if x < -lbl.winfo_reqwidth():
        loops += 1
        if loops >= 2:
            root.destroy()
        else:
            lbl.place(x=w, y=10)
            root.after(15, scroll)
    else:
        lbl.place(x=x - 4, y=10)
        root.after(15, scroll)
scroll()
root.mainloop()"""

    subprocess.Popen([sys.executable, "-c", banner_code])

def trigger_simulated_alert():
    raw_bulletin = """
ZCZC
WEZS42 PHEB 101257
TIBPPG

ASZ001>004-101457-

TSUNAMI INFORMATION STATEMENT NUMBER 1
NWS PACIFIC TSUNAMI WARNING CENTER HONOLULU HI
157 AM SST MON AUG 10 2026

...NO TSUNAMI THREAT FROM A DISTANT EARTHQUAKE...

NNNN
"""
    print(raw_bulletin)
    headline = "TSUNAMI INFORMATION STATEMENT. NO TSUNAMI THREAT FROM A DISTANT EARTHQUAKE."
    
    show_eas_banner(headline)
    play_siren()
    speak_message(f"Attention. Simulated Alert. {headline}")

def check_tsunami_alerts():
    headers = {'User-Agent': 'MySeismicDashboard/1.0'}
    url = "https://api.weather.gov/alerts/active"
    
    print(f"[{time.strftime('%H:%M:%S')}] Fetching live alert data...")
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        
        for feature in data.get('features', []):
            event = feature['properties']['event']
            
            if "Tsunami" in event:
                headline = feature['properties']['headline']
                print(f"\n🚨 TSUNAMI ALERT: {headline}")
                
                show_eas_banner(headline)
                play_siren()
                speak_message(f"Attention. {headline}")
                
    except Exception as e:
        print(f"\n❌ Error fetching data: {e}")

def background_tracker():
    global test_queued
    check_tsunami_alerts()
    
    while True:
        time.sleep(30)
        
        if test_queued:
            print(f"\n[{time.strftime('%H:%M:%S')}] Executing queued test alert...")
            trigger_simulated_alert()
            test_queued = False
            
        check_tsunami_alerts()

# --- MAIN PROGRAM START ---

print("Starting Tsunami Tracker with Custom EAS Banner...")

show_eas_banner("TRACKER ACTIVE: Monitoring for tsunami alerts every 30 seconds.")

tracker_thread = threading.Thread(target=background_tracker, daemon=True)
tracker_thread.start()

print("✅ Tracker is running in the background.")
print("👉 Type 'test' and press Enter to queue a simulated bulletin for the next cycle.")
print("👉 Type 'exit' to close the program.\n")

while True:
    user_input = input().strip().lower()
    
    if not user_input:
        continue
        
    if user_input == "test":
        test_queued = True
        print(f"[{time.strftime('%H:%M:%S')}] Test queued. It will play when the 30-second timer finishes.")
        
    elif user_input == "exit":
        print("Shutting down Tsunami Tracker...")
        break
    else:
        print("Unknown command. Type 'test' or 'exit'.")