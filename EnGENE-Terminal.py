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
		elif(command.lower() == ""):
			return
		else:
			warning(-6, f"Command {command} not found")
			return

	# Multi-argument commands
	if(type(command) == list):
		if(command[-1] == "&"):
			THREADED = True
			command.pop(-1)
		else:
			THREADED = False

		# Removes blank char
		pop = 0
		for i in range(len(command)):
			if(command[i] == ""):
				pop += 1
		for i in range(0, pop):
			command.remove("")

		n_args = len(command)-1

		if(command[0].lower() == "new"):
			if(n_args == 2):
				function_new(command[1], command[2], THREADED)
			else:
				warning(-7, "Syntax: new <modelname> <filename>")

		elif(command[0].lower() == "see"):
			if(n_args == 1):
				function_see(command[1], THREADED)
			else:
				warning(-7, "Syntax: see <modelname>")

		elif(command[0].lower() =="drop"):
			if(n_args == 2):
				function_drop(command[1], command[2], THREADED)
			else:
				warning(-7, "Syntax: drop <modelname> <column_index|list_of_indexes>")
		
		elif(command[0].lower() == "select"):
			if(n_args == 3):
				function_select(command[1], command[2], command[3])
			else:
				warning(-7, "Syntax: select <modelname> <startpos> <endpos>\nindexes always start at 0")

		elif(command[0].lower() == "target"):
			if(n_args == 2):
				function_target(command[1], command[2])
			else:
				warning(-7, "Syntax: target <modelname> <target_column_index|column_name>")

		elif(command[0].lower() == "dummies"):
			if(n_args == 1):
				function_dummies(command[1], THREADED)
			else:
				warning(-7, "Syntax: dummies <modelname>")

		elif(command[0].lower() == "getclasses"):
			if(n_args == 1):
				function_get_classes(command[1])
			else:
				warning(-7, "Syntax: getclasses <modelname>")

		elif(command[0].lower() == "ovatransform"):
			if(n_args == 2):
				function_ova_transform(command[1], command[2], THREADED)
			else:
				warning(-7, "Syntax: ovatransform <modelname> <target_class>")

		elif(command[0].lower() == "holdout"):
			if(n_args == 3):
				function_holdout(command[1], command[2], command[3], THREADED)
			elif(n_args == 2 and __isfloat(command[2])):
				function_holdout(command[1], command[2], "y", THREADED)
				warning(-8, "Holdout defaulted Stratify=y")
			elif(n_args == 2 and not __isfloat(command[2])):
				function_holdout(command[1], "0.9" , command[2], THREADED)
				warning(-8, "Holdout defaulted Train%=0.9")
			elif(n_args == 1):
				function_holdout(command[1], "0.9" , "y", THREADED)				
				warning(-8, "Holdout defaulted Train%=0.9 and Stratify=y")
			else:
				warning(-7, "Syntax: holdout <modelname> <train%=0.9> <stratify=y>")

		elif(command[0].lower() == "unused"):
			if(n_args == 1):
				function_unused(command[1])
			else:
				warning(-7, "Syntax: unused <modelname>")

		elif(command[0].lower() == "fit"):
			if(n_args == 2):
				function_fit(command[1], command[2], THREADED)
			elif(n_args == 1):
				function_fit(command[1], "-1", THREADED)
				warning(-8, "Fit defaulted cpu=-1")
			else:
				warning(-7, "Syntax: fit <modelname> <cpu=-1>")

		elif(command[0].lower() == "score"):
			if(n_args == 1):
				function_score(command[1])
			else:
				warning(-7, "Syntax: score <modelname>")

		elif(command[0].lower() == "snp"):
			if(n_args == 2):
				function_snp(command[1], command[2])
			elif(n_args == 1):
				function_snp(command[1], None)
				warning(-8, "Snp defaulted to top='all'")
			else:
				warning(-7, "Syntax: snp <modelname> <rank_positions=[shows all]>")

		elif(command[0].lower() == "massfit"):
			if(n_args == 4):
				function_massfit(command[1], command[2], command[3], command[4], THREADED)
			elif(n_args == 3):
				function_massfit(command[1], command[2], command[3], "-1", THREADED)
				warning(-8, "Massfit defaulted cpu=-1")
			elif(n_args == 2):
				function_massfit(command[1], command[2], "0.9", "-1", THREADED)
				warning(-8, "Massfit defaulted cpu=-1 and train%=0.9")
			elif(n_args == 1):
				function_massfit(command[1], "1000", "0.9", "-1", THREADED)
				warning(-8, "Massfit defaulted cpu=-1 and train%=0.9 and n_runs=1000")
			else:
				warning(-7, "Syntax: massfit <modelname> <n_runs=1000> <train%=0.9> <cpu=-1>")

		elif(command[0].lower() == "unload"):
			if(n_args == 1):
				function_unload(command[1])
			else:
				warning(-7, "Syntax: unload <modelname>")

		elif(command[0].lower() == "cross"):
			if(n_args == 3):
				function_cross(command[1], command[2], command[3], THREADED)
			elif(n_args == 2):
				function_cross(command[1], command[2], None, THREADED)
				warning(-8, "Cross defaulted top_rank=all")
			else:
				warning(-7, "Syntax: cross <basemodel> <model|list_of_models>")

		elif(command[0].lower() == "print"):
			if(n_args == 1):
				function_print(command[1])
			else:
				warning(-7, "Syntax: print <modelname>")

		elif(command[0].lower() == "save"):
			if(n_args == 1):
				function_save(command[1])
			else:
				warning(-7, "Syntax: save <modelname>")


			'''
			Simplified commands for non-Computer Scientists
			'''

		elif(command[0].lower() == "load"):
			if(n_args == 6):
				function_load(command[1], command[2], command[3], command[4], command[5], command[6], THREADED)
			elif(n_args == 5):
				warning(-8, "Load defaulted target class to None. Therefore it won't perform OVATransform. Note that future warning or errors may occur because of that!")
				function_load(command[1], command[2], command[3], command[4], command[5], None, THREADED)
			else:
				warning(-7, "Syntax: load <input_name> <filename> <column_of_first_SNP> <column_of_last_SNP> <target_feature_column>")
		else:
			warning(-6, f"Command {command[0]} not found")
			return

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

	print(Fore.RED + "Useful Commands")
	print(__format_string("Models: \t\t\t\t\tShows all created models"))
	print(__format_string("Help: \t\t\t\t\tShows this help message"))
	print(__format_string("Quit: \t\t\t\t\tQuits EnGENE-Terminal"))
	print(__format_string("Clear: \t\t\t\t\tClears terminal screen"))
	print(__format_string("Print: \t<modelname>\t\t\t\tRough visualization of model data"))
	print(__format_string("Unused: \t<modelname>\t\t\t\tPrints all columns outside feature space"))
	print(__format_string("GetClasses: \t<modelname>\t\t\t\tPrints all class values in target class"))

	print(Fore.RED + "Model I/O")	
	print(__format_string("New: \t<modelname>\t<filename>\t\t\tLoads a new model"))
	print(__format_string("See: \t<modelname>\t\t\t\tChecks information about the model"))
	print(__format_string("Save: \t<modelname>\t\t\t\tSaves Model data to a new dataset in Saved_Models folder"))

	print(Fore.RED + "Model Configuration")
	print(__format_string("Drop: \t<modelname>\t<col_index|index_list>\t\t\tDrops the columns specified"))
	print(__format_string("Select: \t<modelname>\t<start>\t<end>\t\tSets columns to be considered features in classifier"))
	print(__format_string("Target: \t<modelname>\t<col_name|col_index>\t\t\tSets the column to be predicted by the classifier"))

	print(Fore.RED + "Model Transformations")
	print(__format_string("Dummies: \t<modelname>\t\t\t\tCreates dummy variables in model feature space"))	
	print(__format_string("OVATransform: \t<modelname>\t<classname>\t\t\tPerforms a One-vs-All transformation in model data"))
	print(__format_string("Unload: \t<modelname>\t\t\t\tUnloads memory for model classifier. Keeps snps."))
	
	print(Fore.RED + "Model Training")
	print(__format_string("Holdout: \t<modelname>\t<train%=0.9>\t<stratify=y/n>\t\tPerforms holdout in separating train\% of the dataset and stratifying or not"))
	print(__format_string("Fit: \t<modelname>\t<cpu_amount=-1>\t\t\tTrains the model. Cpu=-1 uses all processor cores"))
	print(__format_string("Massfit: \t<modelname>\t<n_runs=1000>\t<train%=0.9>\t<cpu=-1>\tDoes n FIT operations"))
	print(__format_string("Score: \t<modelname>\t\t\t\tPrints Mean Precision and Recall scores"))
	print(__format_string("Snp: \t<modelname>\t<n_elements=[all]>\t\t\tGets a ranked list of snps detected"))
	print(__format_string("Cross: \t<modelname>\t<model|models_list>\t<top_rank=10>\t\tCross references SNPs of similar models to improve SNP score"))

	print()
	print(Fore.RED + "!!!!!! SIMPLIFIED COMMANDS !!!!!!")
	# Load
	print(Fore.GREEN + "Load Command\n")
	print("Description: Loads and prepares a model based on an input dataset and user-given information")
	print("Syntax: Load <name> <filename> <feature_space_start> <feature_space_end> <target_column> <target_class>?\n")
	print("Name: The name to be given to the new model\nFilename: Path to input dataset\nFeature_space_start: An integer that represents the column index of the first SNP. Starts at 0.")
	print("Feature_space_end: An integer that represents the column index of the last SNP. Starts at 0.\nTarget_column: The column name or integer representing the column index of the investigated feature")
	print("Target_class: The specific value of the target column that wants to be discovered (ignore if there are only two classes)\n")
	print("Example: Load test_model models/test.csv 1 10 growth_speed fast\n")

