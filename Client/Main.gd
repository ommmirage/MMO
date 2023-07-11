extends Node

const NetworkClient = preload("res://websockets_client.gd")
const Packet = preload("res://packet.gd")

# The onready keyword is a special keyword in Godot that ensures 
# the variable is assigned and ready to use when the script is 
# instantiated or the scene is loaded.
onready var _network_client = NetworkClient.new()
var state: FuncRef

func _ready():
	# connect sygnals with functions
	_network_client.connect("connected", self, "_handle_client_connected")
	_network_client.connect("disconnected", self, "_handle_client_disconnected")
	_network_client.connect("error", self, "_handle_network_error")
	_network_client.connect("data", self, "_handle_network_data")
	
	# Add _network_client to a Scene tree
	add_child(_network_client)
	
	_network_client.connect_to_server("127.0.0.1", 8082)
	
	state = funcref(self, "PLAY")
	
func PLAY(packet):
	pass
	
func _handle_client_connected():
	print("Client connected to server!")
	
func _handle_client_disconnected(was_clean: bool):
	OS.alert("Disconnected %s" % ["cleanly" if was_clean else "unexpectedly"])
	get_tree().quit()
	
func _handle_network_data(data: String):
	print("Received server data: ", data)
	var action_payloads: Array = Packet.json_toaction_payloads(data)
	var packet: Packet = Packet.new(action_payloads[0], action_payloads[1])
	# Pass the packet to our current state. If it is PLAY, it will process
	# it one way, if it is LOGIN state, it will process the packet another way
	state.call_func(packet)
	
func _handle_network_error():
	OS.alert("There was an error")
