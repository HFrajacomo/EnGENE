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

class Model:
	# Takes filename to build DataFrame
	def __init__(self, filename):
		# Dataset Atributes
		self.data = pd.read_csv(filename)
		self.target_column = None
		self.target_index = None
		self.feature_range = None
		
		# Classifier Atributes
		self.X_train = None
		self.X_test = None
		self.y_train = None
		self.y_test = None
		self.classifier = None
		self.precision = [0,0]
		self.recall = [0,0]
		self.importance = {}

	# Set target column for the predictor
	def set_target_column(self, name):
		index = 0
		if(name in self.data.columns):
			self.target_column = name
			for index in range(len(self.data.columns)):
				if(self.data.columns[index] == name):
					self.target_index = index
					break

		else:
			warning(1, "Column name doesn't exist")


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
			return

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
			return

		feature_names = []
		for i in range(self.feature_range[0], self.feature_range[1]+1):
			feature_names.append(self.data.columns[i])

		# Get Dummy variables
		self.data = pd.get_dummies(self.data, columns=feature_names)

		cols = self.data.columns.tolist()
		cols.remove(self.target_column)
		cols.append(self.target_column)
		self.data = self.data.reindex(columns=cols)

		self.feature_range[1] = len(cols)-(1+self.feature_range[0])

	# Drops unnecessary columns
	def destroy_column(self, column):
		if(type(column) == int):
			self.data = self.data.drop(self.data.columns[column], axis=1)
			self.__reindex(column)
		elif(type(column == list)):
			for i in range(len(column)):
				num = column.pop(0)
				self.data = self.data.drop(self.data.columns[num], axis=1)
				column = self.__reindex(num, column)
		else:
			error(1, "Argument must be int, list or string")

	# Auto-fix feature_range after deletion
	def __reindex(self, num, l=[]):
		if(num >= self.feature_range[0] and num <= self.feature_range[1]):
			self.feature_range[1] -= 1
		elif(num< self.feature_range[0]):
			self.feature_range[1] -= 1
			self.feature_range[0] -= 1

		for i in range(len(l)):
			if(l[i] >= num):
				l[i] -= 1
		return l

	# Separates data in holdout mode
	def holdout(self, train_s=0.9, stratify=True):
		if(self.feature_range == None):
			warning(4, "Feature range hasn't been set yet")
			return

		X = self.data[self.data.columns[self.feature_range[0]: self.feature_range[1]+1]]
		y = self.data[self.target_column]

		if(stratify):
			self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X,y, train_size=0.9, test_size=None, stratify=y, random_state=int(datetime.now().timestamp()))
		else:
			self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X,y, train_size=0.9, test_size=None, random_state=int(datetime.now().timestamp()))

	# Trains the RandomForest model.
	def fit(self, cpu=-1):
		if(type(self.X_train) != pd.DataFrame):
			error(2, "No data to fit. Use Model.holdout() before fitting data")

		# 10 + SNP%20 trees in the forest
		n_trees = (self.feature_range[1] - self.feature_range[0] + 1)%20 + 10

		self.classifier = RandomForestClassifier(n_estimators=n_trees, n_jobs=cpu)
		self.classifier.fit(self.X_train, self.y_train)

		# Makes prediction
		y_pred = self.classifier.predict(self.X_test)

		# Accumulates mean precision and recall
		self.precision[0] += precision_score(self.y_test, y_pred, average='micro')
		self.precision[1] += 1
		self.recall[0] += recall_score(self.y_test, y_pred, average='micro')
		self.recall[1] += 1

		# Get SNP importance
		most_important_snp = self.X_train.columns[int(np.argmax(self.classifier.feature_importances_))]

		if(most_important_snp in self.importance.keys()):
			self.importance[most_important_snp] += 1
		else:
			self.importance[most_important_snp] = 1


	# Calculates the mean precision of all runs of fit made up to now
	def get_mean_precision(self):
		if(self.precision[1] == 0):
			warning(5, "No runs where made to analyze precision. Try doing Model.fit() before trying again")
			return 0

		return self.precision[0]/self.precision[1]

	# Calculates the mean precision of all runs of fit made up to now
	def get_mean_recall(self):
		if(self.recall[1] == 0):
			warning(5, "No runs where made to analyze recall. Try doing Model.fit() before trying again")
			return 0

		return self.recall[0]/self.recall[1]

	# Returns the best ranked SNPs
	def get_top_snps(self, top=10):
		rank = []

		if(self.importance == {}):
			warning(6, "No ranking is being accumulated. Try Model.fit() before trying again")

		for e in self.importance.keys():
			rank.append([e, self.importance[e]])

		rank = sorted(rank, key=lambda x:x[1], reverse=True)

		if(top > len(rank)):
			return rank
		else:
			return rank[:top]

	# Runs Model.holdout() and Model.fit() n times
	def mass_fit(self, n, cpu=-1):
		for i in range(n):
			progress(f'{i}/{n}')
			self.holdout()
			self.fit(cpu)


m = Model('test.csv')
m.set_target_column("target")
m.set_feature_range(1,3)
m.one_vs_all_transform("B")
m.create_dummies()
m.destroy_column(0)
m.mass_fit(10)
print(m.get_mean_precision())
print(m.get_mean_recall())
print(m.get_top_snps())