# Formats to table view
def __format_string(text):
	text = text.split("\t")
	out_string = ""

	for t in text:
		out_string += "{:<15}".format(t)
	return out_string

# Checks if string can be converted to float
def __isfloat(text):
	try:
		text = float(text)
		return True
	except ValueError:
		return False

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
		if(n != None):
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
def function_cross(name, model, top, THREADED):
	if(not THREADED):
		if(not __model_exist(name)):
			warning(-2, f"Model {name} not found. Cross check has stopped")
			return

		if(top != None):
			try:
				top = int(top)
			except ValueError:
				warning(-4, f"Top value has to be an integer")
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

		if(top == None):
			for element in scores:
				print(element)
		else:
			for element in scores[:top]:
				print(element)

	else:
		print(Fore.CYAN + "Crossing models in Threaded mode. Please do not modify the models until the process is finished!")
		sleep(0.01)
		Thread(target=function_cross, args=(name, model, False)).start()

# Print function
def function_print(name):
	if(__model_exist(name)):
		print(Model.models[name].data)
	else:
		warning(-2, "Model not found")	

# Save function
def function_save(name):
	if(__model_exist(name)):
		Model.models[name].save_to_csv()
	else:
		warning(-2, "Model not found")		

'''
Simplified commands implementation
'''

