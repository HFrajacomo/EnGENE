__author__ = "Henrique Frajacomo"

import sys
from PyQt5 import QtCore, QtGui, QtWidgets
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

# Setup GUI-Python integration
def setup_pywin(Win):
	Win.pushButton.clicked.connect(lambda:click_new(Win))
	Win.toolButton.clicked.connect(lambda:click_tool(Win))
	Win.tableWidget.setRowCount(0)
	Win.tableWidget.setColumnCount(2)
	Win.tableWidget.setHorizontalHeaderLabels(["Model name", "Filename"])
	Win.tableWidget.resizeColumnsToContents()
	Win.tableWidget.resizeRowsToContents()
	Win.tableWidget.itemSelectionChanged.connect(lambda: model_selection_trigger(Win, Win.tableWidget.selectedItems()))
	Win.spinBox_2.valueChanged.connect(spinbox_end_change)
	Win.spinBox_3.valueChanged.connect(spinbox_start_change)
	Win.spinBox_4.valueChanged.connect(spinbox_target_change)
	Win.pushButton_2.clicked.connect(lambda: click_select(Win))
	Win.pushButton_7.clicked.connect(lambda: click_target(Win))
	Win.textBrowser.setFontPointSize(11)
	Win.pushButton_3.clicked.connect(lambda: click_dummy(Win))
	Win.spinBox_5.valueChanged.connect(spinbox_ova_change)
	Win.pushButton_4.clicked.connect(lambda: click_ova(Win))
	set_train_menu(Win)
	Win.toolButton_2.menu().triggered.connect(change_percentage)
	Win.pushButton_5.clicked.connect(lambda: click_train(Win))
	Win.pushButton_6.clicked.connect(lambda: click_unload(Win))

# New Button Function
def click_new(Win):
	if(Win.lineEdit.displayText() != "" and loaded_dataset != ""):
		if(not __model_exist(Win.lineEdit.displayText())):
			if(os.name == 'nt'):
				data_name = loaded_dataset.split("\\")[-1]
			else:
				data_name = loaded_dataset.split("/")[-1]	

			item = QtWidgets.QTableWidgetItem(Win.lineEdit.displayText())
			item2 = QtWidgets.QTableWidgetItem(data_name)
			ui.tableWidget.setRowCount(ui.tableWidget.rowCount()+1)
			Win.tableWidget.setItem(ui.tableWidget.rowCount()-1,0, item)
			Win.tableWidget.setItem(ui.tableWidget.rowCount()-1,1, item2)

			Model(Win.lineEdit.displayText(), loaded_dataset)
			model_selection_trigger(Win, item.text())


# New function tool button
def click_tool(Win):
	global loaded_dataset
	loaded_dataset = fileopenbox(title="Load dataset", filetypes=["*.csv"], default="*.csv")

	if(loaded_dataset == None):
		loaded_dataset = ""

	Win.lineEdit_2.setText(loaded_dataset)

# Checks if a model with name exists
def __model_exist(name):
	if(type(Model.models.get(name, False)) == Model):
		return True
	else:
		return False

# Updates Model Information screen
# Triggers for every model selection change
def update_text_browser(Win):
	if(not __model_exist(currently_selected_model)):
		Win.textBrowser.setText("")
	else:
		Win.textBrowser.setText(str(Model.models[currently_selected_model]))

# Triggers every mouse selection in Model list
def model_selection_trigger(Win, modelname):
	global currently_selected_model
	global all_selected_models

	if(modelname == []):
		return

	elif(type(modelname) == list):
		all_selected_models = [x for x in modelname[::2]]
		currently_selected_model = modelname[-2].text()

	else:
		currently_selected_model = modelname

	reset_spinboxes(Win)
	update_text_browser(Win)

# Re-set all spinbox values
def reset_spinboxes(Win):
	Win.spinBox_2.setMaximum(get_max_spinbox())
	Win.spinBox_3.setMaximum(get_max_spinbox())
	Win.spinBox_4.setMaximum(get_max_spinbox())
	Win.spinBox_2.setValue(0)
	Win.spinBox_3.setValue(0)
	Win.spinBox_4.setValue(0)
	Win.spinBox_5.setValue(0)
	Win.lineEdit_3.setText("")
	Win.lineEdit_4.setText("")
	Win.lineEdit_5.setText("")	
	Win.lineEdit_6.setText("")

	if(currently_selected_model != ""):
		if(not __model_exist(currently_selected_model)):
			return
		if(Model.models[currently_selected_model].target_column != None):
			Win.spinBox_5.setMaximum(get_max_spinbox_class())

