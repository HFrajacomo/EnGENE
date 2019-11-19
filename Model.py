'''
Model class is used to store the data table and Random Forest prediction model
Everything related to data and learning is in here
'''

import pandas as pd
from ErrorHandling import *

class Model:
	# Takes filename to build DataFrame
	def __init__(self, filename):
		self.data = pd.read_csv(filename)
		self.target_column = None
		self.target_index = None
		self.feature_range = None

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
		cols.append(cols.pop(self.feature_range[1]-self.feature_range[0]))
		self.data = self.data.reindex(columns=cols)

'''
Test

m = Model('test.csv')
m.set_target_column("target")
m.set_feature_range(1,2)
m.one_vs_all_transform("B")
m.create_dummies()
print(m.data)
'''