# Loads and configures model - Recursive
def function_load(name, filename, start, end, target, target_class, THREADED):
	if(not THREADED):
		try:
			start = int(start)
			end = int(end)
		except ValueError:
			warning(-5, "Start and End position must be int")
			return

		try:
			target = int(target)
		except ValueError:
			pass

		Model(name, filename)
		Model.models[name].set_target_column(target)
		Model.models[name].set_feature_range(start, end)

		if(target_class == None and len(Model.models[name].get_classes()) != 2):
			warning(-9, "Model cannot be loaded because target_class wasn't set. Please set the class or perform OVATransform command on your model")
			return
		elif(target_class != None):
			Model.models[name].one_vs_all_transform(target_class)

		Model.models[name].create_dummies()

	else:
		Thread(target=function_load, args=(name, filename, start, end, target, target_class, False)).start()					



# Welcome Message
def welcome():
	print(Fore.GREEN + "EnGENE-Terminal " + version)
	print(Fore.GREEN + "Genetic Enhancement Engine")
	print(Fore.GREEN + "by Henrique Frajacomo\n")

version = "v1.0"

'''
Main 
'''
def main():
	try:
		welcome()
		while(True):
			print("\nEnGENE-Terminal> ", end="")
			data = parse(input())
			command_handler(data)

	except KeyboardInterrupt:
		exit()



if(__name__ == '__main__'):
	main()

