__author__ = "Henrique Frajacomo"

import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThreadPool, QRunnable, pyqtSignal, pyqtSlot, QObject, QThread
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QTableWidgetItem
from easygui import *
import os

sys.path.append('EnGENE\\')
sys.path.append('EnGENE/')
sys.path.append('Rosalind\\')
sys.path.append('Rosalind/')

from EnGENE import Model
from Window import Ui_MainWindow
from Result import Result

# Warning Supress function
def warn(*args, **kwargs):
    pass

import warnings
warnings.warn = warn


class Win(QtWidgets.QMainWindow, Ui_MainWindow):
	def __init__(self):
		super(Win, self).__init__()
		self.setupUi(self)
		self.setup_pywin()
		self.threads = QThreadPool()

	# Setup GUI-Python integration
	def setup_pywin(self):
		self.pushButton.clicked.connect(self.click_new)
		self.toolButton.clicked.connect(self.click_tool)
		self.tableWidget.setRowCount(0)
		self.tableWidget.setColumnCount(3)
		self.tableWidget.setHorizontalHeaderLabels(["Model name", "Filename", "Status"])
		self.tableWidget.resizeColumnsToContents()
		self.tableWidget.resizeRowsToContents()
		self.tableWidget_2.setRowCount(0)
		self.tableWidget_2.setColumnCount(5)		
		self.tableWidget_2.setHorizontalHeaderLabels(["Result name", "Precision", "Recall", "Times Trained", "Associated Models"])
		self.tableWidget_2.resizeColumnsToContents()
		self.tableWidget_2.resizeRowsToContents()
		self.tableWidget_3.setRowCount(0)
		self.tableWidget_3.setColumnCount(2)		
		self.tableWidget_3.setHorizontalHeaderLabels(["SNP ID", "Score"])
		self.tableWidget_3.resizeColumnsToContents()
		self.tableWidget_3.resizeRowsToContents()

		self.tableWidget.itemSelectionChanged.connect(lambda:self.model_selection_trigger(self.tableWidget.selectedItems()))
		self.tableWidget_2.itemSelectionChanged.connect(lambda:self.fill_results(self.tableWidget_2.selectedItems()))
		self.spinBox_2.valueChanged.connect(self.spinbox_end_change)
		self.spinBox_3.valueChanged.connect(self.spinbox_start_change)
		self.spinBox_4.valueChanged.connect(self.spinbox_target_change)
		self.pushButton_2.clicked.connect(self.click_select)
		self.pushButton_7.clicked.connect(self.click_target)
		self.textBrowser.setFontPointSize(11)
		self.pushButton_3.clicked.connect(self.click_dummy)
		self.spinBox_5.valueChanged.connect(self.spinbox_ova_change)
		self.pushButton_4.clicked.connect(self.click_ova)
		self.set_train_menu()
		self.toolButton_2.menu().triggered.connect(self.change_percentage)
		self.pushButton_5.clicked.connect(self.click_train)
		self.pushButton_6.clicked.connect(self.click_unload)
		header = self.tableWidget.horizontalHeader()
		header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
		header2 = self.tableWidget_2.horizontalHeader()
		header2.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
		header3 = self.tableWidget_3.horizontalHeader()
		header3.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)

	# Checks if a model with name exists
	def __model_exist(self, name):
		if(type(Model.models.get(name, False)) == Model):
			return True
		else:
			return False

	# New Button Function
	def click_new(self):
		w = Worker("new", self.lineEdit.displayText())
		w.signals.finished_new.connect(self.set_table)
		self.threads.start(w)

	# Sets an item in QTableWidget
	def set_table(self, item1, item2, item3):
		self.update_text_browser()
		self.reset_spinboxes()
		item1 = QTableWidgetItem(item1)
		item2 = QTableWidgetItem(item2)
		item3 = QTableWidgetItem(item3)
		if(item3.text() == "Not Ready"):
			item3.setForeground(QColor(255,0,0))
		else:
			item3.setForeground(QColor(0,255,0))

		self.tableWidget.setRowCount(self.tableWidget.rowCount()+1)
		self.tableWidget.setItem(self.tableWidget.rowCount()-1,0, item1)
		self.tableWidget.setItem(self.tableWidget.rowCount()-1,1, item2)
		self.tableWidget.setItem(self.tableWidget.rowCount()-1,2, item3)

	# New function tool button
	def click_tool(self):
		global loaded_dataset
		loaded_dataset = fileopenbox(title="Load dataset", filetypes=["*.csv"], default="*.csv")

		if(loaded_dataset == None):
			loaded_dataset = ""

		self.lineEdit_2.setText(loaded_dataset)

	# Updates Model Information screen
	# Triggers for every model selection change
	def update_text_browser(self):
		if(not self.__model_exist(currently_selected_model)):
			self.textBrowser.setText("")
		else:
			self.textBrowser.setText(str(Model.models[currently_selected_model]))

	# Triggers every mouse selection in Model list
	def model_selection_trigger(self, modelname):
		global currently_selected_model
		global all_selected_models

		if(modelname == []):
			return

		elif(type(modelname) == list):
			all_selected_models = [x for x in modelname[::3]]
			currently_selected_model = modelname[-3].text()

		else:
			currently_selected_model = modelname

		self.reset_spinboxes()
		self.update_text_browser()
		self.toggle_train_tag()

	# Re-set all spinbox values
	def reset_spinboxes(self):
		self.spinBox_2.setMaximum(self.get_max_spinbox())
		self.spinBox_3.setMaximum(self.get_max_spinbox())
		self.spinBox_4.setMaximum(self.get_max_spinbox())
		self.spinBox_2.setValue(0)
		self.spinBox_3.setValue(0)
		self.spinBox_4.setValue(0)
		self.spinBox_5.setValue(0)
		self.lineEdit_3.setText("")
		self.lineEdit_4.setText("")
		self.lineEdit_5.setText("")	
		self.lineEdit_6.setText("")

		if(currently_selected_model != ""):
			if(not self.__model_exist(currently_selected_model)):
				return
			if(Model.models[currently_selected_model].target_column != None):
				self.spinBox_5.setMaximum(self.get_max_spinbox_class())

	# Gets maximum number of Select and Target Spinboxes
	def get_max_spinbox(self):
		if(currently_selected_model == ""):
			return 0
		if(not self.__model_exist(currently_selected_model)):
			return 0
		return len(Model.models[currently_selected_model].data.columns)-1

	# Gets maximum number of Select to OVA Spinbox
	def get_max_spinbox_class(self):
		if(currently_selected_model == ""):
			return 0
		if(not self.__model_exist(currently_selected_model)):
			return 0
		return len(Model.models[currently_selected_model].get_classes())-1	

	# Gets the header related to n element
	def get_spinbox_header(self, n):
		if(currently_selected_model == ''):
			return ""
		return Model.models[currently_selected_model].data.columns[n]

	def spinbox_end_change(self, q):
		self.lineEdit_4.setText(self.get_spinbox_header(q))
	def spinbox_start_change(self, q):
		self.lineEdit_3.setText(self.get_spinbox_header(q))
	def spinbox_target_change(self, q):
		self.lineEdit_5.setText(self.get_spinbox_header(q))
	def spinbox_ova_change(self, q):
		self.lineEdit_6.setText(Model.models[currently_selected_model].get_classes()[q])

	# Select button click
	def click_select(self):
		if(currently_selected_model != ""):
			Model.models[currently_selected_model].set_feature_range(self.spinBox_3.value(), self.spinBox_2.value())
		self.update_text_browser()

	# Target button click
	def click_target(self):
		if(currently_selected_model != ""):
			Model.models[currently_selected_model].set_target_column(self.spinBox_4.value())
		self.update_model_status(currently_selected_model)
		self.update_text_browser()

	# Dummification button click
	def click_dummy(self):
		w = Worker("dummy")
		w.signals.finished_dummy_ova.connect(self.set_dummy_ova)
		self.threads.start(w)

	# Set dummies and ova post processing
	def set_dummy_ova(self, modelname):
		self.update_text_browser()
		self.reset_spinboxes()
		self.update_model_status(modelname)

	# OVA button click
	def click_ova(self):
		w = Worker("ova", self.lineEdit_6.text())
		w.signals.finished_dummy_ova.connect(self.set_dummy_ova)
		self.threads.start(w)

	# Changes percentage of training
	def change_percentage(self, q):
		self.toolButton_2.setText(q.text())		

	# Creates Train Percentage menu
	def set_train_menu(self):
		menu = QtWidgets.QMenu()

		for i in range(1, 10):
			act = menu.addAction(str(i*10) + "%")
		menu.setDefaultAction(act)
		self.toolButton_2.setText("90%")
		self.toolButton_2.setMenu(menu)

	# Train button click
	def click_train(self):
		# Cancel operation
		if(Worker.thread_control.get(currently_selected_model, False) != False):
			Worker.thread_control.pop(currently_selected_model)
			self.toggle_train_tag()

		# Train operation
		else:
			w = Worker("train", int(self.spinBox.text()), int(self.toolButton_2.text()[:-1])/100, self.radioButton.isChecked())
			w.signals.update_info.connect(self.update_text_browser)
			w.signals.update_list.connect(self.training_update)
			w.signals.finished_training.connect(self.training_post_process)
			Worker.thread_control[currently_selected_model] = True
			self.toggle_train_tag()
			self.threads.start(w)

	# After training processing
	def training_post_process(self, name, other):
		self.toggle_train_tag(name)
		self.add_result(name, other)

	# Changes Train button tag
	def toggle_train_tag(self, name=None):
		if(name == None):
			if(Worker.thread_control.get(currently_selected_model, False) != False):
				self.pushButton_5.setText("Stop Training")
				self.update_model_status(currently_selected_model)
			else:
				self.pushButton_5.setText("Train")
				self.update_model_status(currently_selected_model)
		else:
			if(Worker.thread_control.get(name, False) != False):
				self.pushButton_5.setText("Stop Training")
				self.update_model_status(name)
			else:
				self.pushButton_5.setText("Train")
				self.update_model_status(name)			

	# Unload button click
	def click_unload(self):
		global all_selected_models
		global currently_selected_model

		for md in all_selected_models:
			Model.models.pop(md.text())

		delete_list = []

		for i in range(self.tableWidget.rowCount()):
			if(self.tableWidget.item(i,0).text() in [x.text() for x in all_selected_models]):
				delete_list.append(i)

		delete_list = sorted(delete_list)
		currently_selected_model = ""
		all_selected_models = []
		self.textBrowser.setText("")

		for ind in delete_list:
			self.tableWidget.removeRow(ind)
			for i in range(len(delete_list)):
				delete_list[i] -= 1	

	# Returns model row index in Model list
	def get_row(self, modelname):
		for i in range(0, self.tableWidget.rowCount()):
			if(self.tableWidget.item(i,0).text() == modelname):
				return i
		return -1

	# Updates the state of a model in model list
	def update_model_status(self, modelname):
		index = self.get_row(modelname)

		if(Model.models[modelname].binary_feature_space and Model.models[modelname].binary_target_space):
			self.tableWidget.item(index,2).setText("Ready")
			self.tableWidget.item(index,2).setForeground(QColor(0,255,0))
		else:
			self.tableWidget.item(index,2).setText("Not Ready")
			self.tableWidget.item(index,2).setForeground(QColor(255,0,0))

	# Updates training routine
	def training_update(self, modelname, value):
		index = self.get_row(modelname)
		self.tableWidget.item(index,2).setText(value)
		self.tableWidget.item(index,2).setForeground(QColor(0,0,255))

	# Add result to results list
	def add_result(self, name, other):
		r = Result.results[name]

		items = []
		items.append(QTableWidgetItem(r.modelname))
		items.append(QTableWidgetItem('{0:.3f}'.format(r.score[0]*100) + '%'))
		items.append(QTableWidgetItem('{0:.3f}'.format(r.score[1]*100) + '%'))
		items.append(QTableWidgetItem(str(r.times_fit)))
		items.append(QTableWidgetItem(str(r.other_models).replace("[", "").replace("]", "")))

		if(self.__result_exists(name, other)):
			index = self.get_row_result(name) 
			i = 0
			for el in items:
				self.tableWidget_2.setItem(index, i, el)
				i += 1
		else:
			self.tableWidget_2.setRowCount(self.tableWidget_2.rowCount()+1)
			i = 0
			for el in items:
				self.tableWidget_2.setItem(self.tableWidget_2.rowCount()-1, i, el)
				i += 1

	# Checks if a Result already exists
	def __result_exists(self, name, other):
		other = other.replace("[", "").replace("]", "").split(",")

		for i in range(0, self.tableWidget_2.rowCount()):
			if(self.tableWidget_2.item(i,0).text() == name):
				if(other == []):
					return True
				if(len(other) != len(self.tableWidget_2.item(i,4).text().split(","))):
					continue
				else:
					if(set(other) == set(self.tableWidget_2.item(i,4).text().replace("[", "").replace(']', '').split(","))):
						return True

		return False

	# Finds result index in Results List
	def get_row_result(self, name):
		for i in range(0, self.tableWidget_2.rowCount()):
			if(self.tableWidget_2.item(i,0).text() == name):
				return i
		return -1

	# Inserts results elements into SNP List
	def fill_results(self, res):
		self.tableWidget_3.clearContents()
		self.tableWidget_3.setRowCount(0)

		if(res == []):
			return
		res = Result.results[res[-5].text()].data

		i = 0
		for element in res:
			item1 = QTableWidgetItem(element[0])
			item2 = QTableWidgetItem(str(element[1]))
			self.tableWidget_3.setRowCount(self.tableWidget_3.rowCount()+1)
			self.tableWidget_3.setItem(i, 0, item1)
			self.tableWidget_3.setItem(i, 1, item2)
			i += 1


