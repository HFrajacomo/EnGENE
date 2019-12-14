class Result:
	results = {}

	def __init__(self, name, res, score, times_fit=0, other_models=None):
		self.modelname = name
		self.data = res
		self.times_fit = times_fit
		self.other_models = other_models
		self.score = score

		if(other_models != None):
			self.modelname = "_multi_" + self.modelname

		Result.results[self.modelname] = self

	def __repr__(self):
		print(self.modelname)
		print(self.times_fit)
		print(self.other_models)
		print()

	def __str__(self):
		return self.modelname + '\n' + str(self.times_fit) + '\n' + str(self.other_models) + '\n'

	def pop(self):
		Result.results.pop(self.modelname)
		del(self)

	# Takes a list of models to compare
	def cross_check_models(self, name):
		data = [Result.results[x].data for x in name]

		# score[0] = SNP, [1] = avg(importance), [2] = appearance multiplier 
		score = [x.copy() for x in self.data]
		for element in score:
			element.append(1)

		for i in range(len(score)):
			for mod in data:
				for el in mod:
					if(score[i][0] == el[0]):
						score[i][1] += el[1]
						score[i][2] += 0.3   # Gain multiplier
						break

		r = Result(self.modelname, self.__calculate_cross_check_multiplier(score), ["-","-"], times_fit="-", other_models=",".join(name[1:]))
		return r

	# Applies gain multiplier to all scores
	def  __calculate_cross_check_multiplier(self, scorelist):
		return sorted([[x[0], x[1]*x[2]] for x in scorelist], key=lambda x:x[1], reverse=True)
