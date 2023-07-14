extends Node

const NetworkClient = preload("res://Scripts/websockets_client.gd")
const Packet = preload("res://Scripts/packet.gd")
const Chatbox = preload("res://Scenes/Chatbox.tscn")

# The onready keyword is a special keyword in Godot that ensures 
# the variable is assigned and ready to use when the script is 
# instantiated or the scene is loaded.
onready var _login_screen = get_node("Login")
onready var _network_client = NetworkClient.new()
var state: FuncRef
var _chatbox = null

func _ready():
	# connect sygnals with functions
	_network_client.connect("connected", self, "_handle_client_connected")
	_network_client.connect("disconnected", self, "_handle_client_disconnected")
	_network_client.connect("error", self, "_handle_network_error")
	_network_client.connect("data", self, "_handle_network_data")
	
	# Add _network_client to a Scene tree
	add_child(_network_client)
	_network_client.connect_to_server("127.0.0.1", 8081)
	
	# Connect signals with functions
	_login_screen.connect("login", self, "_handle_login_button")
	_login_screen.connect("register", self, "_handle_register_button")
	
	state = null
	
	
func PLAY(p):
	match p.action:
		"Chat":
			var message: String = p.payloads[0]
			_chatbox.add_message(message)
			
func REGISTER(p):
	match p.action:
		"Ok":
			OS.alert("Registration succenssful")
		"Deny":
			var reason: String = p.payloads[0]
			OS.alert(reason)
			
func LOGIN(p):
	match p.action:
		"Ok":
			_enter_game()
		"Deny":
			var reason: String = p.payloads[0]
			OS.alert(reason)
			
func _enter_game():
	state = funcref(self, "PLAY")
	remove_child(_login_screen)
	
	# Instanciate the chatbox
	_chatbox = Chatbox.instance()
	_chatbox.connect("message_sent", self, "send_chat")
	add_child(_chatbox)
	
func _handle_login_button(username: String, password: String):
	state = funcref(self, "LOGIN")
	var p: Packet = Packet.new("Login", [username, password])
	_network_client.send_packet(p)
	
func _handle_register_button(username: String, password: String):
	state = funcref(self, "REGISTER")
	var p: Packet = Packet.new("Register", [username, password])
	_network_client.send_packet(p)

func send_chat(text: String):
	var p: Packet = Packet.new("Chat", [text])
	_network_client.send_packet(p)
	_chatbox.add_message(text)

func _handle_client_connected():
	print("Client connected to server!")
	
func _handle_client_disconnected(was_clean: bool):
	OS.alert("Disconnected %s" % ["cleanly" if was_clean else "unexpectedly"])
	get_tree().quit()
	
func _handle_network_data(data: String):
	print("Received server data: ", data)
	var action_payloads: Array = Packet.json_to_action_payloads(data)
	var packet: Packet = Packet.new(action_payloads[0], action_payloads[1])
	# Pass the packet to our current state. If it is PLAY, it will process
	# it one way, if it is LOGIN state, it will process the packet another way
	state.call_func(packet)
	
func _handle_network_error():
	OS.alert("There was an error")
