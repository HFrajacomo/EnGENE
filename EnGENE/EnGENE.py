'''
Model class is used to store the data table and Random Forest prediction model
Everything related to data and learning is in here
'''

import pandas as pd
import numpy as np
from datetime import datetime
from ErrorHandling import *
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score
import os

class Model:
	models = {}
	# Takes filename to build DataFrame
	def __init__(self, modelname, filename):
		# Dataset Atributes
		self.modelname = modelname
		self.filename = filename

		try:
			self.data = pd.read_csv(filename)
		except FileNotFoundError:
			warning(0, f"File {filename} not found")
			return

		self.target_column = None
		self.target_index = None
		self.feature_range = None
		
		# Classifier Atributes
		self.X_train = None
		self.X_test = None
		self.y_train = None
		self.y_test = None
		self.classifier = None
		self.precision = 0
		self.recall = 0
		self.importance = {}
		self.times_fit = 0

		# Top SNPs in model
		self.top_snps = []

		Model.models[modelname] = self

	# Set target column for the predictor
	def set_target_column(self, indicator):
		index = 0
		if(type(indicator) == str):
			if(indicator in self.data.columns):
				self.target_column = indicator
				for index in range(len(self.data.columns)):
					if(self.data.columns[index] == indicator):
						self.target_index = index
						break

			else:
				warning(1, "Column name doesn't exist")

		elif(type(indicator) == int):
			if(abs(indicator) < len(self.data.columns)):
				self.target_column = self.data.columns[indicator]
				self.target_index = indicator
			else:
				warning(1, "Column index is out of range")

		else:
			warning(1, f"Type {type(indicator)} is not accepted. Try string or int.")


	# Returns all distinct classes in Model.target_column
	def get_classes(self):
		if(self.target_column == None):
			warning(2, "Target class hasn't been set yet")
			return

		class_names = []

		for i in range(0, len(self.data.count(axis=1))):
			item = self.data[self.target_column][i]
			if(item not in class_names):
				class_names.append(self.data[self.target_column][i])

		return class_names

	# Changes all classes except the target to "Other"
	def one_vs_all_transform(self, target_class):
		if(self.target_column == None):
			warning(2, "Target class hasn't been set yet")
			return 0

		for i in range(len(self.data[self.target_column])):
			if(self.data.iat[i, self.target_index] != target_class):
				self.data.iat[i, self.target_index] = "Other" 

	# Sets what features are considered features
	def set_feature_range(self, start, end):
		if(start >= 0 and end >= 0 and start < len(self.data.columns) and end < len(self.data.columns)):
			self.feature_range = [start, end]
		else:
			warning(3, "Invalid start or end position to feature range")

	# Transform categorical features to a set of binary ones
	def create_dummies(self):
		if(self.feature_range == None):
			warning(4, "Feature range hasn't been set yet")
			return 0

		original_size = len(self.data.columns)-1

		feature_names = []
		for i in range(self.feature_range[0], self.feature_range[1]+1):
			feature_names.append(self.data.columns[i])

		# Get Dummy variables
		self.data = pd.get_dummies(self.data, columns=feature_names)

		cols = self.data.columns.tolist()
		cols.remove(self.target_column)
		cols.append(self.target_column)
		self.data = self.data.reindex(columns=cols)

		self.feature_range[0] += (original_size - self.feature_range[1]) - 1
		self.feature_range[1] = len(cols)-2

	# Drops unnecessary columns
	def destroy_column(self, column):
		dropped_names = []

		if(type(column) == int):
			dropped_names.append(self.data.columns[column])
			self.data = self.data.drop(self.data.columns[column], axis=1)
			self.__reindex(column)

			return dropped_names

		elif(type(column == list)):
			for i in range(len(column)):
				num = column.pop(0)
				dropped_names.append(self.data.columns[num])
				self.data = self.data.drop(self.data.columns[num], axis=1)
				column = self.__reindex(num, column)
			return dropped_names

		else:
			error(1, "Argument must be int, list")

	# Auto-fix feature_range after deletion
	def __reindex(self, num, l=[]):
		if(self.feature_range != None):
			if(num >= self.feature_range[0] and num <= self.feature_range[1]):
				self.feature_range[1] -= 1
			elif(num< self.feature_range[0]):
				self.feature_range[1] -= 1
				self.feature_range[0] -= 1

		for i in range(len(l)):
			if(l[i] >= num):
				l[i] -= 1
		return l

	# Returns all columns outside feature_range
	def print_non_features(self):
		if(self.feature_range == None):
			warning(4, "Feature range hasn't been set yet")
			return

		aux = []
		in_range = set(range(self.feature_range[0], self.feature_range[1]+1))
		out_range = set(range(0, len(self.data.columns)))
		out_range = out_range - in_range

		for index in out_range:
			aux.append([index, self.data.columns[index]])

		return aux

	# Separates data in holdout mode
	def holdout(self, train_s=0.9, stratify=True):
		if(self.feature_range == None):
			warning(4, "Feature range hasn't been set yet")
			return 0

		# Check if data is binary
		if(len(self.get_classes()) != 2):
			warning(7, "Target feature is not binary. Try Model.one_vs_all_transform()")
			return 0

		X = self.data[self.data.columns[self.feature_range[0]: self.feature_range[1]+1]]
		y = self.data[self.target_column]

		if(stratify):
			self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X,y, train_size=train_s, test_size=None, stratify=y, random_state=int(datetime.now().timestamp()))
		else:
			self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X,y, train_size=train_s, test_size=None, random_state=int(datetime.now().timestamp()))

	# Trains the RandomForest model.
	def fit(self, cpu=-1):
		if(type(self.X_train) != pd.DataFrame):
			warning(2, "No data to fit. Use Model.holdout() before fitting data")

		# 10 + SNP%20 trees in the forest
		n_trees = (self.feature_range[1] - self.feature_range[0] + 1)%20 + 10

		self.classifier = RandomForestClassifier(n_estimators=n_trees, n_jobs=cpu)
		
		# Fix for empty list pop inside sklearn
		while(True):
			try:
				try:
					self.classifier.fit(self.X_train, self.y_train)
					break
				except ValueError:
					warning(9, "Feature space isn't binary. Try Model.create_dummies() and Model.holdout() before fitting")
					return 0
			except IndexError:
				pass

		# Makes prediction
		y_pred = self.classifier.predict(self.X_test)

		# Accumulates mean precision and recall
		self.precision += precision_score(self.y_test, y_pred, average='micro')
		self.times_fit += 1
		self.recall += recall_score(self.y_test, y_pred, average='micro')

		# Get SNP importance
		most_important_snp = self.X_train.columns[int(np.argmax(self.classifier.feature_importances_))].split("_")[0]

		if(most_important_snp in self.importance.keys()):
			self.importance[most_important_snp] += 1
		else:
			self.importance[most_important_snp] = 1


	# Calculates the mean precision of all runs of fit made up to now
	def get_mean_precision(self):
		if(self.precision == 0):
			warning(5, "No runs where made to analyze precision. Try doing Model.fit() before trying again")
			return 0

		return self.precision/self.times_fit

	# Calculates the mean precision of all runs of fit made up to now
	def get_mean_recall(self):
		if(self.recall == 0):
			warning(5, "No runs where made to analyze recall. Try doing Model.fit() before trying again")
			return 0

		return self.recall/self.times_fit

	# Calculates the best ranked SNPs in a fitted model
	def calculate_top_snps(self):
		rank = []

		if(self.importance == {}):
			warning(6, "No ranking is being accumulated. Try Model.fit() before trying again")

		for e in self.importance.keys():
			rank.append([e, self.importance[e]])

		rank = sorted(rank, key=lambda x:x[1], reverse=True)

		self.top_snps = rank

	# Get top SNPs until top element
	def get_top_snps(self, top=10):
		if(top == None):
			return self.top_snps
		else:
			return self.top_snps[:top]

	# Runs Model.holdout() and Model.fit() n times
	def mass_fit(self, n, train_s=0.9, stratify=True, cpu=-1):
		for i in range(n):
			progress(f'{i}/{n}')
			errcode = self.holdout(train_s=train_s, stratify=stratify)

			if(errcode == 0):
				warning(8, "Too many classes in target column. Try running an OVATransform")
				return 0

			errcode = self.fit(cpu)

			if(errcode == 0):
				warning(10, "Massfit failed because of accumulated warnings")
				return
		print("Training of model " + self.modelname + " is done!")

	# Cross checks important SNPs on similar data models
	'''
		This is an extremely powerful method of post-processing.
		It has been confirmed in experiments that having multiple datasets of genotypes
			harvested in different places and dates can yield different SNP importances.
			The Cross checking of the trained models can analyze similarities in found SNPs,
			thus, giving a better understanding of their importances in a macro scale.
	'''
	# Takes a list of models to compare
	def cross_check_models(self, model):
		if(type(model) != Model and type(model) != list):
			error(3, f"{type(model)} received on cross_check_models(). Try using a Model or list of models.")
		if(self.top_snps == []):
			self.calculate_top_snps()


		# score[0] = SNP, [1] = avg(importance), [2] = appearance multiplier 
		score = self.top_snps.copy()
		for element in score:
			element.append(1)


		if(type(model) == Model):
			if(model.top_snps == []):
				model.calculate_top_snps()

			for i in range(len(score)):
				for el in model.top_snps:
					if(score[i][0] == el[0]):
						score[i][1] += el[1]
						score[i][2] += 0.3  # Gain multiplier
						break

		else:
			for i in range(len(score)):
				for mod in model:
					if(mod.top_snps == []):
						mod.calculate_top_snps()

					for el in mod.top_snps:
						if(score[i][0] == el[0]):
							score[i][1] += el[1]
							score[i][2] += 0.3   # Gain multiplier
							break

		return self.__calculate_cross_check_multiplier(score)						

	# Applies gain multiplier to all scores
	def  __calculate_cross_check_multiplier(self, scorelist):
		return sorted([[x[0], x[1]*x[2]] for x in scorelist], key=lambda x:x[1], reverse=True)

	# Deletes all data concerning the classifier
	# Turns model into a read-only object to read self.top_snps
	def unload(self):
		self.data = None
		self.target_column = None
		self.target_index = None
		self.feature_range = None
		self.X_train = None
		self.X_test = None
		self.y_train = None
		self.y_test = None
		self.classifier = None

	# Padding for __repr__
	def __format_string(self, text):
		return '{:<20}'.format(text)

	# Terminal print of Model class
	def __repr__(self):
		text = self.modelname + "\n"
		text += self.__format_string("Filename: ") + f'{self.filename}\n'
		text += self.__format_string("Target Feature: ") + f'{self.target_column}\n'
		text += self.__format_string("Feature Range: ") + f'{self.feature_range}\n'
		text += self.__format_string("Times Trained: ") + f'{self.times_fit}'

		if(type(self.data) == pd.DataFrame):
			text += "\n" + self.__format_string("Dataframe size: ") + f'{len(self.data)}x{len(self.data.columns)}'
		if(type(self.X_train) == pd.DataFrame):
			text += "\n" + self.__format_string("Holdout: ") + f'{len(self.X_train)}' + " instances in training set"
		if(self.times_fit > 0):
			text += "\n" + self.__format_string("Precision: ") + '{0:.5f}'.format(self.get_mean_precision())
			text += "\n" + self.__format_string("Recall: ") + '{0:.5f}'.format(self.get_mean_recall())
		return text

	# Saved Model.data to a new .csv file
	def save_to_csv(self):
		# Creates save dir
		if(os.name == 'nt' and not os.path.isdir("Saved_Models")):
			os.system("mkdir Saved_Models")
		elif(os.name != 'nt' and not os.path.isdir("Saved_Models")):
			os.system("mkdir Saved_Models")

		if(os.name == 'nt'):
			self.data.to_csv("Saved_Models\\Model_" + self.modelname + ".csv", header=self.data.columns, index=False)
		else:
			self.data.to_csv("Saved_Models/Model_" + self.modelname + ".csv", header=self.data.columns, index=False)