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
	Win.textBrowser.setText(str(Model.models[currently_selected_model]))

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

	# Spinboxes
	Win.spinBox_2.setMaximum(get_max_spinbox())
	Win.spinBox_3.setMaximum(get_max_spinbox())
	Win.spinBox_4.setMaximum(get_max_spinbox())
	Win.spinBox_2.setValue(0)
	Win.spinBox_3.setValue(0)
	Win.spinBox_4.setValue(0)
	Win.lineEdit_3.setText("")
	Win.lineEdit_4.setText("")
	Win.lineEdit_5.setText("")	

	update_text_browser(Win)

# Gets maximum number of Select and Target Spinboxes
def get_max_spinbox():
	if(currently_selected_model == ""):
		return 0
	return len(Model.models[currently_selected_model].data.columns)-1

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

# Select button click
def click_select(Win):
	if(currently_selected_model != ""):
		Model.models[currently_selected_model].set_feature_range(Win.spinBox_3.value(), Win.spinBox_2.value())
		update_text_browser(Win)


loaded_dataset = ""
version = "v1.0"
currently_selected_model = ""
all_selected_models = []

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    setup_pywin(ui)
    MainWindow.show()
    sys.exit(app.exec_())