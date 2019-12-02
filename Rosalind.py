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
	Win.tableWidget.itemSelectionChanged.connect(lambda: update_text_browser(Win, Win.tableWidget.selectedItems()))

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
			update_text_browser(Win, item.text())


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
def update_text_browser(Win, modelname):
	global currently_selected_model

	if(modelname == []):
		return

	if(type(modelname) == list):
		modelname = modelname[-2].text()

	Win.textBrowser.setText(str(Model.models[modelname]))
	currently_selected_model = modelname

loaded_dataset = ""
version = "v1.0"
currently_selected_model = ""

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    setup_pywin(ui)
    MainWindow.show()
    sys.exit(app.exec_())