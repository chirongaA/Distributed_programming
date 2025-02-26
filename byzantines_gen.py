import socket
import threading
import random
import json
import time

class ProcessServer:
    def __init__(self, name, port, faulty=False, user_decision="ATTACK"):
        self.name = name
        self.port = port
        self.faulty = faulty
        # Use user's choice for non-faulty processes and random for faulty
        self.decision = user_decision if not self.faulty else random.choice(["ATTACK", "RETREAT"])
        self.responses = {}
        self.final_decision = None

    def handle_client(self, conn, addr):
        try:
            data = conn.recv(1024).decode()
            message = json.loads(data)
            sender = message["sender"]
            decision = message["decision"]
            print(f"{self.name} received {decision} from {sender}")
            self.responses[sender] = decision
        finally:
            conn.close()

    def start(self):
        print(f"{self.name} starting on port {self.port}. Faulty: {self.faulty}")
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("localhost", self.port))
        server.listen(5)
        while True:
            try:
                conn, addr = server.accept()
                threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()
            except Exception as e:
                print(f"{self.name} encountered an error: {e}")

    def send_message(self, target_port, sender_name):
        message = {"sender": sender_name, "decision": self.decision}
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(("localhost", target_port))
            client.send(json.dumps(message).encode())
        except Exception as e:
            print(f"{sender_name} failed to send message to port {target_port}: {e}")
        finally:
            client.close()

    def decide(self):
        # Wait for a moment to ensure all messages are received
        time.sleep(5)
        
        # Count decisions received
        counts = {"ATTACK": 0, "RETREAT": 0}
        for decision in self.responses.values():
            counts[decision] = counts.get(decision, 0) + 1

        # Majority decision
        if counts["ATTACK"] >= counts["RETREAT"]:
            self.final_decision = "ATTACK"
        else:
            self.final_decision = "RETREAT"

        print(f"{self.name} made a final decision: {self.final_decision}")

# Start processes
def run_process(name, port, faulty, target_ports, user_decision):
    process = ProcessServer(name, port, faulty, user_decision)
    threading.Thread(target=process.start, daemon=True).start()

    # Allow time for servers to start
    time.sleep(2)

    # Send messages to other processes
    for target_port in target_ports:
        process.send_message(target_port, name)

    # Decide based on received responses
    process.decide()

# Prompt user for decision
user_decision = input("Choose the decision for non-faulty processes (ATTACK/RETREAT): ").strip().upper()
while user_decision not in ["ATTACK", "RETREAT"]:
    user_decision = input("Invalid choice. Please enter 'ATTACK' or 'RETREAT': ").strip().upper()

# Ports and configuration
ports = [5000, 5001, 5002, 5003]
names = ["P", "Q", "R", "S"]
faulty_index = 0  # Process P is faulty

# Start all processes
threads = []
for i, port in enumerate(ports):
    t = threading.Thread(
        target=run_process,
        args=(names[i], port, i == faulty_index, [p for p in ports if p != port], user_decision),
        daemon=True
    )
    threads.append(t)
    t.start()

# Allow time for all threads to complete
for t in threads:
    t.join()
