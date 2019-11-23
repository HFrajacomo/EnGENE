__author__ = "Henrique Frajacomo"

from EnGENE import Model
from ErrorHandling import *
from threading import Thread, Lock
from datetime import datetime


init(autoreset=True) # Starts Colorama

# Parse input commands
def parse(text):
	if(text.count("\"")%2 or text.count("\'")%2 or text.count("[") != text.count("]")):
		warning(-1, "Invalid string definition")
		return ""

	accumulator = ""
	IN_QUOTES = False
	IN_BRACKETS = False
	IN_WS = False

	for el in text:
		if(IN_WS and el==" " and not IN_QUOTES):
			continue
		elif(IN_BRACKETS and el==" "):
			continue
		elif(el==" "):
			IN_WS = True
		elif(el=="\"" or el=="\'"):
			IN_QUOTES = not IN_QUOTES
		elif(el == "["):
			IN_BRACKETS = True
		elif(el == "]"):
			IN_BRACKETS = False
		elif(IN_WS and el!=" "):
			IN_WS = False

		accumulator += el

	if(len(accumulator.split(" ")) > 1):
		return accumulator.split(" ")
	else:
		return accumulator

# Finds the correct command inputted by the user and handles it
def command_handler(command):
	# Fix in command parsing for threaded function
	if(type(command) == list and len(command) == 2 and command[1] == "&"):
		command = command[0]

	# Single-argument commands
	'''
		MODELS: List all models that were created
		QUIT: Quits EnGENE-Terminal
		HELP: Prompts a help message
	'''
	if(type(command) == str):
		if(command.lower() == "models"):
			function_models()
		elif(command.lower() == "help"):
			function_help()
		elif(command.lower() == "quit"):
			print("Shutting down EnGENE-Terminal...")
			exit()

	# Multi-argument commands
	'''
		NEW <name> <filename>: Loads a new model with data
		SEE <modelname>: Prints model information
		DROP <modelname> <columns>: Drop columns from model data
	'''
	if(type(command) == list):
		if(command[-1] == "&"):
			THREADED = True
		else:
			THREADED = False

		if(command[0].lower() == "new"):
			function_new(command[1], command[2], THREADED)
		elif(command[0].lower() == "see"):
			function_see(command[1], THREADED)
		elif(command[0].lower() =="drop"):
			function_drop(command[1], command[2], THREADED)

# Shows all models created
def function_models():
	if(Model.models == {}):
		print("No models were created yet")
	else:
		for mod in Model.models.values():
			print()
			print(mod)
		print()

# Help function
def function_help():
	print("EnGENE-Terminal " + version)
	print("by Henrique Frajacomo\n\n")

	print(__format_string("Models: \t\t\tShows all created models"))
	print(__format_string("Help: \t\t\tShows this help message"))
	print(__format_string("Quit: \t\t\tQuits EnGENE-Terminal"))

# Formats to table view
def __format_string(text):
	text = text.split("\t")
	out_string = ""

	for t in text:
		out_string += "{:<15}".format(t)
	return out_string

# New Function
def function_new(name, filename, THREADED):
	if(not THREADED):
		Model(name, filename)
	else:
		Thread(target=Model, args=(name, filename)).start()

# Checks if a model with name exists
def __model_exist(name):
	if(type(Model.models.get(name, False)) == Model):
		return True
	else:
		return False

# See Function - Recursive
def function_see(name, THREADED):
	if(not THREADED):
		if(__model_exist(name)):
			print()
			print(Model.models[name])
			print()
		else:
			warning(-2, "Model not found")
	else:
		Thread(target=function_see, args=(name, False)).start()

# Drop function - Recursive
def function_drop(name, columns, THREADED):
	if(not THREADED):
		new_columns = None

		if(__model_exist(name)):
			try:
				new_columns = int(columns)
			except ValueError:
				columns = columns.replace("[", "").replace("]", "").split(",")
				new_columns = [int(x) for x in columns]
		
			dropped = Model.models[name].destroy_column(new_columns)

			for element in dropped:
				print("Dropped column: " + element)

		else:
			warning(-2, "Model not found") 

	else:
		Thread(target=function_see, args=(name, columns, False)).start()

version = "v1.0"
QUIT = False

try:
	while(not QUIT):
		print("\nEnGENE-Terminal> ", end="")
		data = parse(input())
		command_handler(data)

except KeyboardInterrupt:
	QUIT = True
	exit()