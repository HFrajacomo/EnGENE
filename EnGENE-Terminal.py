__author__ = "Henrique Frajacomo"

from EnGENE import Model
from ErrorHandling import *
from threading import Thread, Lock
from datetime import datetime
from colorama import init, Fore
import os
from time import sleep

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
		elif(command.lower() == "clear" or command.lower() == "cls"):
			os.system("cls" if os.name == 'nt' else 'clear')

	# Multi-argument commands
	'''
		NEW <name> <filename>: Loads a new model with data
		SEE <modelname>: Prints model information
		DROP <modelname> <columns>: Drop columns from model data
		SELECT <modelname> <start> <end>: Sets feature columns in dataset
		TARGET <modelname> <column_name>: Sets the target feature for prediction
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
		elif(command[0].lower() == "select"):
			function_select(command[1], command[2], command[3])
		elif(command[0].lower() == "target"):
			function_target(command[1], command[2])
		elif(command[0].lower() == "dummies"):
			function_dummies(command[1], THREADED)
		elif(command[0].lower() == "getclasses"):
			function_get_classes(command[1])
		elif(command[0].lower() == "ovatransform"):
			function_ova_transform(command[1], command[2], THREADED)
		elif(command[0].lower() == "holdout"):
			function_holdout(command[1], command[2], command[3], THREADED)
		elif(command[0].lower() == "unused"):
			function_unused(command[1])
		elif(command[0].lower() == "fit"):
			function_fit(command[1], command[2], THREADED)
		elif(command[0].lower() == "score"):
			function_score(command[1])
		elif(command[0].lower() == "snp"):
			function_snp(command[1], command[2])
		elif(command[0].lower() == "massfit"):
			function_massfit(command[1], command[2], command[3], command[4], THREADED)
		elif(command[0].lower() == "unload"):
			function_unload(command[1])
		elif(command[0].lower() == "cross"):
			function_cross(command[1], command[2], THREADED)

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
	print()
	print(Fore.GREEN + "EnGENE-Terminal " + version)
	print(Fore.GREEN + "Genetic Enhancement Engine")
	print(Fore.GREEN + "by Henrique Frajacomo\n\n")

	print(__format_string("Models: \t\t\t\t\tShows all created models"))
	print(__format_string("Help: \t\t\t\t\tShows this help message"))
	print(__format_string("Quit: \t\t\t\t\tQuits EnGENE-Terminal"))
	print(__format_string("Clear: \t\t\t\t\tClears terminal screen"))
	print(__format_string("New: \t<modelname>\t<filename>\t\t\tLoads a new model"))
	print(__format_string("See: \t<modelname>\t\t\t\tChecks information about the model"))
	print(__format_string("Drop: \t<modelname>\t<col_index|index_list>\t\t\tDrops the columns specified"))
	print(__format_string("Select: \t<modelname>\t<start>\t<end>\t\tSets columns to be considered features in classifier"))
	print(__format_string("Target: \t<modelname>\t<col_name|col_index>\t\t\tSets the column to be predicted by the classifier"))
	print(__format_string("Unused: \t<modelname>\t\t\t\tPrints all columns outside feature space"))
	print(__format_string("Dummies: \t<modelname>\t\t\t\tCreates dummy variables in model feature space"))
	print(__format_string("GetClasses: \t<modelname>\t\t\t\tPrints all class values in target class"))
	print(__format_string("OVATransform: \t<modelname>\t<classname>\t\t\tPerforms a One-vs-All transformation in model data"))
	print(__format_string("Holdout: \t<modelname>\t<train%=0.9>\t<stratify=y/n>\t\tPerforms holdout in separating train\% of the dataset and stratifying or not"))
	print(__format_string("Fit: \t<modelname>\t<cpu_amount>\t\t\tTrains the model. Cpu=-1 uses all processor cores"))
	print(__format_string("Massfit: \t<modelname>\t<n_runs>\t<train%=0.9>\t<cpu_amount>\tDoes n FIT operations"))
	print(__format_string("Score: \t<modelname>\t\t\t\tPrints Mean Precision and Recall scores"))
	print(__format_string("Snp: \t<modelname>\t<n_elements>\t\t\tGets a ranked list of snps detected"))
	print(__format_string("Unload: \t<modelname>\t\t\t\tUnloads memory for model classifier. Keeps snps."))
	print(__format_string("Cross: \t<modelname>\t<model|models_list>\t\t\tCross references SNPs of similar models to improve SNP score"))

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

# Select function
def function_select(name, start, end):
	try:
		start = int(start)
		end = int(end)
	except ValueError:
		warning(-3, "Start and End values must be int")
		return

	if(__model_exist(name)):
		Model.models[name].set_feature_range(start, end)
	else:
		warning(-2, "Model not found") 

# Target function
def function_target(name, target):
	try:
		target = int(target)
	except:
		pass

	if(__model_exist(name)):
		Model.models[name].set_target_column(target)
	else:
		warning(-2, "Model not found") 	

# Dummies function - Recursive
def function_dummies(name, THREADED):
	if(not THREADED):
		if(__model_exist(name)):
			Model.models[name].create_dummies()
		else:
			warning(-2, "Model not found") 	
	else:
		Thread(target=function_dummies, args=(name, False)).start()

# GetClass function
def function_get_classes(name):
	if(__model_exist(name)):
		classes = Model.models[name].get_classes()
		for cl in classes:
			print(cl)
	else:
		warning(-2, "Model not found")

# One-vs-All transform function - Recursive
def function_ova_transform(name, cls, THREADED):
	if(not THREADED):
		if(__model_exist(name)):
			Model.models[name].one_vs_all_transform(cls)
		else:
			warning(-2, "Model not found")	
	else:
		Thread(target=function_ova_transform, args=(name, cls, False)).start()

# Holdout function - Recursive
def function_holdout(name, train, stratify, THREADED):
	if(not THREADED):
		if(__model_exist(name)):
			try:
				train = float(train)
			except ValueError:
				warning(-4, "Train% value must be a float between 0 and 1")
				return

			if(stratify.lower() == "n" or stratify.lower() == "no"):
				Model.models[name].holdout(train_s=train, stratify=False)
			else:
				Model.models[name].holdout(train_s=train)
		else:
			warning(-2, "Model not found")	
	else:
		Thread(target=function_holdout, args=(name, train, stratify, False)).start()

# Unused Columns
def function_unused(name):
		if(__model_exist(name)):
			aux = Model.models[name].print_non_features()
			for element in aux:
				print(element)
		else:
			warning(-2, "Model not found")	

# Fit function - Recursive
def function_fit(name, cpu, THREADED):
	if(not THREADED):
		if(__model_exist(name)):
			try:
				cpu = int(cpu)
			except ValueError:
				warning(-5, "Cpu must be int")
				return

			Model.models[name].fit(cpu=cpu)
		else:
			warning(-2, "Model not found")	
	else:
		Thread(target=function_fit, args=(name, cpu, False)).start()

# Score function
def function_score(name):
	if(__model_exist(name)):
		print(f'Mean Precision: {Model.models[name].get_mean_precision()}')
		print(f'Mean Recall: {Model.models[name].get_mean_recall()}')
	else:
		warning(-2, "Model not found")		

# SNP function
def function_snp(name, n):
	if(__model_exist(name)):
		try:
			n = int(n)
		except ValueError:
			warning(-5, "n_elements must be int")
			return

		Model.models[name].calculate_top_snps()
		aux = Model.models[name].get_top_snps(top=n)
		for element in aux:
			print(element)
	else:
		warning(-2, "Model not found")	

# Massfit function
def function_massfit(name, n, train, cpu, THREADED):
	if(not THREADED):
		if(__model_exist(name)):
			try:
				cpu = int(cpu)
				n = int(n)
			except ValueError:
				warning(-5, "Cpu and n must be int")
				return

			try:
				train = float(train)
			except ValueError:
				warning(-4, "Train% value must be a float between 0 and 1")
				return

			Model.models[name].mass_fit(n, train_s=train, cpu=cpu)
		else:
			warning(-2, "Model not found")	
	else:
		Thread(target=function_massfit, args=(name, n, train, cpu, False)).start()	

# Unload function
def function_unload(name):
	if(__model_exist(name)):
		Model.models[name].unload()
	else:
		warning(-2, "Model not found")	

# Cross function - Recursive
def function_cross(name, model, THREADED):
	if(not THREADED):
		if(not __model_exist(name)):
			warning(-2, f"Model {name} not found. Cross check has stopped")
			return


		# Single model
		if(model.count("[") == 0):
			if(not __model_exist(model)):
				warning(-2, f"Model {model} not found. Cross check has stopped")
				return

			scores = Model.models[name].cross_check_models(Model.models[model])

		# Multiple models
		else:
			# String parsing
			new_string = model.replace(" ", "").replace("[", "").replace("]", "").split(",")
			for mod in new_string:
				if(not __model_exist(mod)):
					warning(-2, f"Model {mod} not found. Cross check has stopped")
					return

			scores = Model.models[name].cross_check_models([Model.models[x] for x in new_string])

		print(Fore.CYAN + "Crossing process finished!")
		for element in scores:
			print(element)

	else:
		print(Fore.CYAN + "Crossing models in Threaded mode. Please do not modify the models until the process is finished!")
		sleep(0.01)
		Thread(target=function_cross, args=(name, model, False)).start()


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