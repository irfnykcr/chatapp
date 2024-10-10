import socket
import threading
from textual.widgets import Header, Static
from textual.app import App, ComposeResult
from textual.containers import Container,ScrollableContainer
from textual.widgets import Input
from json import load
from cryptography.fernet import Fernet
import time


with open("./config/config.json", "r") as f:
	j = load(f)
	HOST = j["host"]
	PORT = j["port"]
	RECV_BUFSIZE = j["bufsize"]
	MCHECK_INTERVAL = j["messagecheck_interval"]
with open("./config/key.key", "rb") as f:
	j = f.read()
	FER = Fernet(j)


CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
CLIENT.connect((HOST, PORT))
MESSAGES = []
CONT_MSG = 1

def abort():
	global CONT_MSG
	global CLIENT
	global MESSAGE_HANDLER

	CONT_MSG = 0
	CLIENT.close()
	MESSAGE_HANDLER.join()
	exit()
	return 1

def get_messages():
	global RECV_BUFSIZE
	global MCHECK_INTERVAL
	global FER
	global CONT_MSG
	try:
		while CONT_MSG:
			response = CLIENT.recv(RECV_BUFSIZE)
			response = FER.decrypt(response).decode("utf-8")
			if response == b"": return abort()
			elif response.lower() == "closed":
				return abort()
			MESSAGES.append(response)
			time.sleep(MCHECK_INTERVAL)
		return abort()
	except Exception as e:
		print(e)
		return abort()

class ChatApp(App):
	global MCHECK_INTERVAL
	global FER
	CSS_PATH = "./css/chatapp.tcss"
	def compose(self) -> ComposeResult:
		yield Header()
		yield Container(
			ScrollableContainer(
				Static(id="messages"), id="scrollable"
			),
			Input(placeholder="Type a message...", id="input"),
		)
		# yield Footer()
	def on_mount(self) -> None:
		self.set_interval(MCHECK_INTERVAL, self.update_messages)
		self.query_one("#input", Input).focus()
	def on_input_submitted(self) -> None:
		message = self.query_one("#input", Input)
		if not message.value:
			return
		msg = (message.value[:RECV_BUFSIZE]).encode("utf-8")
		msg = FER.encrypt(msg)
		CLIENT.send(msg)
		if message.value.lower() == "close":
			return abort()
		message.value = ""
		self.update_messages()
	def update_messages(self) -> None:
		if not CONT_MSG:
			return abort()
		scrollable = self.query_one("#scrollable", ScrollableContainer)
		messages_widget = self.query_one("#messages", Static)
		messages_widget.update("\n".join(MESSAGES))
		scrollable.scroll_end()

if __name__ == "__main__":
	app = ChatApp()
	MESSAGE_HANDLER = threading.Thread(target=get_messages)
	MESSAGE_HANDLER.start()
	app.run()
	abort()