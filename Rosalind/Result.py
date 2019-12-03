class Result:
	results = {}

	def __init__(self, name, res, times_fit=0, other_models=None):
		self.modelname = name
		self.data = res
		self.times_fit = times_fit
		self.other_models = other_models

		if(other_models != None):
			self.modelname = "_multi_" + self.modelname

		Result.results[self.modelname] = self

	def pop(self):
		Result.results.pop(self.modelname)
		del(self)