import sys
#from PyQt4 import QtCore, QtGui, uic
import runErrorDialog
import pandas as pd
from PyQt5 import QtWidgets, uic
import csv
import postProcessing
qtCreatorFile = "main.ui" # Enter file here.
main, base = uic.loadUiType(qtCreatorFile)
import similar

class Main(base, main):
    def __init__(self, parent=None):
        base.__init__(self, parent)
        self.setupUi(self)
        
        self.calculate_button.clicked.connect(self.calculateHouse)
        #self.forward_button.clicked.connect(self.forward)
        #self.backward_button.clicked.connect(self.backward)
        
        self.columns = ['Neighborhood', 'ExterQual', 'KitchenQual', 'BsmtQual', 'GarageFinish', 'Foundation', 'HeatingQC', 'GarageType', 'MasVnrType', 'BsmtFinType1', 'SalePrice','GrLivArea','GarageCars','GarageArea','TotalBsmtSF','stFlrSF','FullBath','TotRmsAbvGrd','YearBuilt','OverallQual']
        self.df = pd.DataFrame(index = [1],columns=self.columns)

        self.data = 0
        self.is_numerical = True
        self.cat = ''
        
    def calculateHouse(self):
        print('calculating..')
        self.getNumerical()
        self.getCategorical()
        self.df.rename({"stFlrSF": "1stFlrSF"},axis='columns',inplace=True)
        #write to file
        self.df.to_csv('user_input.csv', sep=',', index = False, header = True)
        #remap
        postProcessing.postProcessing()
        
        #search alternatives
        #similar.run('processed_user_input.csv')
        postProcessing.convertAlternatives()
        postProcessing.postProcessing2()
        self.setAlternatives()
    #def postProcessing(self):
        #self.df.to_csv('user_input.csv', sep=',', index = False, header = True)        
        #reader = csv.reader(open('plain.csv'))    
        #dic = {}
        #for row in reader:
            #key = row[0]
            #if key in dic:
                #pass
            #dic[key] = row[1:]
        #self.df = pd.read_csv('user_input.csv')
        #self.df.replace(dic)
        #self.df.to_csv('user_input.csv', sep=',', index = False, header = True)        
    
    def getCategorical(self):
        fields = ['Neighborhood', 'ExterQual', 'KitchenQual', 'BsmtQual', 'GarageFinish', 'Foundation', 'HeatingQC', 'GarageType', 'MasVnrType','BsmtFinType1']
        for field in fields:
            exec('self.cat = self.' + field + '.currentText()')
            if self.cat == '<none>':
                pass
            else:
                self.df[field] = self.cat
    
    
    def checkWriteNumerical(self,field,data):
        if data == '':
            pass
        else:        
            if(data.isdigit()):
                number = int(data)
                if number >= 0:
                    self.df[field] = data
                else:
                    self.is_numerical = False
                    exec(str('self.'+str(field)+'.clear()'))
                    runErrorDialog.errorDialog()
            else:
                self.is_numerical = False
                exec(str('self.'+str(field)+'.clear()'))
                runErrorDialog.errorDialog()
                #self.buildExamplePopup
        
   
    def getNumerical(self):
        self.is_numerical = True
        fields = ['SalePrice','GrLivArea','GarageCars','GarageArea','TotalBsmtSF','stFlrSF','FullBath','TotRmsAbvGrd','YearBuilt']
        for field in fields:
            exec(str('self.data = ' + 'self.' + field + '.text()'))
            self.checkWriteNumerical(field,self.data)
        
        self.df['OverallQual'] = int(self.OverallQual.currentText())
        
        if self.is_numerical == False:
            runErrorDialog.errorDialog()   
   
    
 
    def setAlternatives(self):
        alt = pd.read_csv('finished_alternative.csv')
        print(alt)
        alt.rename({"1stFlrSF": "stFlrSF"},axis='columns',inplace=True)
        for column in self.columns:
            exec(str('self.'+ column + '_2.setText('+'"' +str(alt.loc[0,column])+'"'+')'))
        
        self.Score_2.setText(str(int(alt.loc[0,'Score'])))
    
    def buildExamplePopup(self, item):
        name = item.text()
        self.exPopup = examplePopup(name)
        self.exPopup.setGeometry(100, 200, 100, 100)
        self.exPopup.show()    
        
if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    application = Main()
    application.show()
    sys.exit(app.exec())
    