# Gets maximum number of Select and Target Spinboxes
def get_max_spinbox():
	if(currently_selected_model == ""):
		return 0
	if(not __model_exist(currently_selected_model)):
		return 0
	return len(Model.models[currently_selected_model].data.columns)-1

# Gets maximum number of Select to OVA Spinbox
def get_max_spinbox_class():
	if(currently_selected_model == ""):
		return 0
	if(not __model_exist(currently_selected_model)):
		return 0
	return len(Model.models[currently_selected_model].get_classes())-1	

# Gets the header related to n element
def get_spinbox_header(n):
	if(currently_selected_model == ''):
		return ""
	return Model.models[currently_selected_model].data.columns[n]

def spinbox_end_change(q):
	global ui
	ui.lineEdit_4.setText(get_spinbox_header(q))
def spinbox_start_change(q):
	global ui
	ui.lineEdit_3.setText(get_spinbox_header(q))
def spinbox_target_change(q):
	global ui
	ui.lineEdit_5.setText(get_spinbox_header(q))
def spinbox_ova_change(q):
	global ui
	ui.lineEdit_6.setText(Model.models[currently_selected_model].get_classes()[q])

# Select button click
def click_select(Win):
	if(currently_selected_model != ""):
		Model.models[currently_selected_model].set_feature_range(Win.spinBox_3.value(), Win.spinBox_2.value())
		update_text_browser(Win)

# Target button click
def click_target(Win):
	if(currently_selected_model != ""):
		Model.models[currently_selected_model].set_target_column(Win.spinBox_4.value())
		update_text_browser(Win)

# Dummification button click
def click_dummy(Win):
	if(currently_selected_model != ""):
		if(not Model.models[currently_selected_model].binary_feature_space and Model.models[currently_selected_model].target_column != None):
			Model.models[currently_selected_model].create_dummies()
			update_text_browser(Win)
			reset_spinboxes(Win)

# OVA button click
def click_ova(Win):
	if(currently_selected_model != ""):
		if(not Model.models[currently_selected_model].binary_target_space):
			Model.models[currently_selected_model].one_vs_all_transform(Win.lineEdit_6.text())
			update_text_browser(Win)
			reset_spinboxes(Win)

# Changes percentage of training
def change_percentage(q):
	global ui
	ui.toolButton_2.setText(q.text())		

# Creates Train Percentage menu
def set_train_menu(Win):
	menu = QtWidgets.QMenu()

	for i in range(1, 10):
		act = menu.addAction(str(i*10) + "%")
	menu.setDefaultAction(act)
	Win.toolButton_2.setText("90%")
	Win.toolButton_2.setMenu(menu)

# Train button click
def click_train(Win):
	if(currently_selected_model != ""):
		md = currently_selected_model

		if(Model.models[md].binary_feature_space and Model.models[md].binary_target_space):
			iterations = int(Win.spinBox.text())
			percentage = int(Win.toolButton_2.text()[:-1])/100
			strat = Win.radioButton.isChecked()

			for i in range(0, iterations):
				Model.models[md].holdout(train_s=percentage, stratify=strat)
				Model.models[md].fit()

				if(currently_selected_model == md):
					update_text_browser(Win)

			Result(md, Model.models[md].get_top_snps(top=None), times_fit=Model.models[md].times_fit)

# Unload button click
def click_unload(Win):
	global all_selected_models
	global currently_selected_model

	for md in all_selected_models:
		Model.models.pop(md.text())

	delete_list = []

	for i in range(Win.tableWidget.rowCount()):
		if(Win.tableWidget.item(i,0).text() in [x.text() for x in all_selected_models]):
			delete_list.append(i)

	delete_list = sorted(delete_list)
	currently_selected_model = ""
	all_selected_models = []
	Win.textBrowser.setText("")

	for ind in delete_list:
		Win.tableWidget.removeRow(ind)
		for i in range(len(delete_list)):
			delete_list[i] -= 1




loaded_dataset = ""
version = "v1.0"
currently_selected_model = ""
all_selected_models = []
Model.GUI = True

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    setup_pywin(ui)
    MainWindow.show()
    sys.exit(app.exec_())