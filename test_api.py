import requests
import json
import time
import subprocess
import sys

# Step 1: Start the Uvicorn Server in the background for this test script
print("Starting FastAPI Backend (Uvicorn)...")
process = subprocess.Popen(["uvicorn", "api:app", "--port", "8000"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(3) # Wait for server to boot up

url = "http://127.0.0.1:8000/predict/cluster"

# Step 2: Create a mock payload to send to the AI
# Scenario: Tuesday at 2 PM, 35% CPU Load, 5000 server cluster
payload = {
    "hour_of_day": 14,
    "day_of_week": 1, 
    "avg_cpu_load": 35.0,
    "avg_memory_load": 45.0,
    "network_traffic_gbps": 18.5,
    "total_servers": 5000 
}

print("--------------------------------------------------")
print(f"Sending POST request to {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")
print("--------------------------------------------------")

try:
    # Step 3: Hit the API Endpoint
    response = requests.post(url, json=payload)
    
    # Check if the HTTP Status Code is 200 OK
    if response.status_code == 200:
        data = response.json()
        print(f"\\n✅ SUCCESS [HTTP 200 OK]")
        print(f"Action: {data['action']}")
        print(f"Servers To Shutdown: {data['servers_to_shutdown']}")
        print(f"Active Servers Remaining: {data['active_servers_remaining']}")
        print(f"Message: {data['message']}")
    else:
        print(f"\\n❌ FAILED [HTTP {response.status_code}]")
        print(response.text)
        
except requests.exceptions.ConnectionError:
    print("\\n❌ FAILED: Could not connect to the API. Is Uvicorn running?")

# Finally, kill the background server after the test completes
print("--------------------------------------------------")
print("Shutting down the test FastAPI server...")
process.terminate()
print("Done!")
