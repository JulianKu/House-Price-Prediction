import os
import pickle
import json
import numpy as np
import pandas as pd
from predPrice import predictSalesPrice
from misVal import predkNN, prepNeighbors
from loadData import loadData

def makePrediction(trainData, NHData, inData, model=None, misVal=None):
    
    trainData.replace(to_replace=np.nan, value='NA',inplace=True)
    inData.replace(to_replace=np.nan, value=misVal, inplace=True)
    try:
        inData.drop('SalePrice',inplace=True, axis=1)
    except Exception:
        pass
    inData.rename({0: 'query'}, axis='index', inplace=True)
    impData = predkNN(trainData, NHData, inData=inData, n_neighbors = 5, misVal=misVal)
    inDataImp = impData.loc['query'].to_frame().transpose()
    inDataImp.rename({'BsmtQual = NA':'BsmtQual = No Basement',
                      'BsmtFinType1 = NA':'BsmtFinType1 = No Basement',
                      'GarageType = NA':'GarageType = No_Garage',
                      'GarageFinish = NA':'GarageFinish = No_Garage'},
                      axis=1,
                      inplace=True)
    if model is not None:
        predPrice = predictSalesPrice(inDataImp, model)[0]
        return predPrice, inDataImp
#    return impData, _


#----------------------------------------
# to run at initialization of GUI:
#----------------------------------------
def run(sample):
    # for missing value imputation
      
    # load data
    trainData, target = loadData('data', 'SalePrice')
    
    # get neighborhood geographical coordinates and valence bins
    if not os.path.isfile('neighborhood.json'):
        neighborhoods = prepNeighbors(trainData, target,
                                  bins=[0,100000,150000,200000,250000,300000,np.inf])
    else:
        with open('neighborhood.json', 'r') as f:
            neighborhoods = json.load(f)
        
    missingVal = np.nan
    
    #for price prediction
    
    #load model
    modelFile = 'RandomCVModel.rfmdl'
    if os.path.isfile(modelFile):
        model = pickle.load(open(modelFile, 'rb'))
    else:
        raise IOError('file {} could not be found.\n Specify directory and make sure file exists')
    
    price, imputedData = makePrediction(trainData, neighborhoods, sample, model, missingVal)
    imputedData.to_csv('processed_user_input.csv', sep=',', index = False, header = True)
    return(price,imputedData)

if __name__ == "__main__":
#------------------------------------------
    sample = pd.read_csv('user_input.csv')
    price, imputedData = run(sample)