'''

Worker class for Threaded control

'''

class Worker(QRunnable):
	thread_control = {}

	def __init__(self, function, *args):
		super().__init__()
		self.function = function
		self.args = args
		self.signals = Signals()

	def run(self):
		global currently_selected_model

		if(self.function == "new"):
			displayname = self.args[0]

			if(displayname != "" and loaded_dataset != ""):
				if(Model.models.get(displayname, False) == False):
					if(os.name == 'nt'):
						data_name = loaded_dataset.split("\\")[-1]
					else:
						data_name = loaded_dataset.split("/")[-1]	

					Model(displayname, loaded_dataset)

					item = displayname
					item2 = data_name

					if(Model.models[displayname].binary_feature_space and Model.models[displayname].binary_target_space):
						item3 = "Ready"
					else:
						item3 = "Not Ready"

					currently_selected_model = displayname
					self.signals.finished_new.emit(item, item2, item3)

		elif(self.function == "train"):

			if(currently_selected_model != ""):
				md = currently_selected_model

				if(Model.models[md].binary_feature_space and Model.models[md].binary_target_space):
					iterations = self.args[0]
					percentage = self.args[1]
					strat = self.args[2] 

					for i in range(0, iterations):
						Model.models[md].holdout(train_s=percentage, stratify=strat)
						Model.models[md].fit()

						if(currently_selected_model == md):
							self.signals.update_info.emit()

						self.signals.update_list.emit(md, str(i) + "/" + str(iterations))

						# Stop proccess
						if(Worker.thread_control.get(md, False) == False):
							self.signals.finished_training.emit(md)	
							return

					Model.models[md].calculate_top_snps()
					Result(md, Model.models[md].get_top_snps(top=None), times_fit=Model.models[md].times_fit, score=[Model.models[md].get_mean_precision(), Model.models[md].get_mean_recall()])
					Worker.thread_control.pop(md)

			self.signals.finished_training.emit(md, str(Result.results[md].other_models))	

		elif(self.function == "dummy"):
			modelname = currently_selected_model
			if(modelname != ""):
				if(not Model.models[modelname].binary_feature_space and Model.models[modelname].target_column != None):
					Model.models[modelname].create_dummies()
			self.signals.finished_dummy_ova.emit(modelname)

		elif(self.function == "ova"):
			modelname = currently_selected_model
			if(modelname != ""):
				if(not Model.models[modelname].binary_target_space):
					Model.models[modelname].one_vs_all_transform(self.args[0])
			self.signals.finished_dummy_ova.emit(modelname)

		del(self)

'''

Worker Signals class for inter-threading communication

'''

class Signals(QObject):
	# Train operation
	update_info = pyqtSignal()
	update_list = pyqtSignal(str, str)
	finished_training = pyqtSignal(str, str)
	# New operation
	finished_new = pyqtSignal(str,str,str)
	# Dummy and OVA operation
	finished_dummy_ova = pyqtSignal(str)

# Warning messages suppressor
def handler(msg_type, msg_log_context, msg_string):
    if(msg_type == 1):
    	pass
    else:
    	print(msg_string)


loaded_dataset = ""
version = "v1.0"
currently_selected_model = ""
all_selected_models = []
currently_selected_result = ""
Model.GUI = True

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = Win()
    ui.show()
    sys.exit(app.exec_())