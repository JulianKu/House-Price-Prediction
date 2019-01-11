import sys
#from PyQt5 import QtCore, QtGui, uic
from PyQt5 import QtCore, QtGui, QtWidgets, uic

qtCreatorFile = "errorDialog.ui" # Enter file here.
 
main, base = uic.loadUiType(qtCreatorFile)
 
class Error(base, main):
    def __init__(self, parent=None):
        base.__init__(self, parent)
        self.setupUi(self)
        
        #self.close_button.clicked.connect(self.closeWindow)
    #def closeWindow(self):
        #sys.exit(Dialog.exec_())
        
def errorDialog():
    #app = QtWidgets.QApplication([])
    #application = Error()
    #application.show()
    #sys.exit(app.exec())
   
    
    Dialog = QtWidgets.QDialog()
    ui = Error()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())    
 
if __name__ == "__main__":
    print("Can't run independently")