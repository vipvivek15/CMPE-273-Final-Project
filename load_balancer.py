import queue
import threading
import logging
import time
from flask import Flask, jsonify, request

# Flask App Setup
app = Flask(__name__)

# Setup logging
logging.basicConfig(filename="load_balancer.log", level=logging.INFO, format="%(asctime)s - %(message)s")

### **📌 In-Memory Data Structures**
servers = {}  # Dictionary {server_id: {"handled_requests": int, "active": bool}}
clients = {}  # Dictionary {client_id: requests_sent}
request_queue = queue.PriorityQueue()  # Priority Queue for processing requests
log_entries = []  # Stores logs in-memory
pending_requests = []  # Stores pending requests
all_requests = []  # ✅ Stores all requests (both pending & processed)
pending_lock = threading.Lock()  # ✅ Prevent race conditions

### **📌 Load Balancer Class**
class LoadBalancer:
    def __init__(self):
        self.lock = threading.Lock()
        threading.Thread(target=self.process_requests, daemon=True).start()  # Start background worker

    def configure(self, num_servers, num_clients, requests_per_client):
        """ Configures the system with the number of servers and clients """
        global servers, clients
        servers = {i: {"handled_requests": 0, "active": True} for i in range(num_servers)}  # Initialize servers
        clients = {i: requests_per_client for i in range(num_clients)}  # Initialize clients
        log_event(f"System configured with {num_servers} servers and {num_clients} clients.")
        return {"servers": num_servers, "clients": num_clients, "requests_per_client": requests_per_client}

    def add_request(self, client_id, request_id, priority):
        """ Adds a request to the queue, preventing duplicates and handling errors """
        if client_id not in clients:
            return {"error": "Invalid client ID!"}, 400  # Reject unknown client IDs

        if clients[client_id] <= 0:
            return {"error": "Client has reached max requests!"}, 400  # Prevent exceeding limit

        if priority <= 0:
            return {"error": "Priority must be greater than zero!"}, 400  # Ensure valid priority

        # Prevent duplicate requests
        existing_requests = [(r[1][0], r[1][1]) for r in request_queue.queue]
        if (client_id, request_id) in existing_requests:
            return {"error": "Request already exists!"}, 400  

        request_queue.put((priority, (client_id, request_id)))
        clients[client_id] -= 1  # Decrement available requests for client

        request_entry = {
            "client_id": client_id,
            "request_id": request_id,
            "priority": priority,
            "status": "pending"  # ✅ Initially marked as pending
        }

        # ✅ Lock to prevent race conditions
        with pending_lock:
            pending_requests.append(request_entry)
            all_requests.append(request_entry)  # ✅ Store in complete log

        log_event(f"🟠 Request {request_id} from Client {client_id} added to queue with priority {priority}")
        return {"message": f"Request {request_id} added successfully!"}, 201

    def process_requests(self):
        """ Process requests and assign to the least loaded active server """
        while True:
            time.sleep(5)  # ✅ Delay request processing to allow observation

            if not request_queue.empty():
                _, (client_id, request_id) = request_queue.get()

                with self.lock:
                    active_servers = {sid: data for sid, data in servers.items() if data["active"]}

                    if not active_servers:
                        log_event(f"⚠ No active servers available. Request {request_id} delayed.")
                        request_queue.put((_, (client_id, request_id)))  # Re-add to queue
                        time.sleep(2)  # Wait before retrying
                        continue

                    # Assign request to the least loaded active server
                    available_server = min(active_servers, key=lambda s: active_servers[s]["handled_requests"])
                    servers[available_server]["handled_requests"] += 1

                    # ✅ Update request status in `all_requests`
                    with pending_lock:
                        for req in all_requests:
                            if req["request_id"] == request_id:
                                req["status"] = "processed"
                                break
                        # ✅ Remove from pending requests
                        pending_requests[:] = [req for req in pending_requests if req["request_id"] != request_id]

                    log_event(f"✅ Request {request_id} assigned to Server {available_server}")
            time.sleep(1)  # Ensure loop doesn’t run at 100% CPU

    def get_server_status(self):
        """ Returns all servers and their request counts """
        return [{"server_id": sid, "handled_requests": data["handled_requests"], "active": data["active"]}
                for sid, data in servers.items()]

    def get_all_requests(self):
        """ Returns all requests (both pending & processed) """
        with pending_lock:
            log_event(f"🔍 DEBUG: Fetching All Requests = {all_requests}")
            return list(all_requests)  # ✅ Return a copy to prevent modifications while iterating

load_balancer = LoadBalancer()

### **📌 Utility Function for Logging**
def log_event(message):
    """ Adds a log entry to an in-memory log list """
    log_entries.append(message)
    print(f"📌 LOGGED: {message}")  # Also print to console for debugging

### **📌 API Endpoints**
@app.route("/configure", methods=["POST"])
def configure():
    data = request.get_json()
    return jsonify(load_balancer.configure(data["num_servers"], data["num_clients"], data["requests_per_client"]))

@app.route("/servers", methods=["GET"])
def get_servers():
    return jsonify(load_balancer.get_server_status())

@app.route("/requests", methods=["GET"])
def get_requests():
    return jsonify(load_balancer.get_all_requests())  # ✅ Fetch all requests

@app.route("/send_request", methods=["POST"])
def send_request():
    data = request.get_json()
    return jsonify(load_balancer.add_request(data["client_id"], data["request_id"], data["priority"]))

@app.route("/logs", methods=["GET"])
def get_logs():
    return jsonify({"logs": log_entries})  # ✅ Return full log list

@app.route("/server_down/<int:server_id>", methods=["POST"])
def mark_server_down(server_id):
    """ Simulates a server going down """
    if server_id not in servers:
        return jsonify({"error": "Invalid server ID"}), 400
    servers[server_id]["active"] = False
    log_event(f"❌ Server {server_id} is DOWN.")
    return jsonify({"message": f"Server {server_id} marked as down"}), 200

@app.route("/server_up/<int:server_id>", methods=["POST"])
def mark_server_up(server_id):
    """ Simulates a server recovering """
    if server_id not in servers:
        return jsonify({"error": "Invalid server ID"}), 400
    servers[server_id]["active"] = True
    log_event(f"✅ Server {server_id} is BACK ONLINE.")
    return jsonify({"message": f"Server {server_id} marked as up"}), 200

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
