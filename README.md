# **Load Balancer API**
A Flask-based **load balancer simulation** that efficiently assigns client requests to the least loaded active servers. The system supports:
- **Request prioritization** via a priority queue.
- **Handling server failures** and automatic request reassignment.
- **Thread-safe request processing** with logging.
- **Retrieving all requests** (both pending & processed).
- **Live monitoring of servers and logs.**

---

## **🚀 Features**
✅ Priority-based **request queuing**  
✅ **Thread-safe** processing with locks  
✅ **Automatic reassignment** when a server fails  
✅ **Real-time monitoring** of logs & server status  
✅ API for managing **servers, requests, and logs**

---

## **🛠️ Setup & Installation**
### **🔹 Prerequisites**
Ensure you have **Python 3.7+** installed. Then, install Flask:
```sh
pip install flask
```
🔹 Clone Repository
```sh
git clone https://github.com/your-repo/load-balancer.git
cd load-balancer
```
🔹 Run the Server
```sh
python load_balancer.py
```
The Flask app will start at http://127.0.0.1:5000.

🖥️ API Endpoints
1️⃣ Configure the Load Balancer
📌 Setup servers and clients

http
POST /configure
Request Body:

json
{
    "num_servers": 3,
    "num_clients": 2,
    "requests_per_client": 2
}
Response:

json
{
    "servers": 3,
    "clients": 2,
    "requests_per_client": 2
}
2️⃣ Add a Request
📌 Client sends a request

http
POST /send_request
Request Body:

json
{
    "client_id": 0,
    "request_id": 101,
    "priority": 1
}
Response:

json
{
    "message": "Request 101 added successfully!"
}
3️⃣ Retrieve All Requests
📌 Get all requests (both pending & processed)

http
GET /requests
Response Example:

json
[
    {"client_id": 0, "request_id": 101, "priority": 1, "status": "processed"},
    {"client_id": 1, "request_id": 102, "priority": 5, "status": "pending"}
]
4️⃣ Check Server Status
📌 Get the current load on all servers

http
GET /servers
Response Example:

json
[
    {"server_id": 0, "handled_requests": 2, "active": true},
    {"server_id": 1, "handled_requests": 1, "active": true},
    {"server_id": 2, "handled_requests": 0, "active": false}
]
5️⃣ Simulate Server Failure & Recovery
📌 Mark a server as down

json
POST /server_down/1
Response:

json
{
    "message": "Server 1 marked as down"
}
📌 Mark a server back online

http
POST /server_up/1
Response:

json
{
    "message": "Server 1 marked as up"
}
6️⃣ Retrieve System Logs
📌 Get all logs

http
GET /logs
Response Example:

json
{
    "logs": [
        "System configured with 3 servers and 2 clients.",
        "Request 101 from Client 0 added to queue with priority 1",
        "✅ Request 101 assigned to Server 0"
    ]
}
📌 Download logs as a file

http
GET /logs/download
(Automatically downloads a load_balancer_logs.txt file)

📊 Live Monitoring
Run the monitor script to check server load & requests in real-time:

sh
python monitor.py
🔹 Sample output:

```yaml
📊 Load Balancer Status:
🔹 Servers: [{'server_id': 0, 'handled_requests': 1, 'active': True}, {'server_id': 1, 'handled_requests': 1, 'active': True}]
🟠 Requests: [{'client_id': 1, 'request_id': 102, 'priority': 5, 'status': 'pending'}]
📝 Logs: ['✅ Request 101 assigned to Server 0']
```
📌 Project Structure
```bash
📂 load-balancer/
 ├── 📜 load_balancer.py   # Main Flask app
 ├── 📜 monitor.py         # Monitoring script
 ├── 📜 README.md          # Documentation
 ├── 📜 requirements.txt   # Python dependencies
```
