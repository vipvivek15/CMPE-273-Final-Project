import requests
import time

BASE_URL = "http://127.0.0.1:5000"

def fetch(endpoint):
    """ Fetch data from the given endpoint and handle errors """
    try:
        response = requests.get(f"{BASE_URL}{endpoint}")
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to connect to {endpoint}: {str(e)}"}

try:
    while True:
        print("\n📊 Load Balancer Status:")
        print("🔹 Servers:", fetch("/servers"))
        print("🟠 Pending Requests:", fetch("/requests"))
        print("📝 Logs:", fetch("/logs").get("logs", [])[-3:])  # Show last 3 logs
        time.sleep(5)
except KeyboardInterrupt:
    print("\n🛑 Load Balancer Monitoring Stopped.")
