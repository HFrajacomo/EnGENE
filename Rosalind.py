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

# Setup GUI-Python integration
def setup_pywin(Win):
	Win.pushButton.clicked.connect(lambda:click_new(Win))
	Win.toolButton.clicked.connect(lambda:click_tool(Win))
	Win.tableWidget.setRowCount(0)
	Win.tableWidget.setColumnCount(2)
	Win.tableWidget.setHorizontalHeaderLabels(["Model name", "Filename"])
	Win.tableWidget.resizeColumnsToContents()
	Win.tableWidget.resizeRowsToContents()


# New Button Function
def click_new(Win):
	if(Win.lineEdit.displayText() != "" and loaded_dataset != ""):
		item = QtWidgets.QTableWidgetItem(Win.lineEdit.displayText())
		item2 = QtWidgets.QTableWidgetItem(loaded_dataset)
		ui.tableWidget.setRowCount(ui.tableWidget.rowCount()+1)
		Win.tableWidget.setItem(ui.tableWidget.rowCount()-1,0, item)
		Win.tableWidget.setItem(ui.tableWidget.rowCount()-1,1, item2)

		## Add exception to already existant model


# New function tool button
def click_tool(Win):
	global loaded_dataset
	loaded_dataset = fileopenbox(title="Load dataset", filetypes=["*.csv"])

	if(loaded_dataset == None):
		loaded_dataset = ""
	else:
		if(os.name == 'nt'):
			loaded_dataset = loaded_dataset.split("\\")[-1]
		else:
			loaded_dataset = loaded_dataset.split("/")[-1]

	Win.lineEdit_2.setText(loaded_dataset)


loaded_dataset = ""

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    setup_pywin(ui)
    MainWindow.show()
    sys.exit(app.exec_())