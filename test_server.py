from json import load
from socket import socket, AF_INET, SOCK_STREAM
from threading import Lock, Thread
from datetime import datetime
from cryptography.fernet import Fernet
from string import ascii_letters, digits
from random import choices

with open("./config/config.json", "r") as f:
	j = load(f)
	HOST = j["host"]
	PORT = j["port"]
	RECV_BUFSIZE = j["bufsize"]
with open("./config/key.key", "rb") as f:
	j = f.read()
	FER = Fernet(j)

CLIENTS = set()
CLIENT_NAMES = {}
CLIENTS_LOCK = Lock()
COUNT = 0
def genrandomanme() -> str:
	global COUNT
	COUNT += 1
	return str(COUNT) + "".join(choices(list(f"{ascii_letters + digits}"), k=15))

def handle_client(client_socket:socket, addr):
	global CLIENTS, CLIENT_NAMES, CLIENTS_LOCK
	global RECV_BUFSIZE
	global FER
	try:
		n = f"{addr[0]}:{addr[1]}"
		while True:
			request = client_socket.recv(RECV_BUFSIZE)
			request = FER.decrypt(request)
			if request == b"": break
			elif request.lower() == b"close":
				client_socket.send(b"closed")
				break
			date = (str(datetime.now()).split(" ")[1])[:11]
			request = f"{date} - {CLIENT_NAMES[n]}: ".encode("utf-8") + request
			print(request, len(request))
			request = FER.encrypt(request)
			with CLIENTS_LOCK:
				for c in CLIENTS:
					c.sendall(request)
	except Exception as e:
		print(f"Error when hanlding client: {e}")
	finally:
		client_socket.close()
		with CLIENTS_LOCK:
			CLIENTS.remove(client_socket)
			w = f"[!] {CLIENT_NAMES[n]} lost connection."
			print(w)
			for c in CLIENTS:
				c.sendall(FER.encrypt(w.encode("utf-8")))
			CLIENT_NAMES.__delitem__(n)
def run_server():
	global HOST, PORT
	global CLIENTS, CLIENT_NAMES, CLIENTS_LOCK
	try:
		server = socket(AF_INET, SOCK_STREAM)
		server.bind((HOST, PORT))
		server.listen(5)
		print(f"Listening on {HOST}:{PORT}")

		while True:
			client_socket, addr = server.accept()
			n = f"{addr[0]}:{addr[1]}"
			with CLIENTS_LOCK:
				CLIENTS.add(client_socket)
				CLIENT_NAMES[n] = genrandomanme()
				w = f"[!] {CLIENT_NAMES[n]} connected."
				print(w)
				for c in CLIENTS:
					c.sendall(FER.encrypt(w.encode("utf-8")))
			thread = Thread(target=handle_client, args=(client_socket, addr,))
			thread.start()
	except Exception as e:
		print(f"Error11: {e}")
	finally:
		server.close()
		exit()

if __name__ == "__main__":
	run_server()