__author__ = "Henrique Frajacomo"

import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThreadPool, QRunnable, pyqtSignal, pyqtSlot, QObject, QThread
from PyQt5.QtGui import QColor
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
		self.tableWidget.itemSelectionChanged.connect(lambda:self.model_selection_trigger(self.tableWidget.selectedItems()))
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

	# Checks if a model with name exists
	def __model_exist(self, name):
		if(type(Model.models.get(name, False)) == Model):
			return True
		else:
			return False

	# New Button Function
	def click_new(self):
		if(self.lineEdit.displayText() != "" and loaded_dataset != ""):
			if(not self.__model_exist(self.lineEdit.displayText())):
				if(os.name == 'nt'):
					data_name = loaded_dataset.split("\\")[-1]
				else:
					data_name = loaded_dataset.split("/")[-1]	

				Model(self.lineEdit.displayText(), loaded_dataset)

				item = QtWidgets.QTableWidgetItem(self.lineEdit.displayText())
				item2 = QtWidgets.QTableWidgetItem(data_name)

				if(Model.models[self.lineEdit.displayText()].binary_feature_space and Model.models[self.lineEdit.displayText()].binary_target_space):
					item3 = QtWidgets.QTableWidgetItem("Ready")
					item3.setForeground(QColor(0,255,0))
				else:
					item3 = QtWidgets.QTableWidgetItem("Not Ready")
					item3.setForeground(QColor(255,0,0))					

				self.tableWidget.setRowCount(self.tableWidget.rowCount()+1)
				self.tableWidget.setItem(self.tableWidget.rowCount()-1,0, item)
				self.tableWidget.setItem(self.tableWidget.rowCount()-1,1, item2)
				self.tableWidget.setItem(self.tableWidget.rowCount()-1,2, item3)
				self.model_selection_trigger(item.text())

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
		if(currently_selected_model != ""):
			if(not Model.models[currently_selected_model].binary_feature_space and Model.models[currently_selected_model].target_column != None):
				Model.models[currently_selected_model].create_dummies()
				self.update_text_browser()
				self.reset_spinboxes()
		self.update_model_status(currently_selected_model)

	# OVA button click
	def click_ova(self):
		if(currently_selected_model != ""):
			if(not Model.models[currently_selected_model].binary_target_space):
				Model.models[currently_selected_model].one_vs_all_transform(self.lineEdit_6.text())
				self.update_text_browser()
				self.reset_spinboxes()

		self.update_model_status(currently_selected_model)

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
		# Cancel operation implementation
		if(Worker.thread_control.get(currently_selected_model, False) != False):
			Worker.thread_control.pop(currently_selected_model)
			self.toggle_train_tag()

		# Train operation
		else:
			w = Worker("train", int(self.spinBox.text()), int(self.toolButton_2.text()[:-1])/100, self.radioButton.isChecked())
			w.signals.update_info.connect(self.update_text_browser)
			w.signals.update_list.connect(self.training_update)
			w.signals.finished_training.connect(self.update_model_status)
			Worker.thread_control[currently_selected_model] = True
			self.toggle_train_tag()
			self.threads.start(w)

	# Changes Train button tag
	def toggle_train_tag(self):
		if(Worker.thread_control.get(currently_selected_model, False) != False):
			self.pushButton_5.setText("Stop Training")
			self.update_model_status(currently_selected_model)
		else:
			self.pushButton_5.setText("Train")
			self.update_model_status(currently_selected_model)

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
		if(self.function == "train"):
			global currently_selected_model

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

					Result(md, Model.models[md].get_top_snps(top=None), times_fit=Model.models[md].times_fit)
					Worker.thread_control.pop(md)

			self.signals.finished_training.emit(md)	

'''

Worker Signals class for inter-threading communication

'''

class Signals(QObject):
	update_info = pyqtSignal()
	update_list = pyqtSignal(str, str)
	finished_training = pyqtSignal(str)

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
Model.GUI = True

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = Win()
    ui.show()
    sys.exit(app.exec_())