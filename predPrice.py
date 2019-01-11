import os
import pickle
import pandas as pd
import numpy as np

def predictSalesPrice(X, model):
    '''
    predict sales price for house instance
    
    Parameters:
        X:  array-like (data to predict price of)
        model: sklearn class object that offers a predict(Data) function
    Return:
        y:  predicted price
    '''
    X_shaped = np.array(X).reshape(1,-1)
    y = model.predict(X_shaped)
    return y
    
modelFile = 'RandomCVModel.rfmdl'
if os.path.isfile(modelFile):
    model = pickle.load(open(modelFile, 'rb'))
else:
    raise IOError('file {} could not be found.\n Specify directory and make sure file exists')

testData = pd.read_csv('house_geo_binominal_test.csv')

SquaredLogErrors = []
for sample in range(testData.shape[0]): 
    testSample = testData.loc[sample]
    realPrice = testSample['SalePrice']
    testSample = testSample.drop(['Unnamed: 0','SalePrice','Neighborhood'])
    predPrice = predictSalesPrice(testSample, model)
    SquaredLogErrors.append(np.square(np.log((predPrice+1)/(realPrice+1))))
RootMeanSquaredLogError = np.sqrt(np.mean(SquaredLogErrors))
print('Root Mean Squared Log Error = {}'.format(RootMeanSquaredLogError)) 