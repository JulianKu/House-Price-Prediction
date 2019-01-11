import os
import numpy as np
import pandas as pd
import sklearn as sk
from sklearn.decomposition import NMF
from loadData import loadData 
import lom as lom
from missingpy import KNNImputer

def replaceRandom(dataframe, columns=None, repVal=0, num=10, seed=1):
    '''
    replaces a random number of entries in a dataframe with the specified value
    
    Parameters:
        dataframe:  pd.dataframe (dataframe in which values are to be replaced)
        columns:    list of str, optional 
                    (list of columns that values should be replaced in
                    if columns = None, all columns are considered
                    default None)
        repVal:     value with which the randomly drawn entries are replaced
                    default 0
        num:        number of entries to be replaced
                    default 10
    Return:
        dataframe:  pd.dataframe of same dimensions, 
                    just with respective values replaced
        randomIdx:  numpy array of list 
                    (an array of the indices that have been changed)
        
    '''
    np.random.seed(seed)
    if columns == None:
        columns = dataframe.columns
    reducedFrame = dataframe[columns]    
    index_array = np.zeros_like(reducedFrame, dtype=object)
    for col in range(reducedFrame.shape[1]):    
        for row in range(reducedFrame.shape[0]):
            index_array[row,col] = [row,reducedFrame.columns[col]]
    randomIdx = np.random.choice(index_array.flatten(), size=num, replace=False)
    for pair in randomIdx:
        dataframe.loc[pair[0], pair[1]] = repVal
    
    return dataframe, randomIdx

seed = 1
data, target = loadData('house_geo_binominal', 'SalePrice', seed)

boolFeat = []
numFeat = []
for feature in data.columns:
    if data[feature].dtype == np.float64 or data[feature].dtype == np.int64:
        numFeat.append(feature)
    elif data[feature].dtype == bool:
        boolFeat.append(feature)
dataNum = data[numFeat].drop('Id', axis=1)
dataBool = data[boolFeat]


# normalize numerical data
dataNumMax = dataNum.max(axis=0)
dataNumMin = dataNum.min(axis=0)
dataNumNorm = (dataNum - dataNumMin)/(dataNumMax - dataNumMin)

# turn boolean (0,1) into binary (-1,1) data
dataBin = dataBool.astype(int)
dataBin[dataBin == 0] = -1

#---------------------------------------------
#-build test set for missing value estimation-
#---------------------------------------------

# replace random numbers with NaNs to check prediction capabilities
unchangeColumnsNum = ['OverallQual','GrLivArea','GarageCars']
replaceColumnsNum = list(set(dataNumNorm) - set(unchangeColumnsNum))
dataNumVal, randIdxNum = replaceRandom(dataNumNorm.copy(), 
                                    columns=replaceColumnsNum, 
                                    repVal = np.nan, 
                                    num=int(0.05*dataNumNorm.count().sum()),
                                    seed=seed)

# replace random numbers with 0 to check prediction capabilities
unchangeColumnsBool = ['Neighborhood','ExterQual']
replaceColumnsBool = list(set(dataBool) - set(unchangeColumnsBool))
dataBinVal, randIdxBin = replaceRandom(dataBin.copy(), 
                                    columns=replaceColumnsBool, 
                                    repVal = 0, 
                                    num=int(0.05*dataBin.count().sum()),
                                    seed=seed)

dataBoolVal, randIdxBool = replaceRandom(dataBool.copy(), 
                                    columns=replaceColumnsBool, 
                                    repVal = np.nan, 
                                    num=int(0.05*dataBool.count().sum()),
                                    seed=seed)

#------------------------------------------------------------------------------
#--------------------------Non-negative matrix factorization-------------------
#------------------------------------------------------------------------------
# NMF with missing values see https://github.com/TomDLT/scikit-learn/tree/nmf_missing


# find Non-Negative Matrix Factorization for numerical data
model = NMF(n_components=2, init='random', random_state=seed, solver='mu')
W = model.fit_transform(dataNumVal)
H = model.components_

reDataNum = pd.DataFrame(np.dot(W,H), columns=dataNumVal.columns)
# residuals sum of squared errors for the reconstructed missing values:
rssNMF = sum([(reDataNum.loc[idx[0],idx[1]] - dataNumNorm.loc[idx[0],idx[1]])**2 for idx in randIdxNum])

# scale back to normal    
reDataMax = reDataNum.max(axis=0)
reDataMin = reDataNum.min(axis=0)
reScDataNum = (reDataNum - reDataMin) * (dataNumMax - dataNumMin) / (reDataMax - reDataMin) + dataNumMin

# insert reconstructed data in missing values
re2DataNum = dataNum.copy()
for idx in randIdxNum:
    re2DataNum.loc[idx[0], idx[1]] = reScDataNum.loc[idx[0], idx[1]]
    
#------------------------------------------------------------------------------
#--------------------------Boolean matrix factorization------------------------
#------------------------------------------------------------------------------  
#BMF with missing values see https://github.com/TammoR/LogicalFactorisationMachines

dataBinVal = dataBin.copy()
orm = lom.Machine()
data = orm.add_matrix(dataBinVal.values, fixed=True)
layer1 = orm.add_layer(latent_size=10, child=data, model='OR-AND')
layer2 = orm.add_layer(latent_size=3, child=layer1.z, model='OR-AND')

orm.infer(burn_in_min=100, burn_in_max=1000, no_samples=1000)

reDataBin = pd.DataFrame(layer1.output(technique='factor_map'), columns=dataBinVal.columns)
# turn into boolean again
reDataBin[reDataBin == -1] = 0
reDataBool = reDataBin.astype(bool)

rssBMF = sum([abs(reDataBool.loc[idx[0],idx[1]] ^ dataBool.loc[idx[0],idx[1]]) for idx in randIdxBool])

    
#------------------------------------------------------------------------------
#-------------------------Nearest Neighbor Imputation--------------------------
#------------------------------------------------------------------------------

n_neighbors = 5
nan = np.nan

#numerical data
imputerNum = KNNImputer(missing_values=nan,
                        n_neighbors=n_neighbors,
                        weights="distance")
impDataNum = imputerNum.fit_transform(dataNumVal)
impDataNum = pd.DataFrame(impDataNum, columns=dataNumVal.columns)

# residuals sum of squared errors for the imputed missing values:
rssImpNum = sum([(impDataNum.loc[idx[0],idx[1]] - dataNumNorm.loc[idx[0],idx[1]])**2 for idx in randIdxNum])

# scale back to normal    
impDataMax = impDataNum.max(axis=0)
impDataMin = impDataNum.min(axis=0)
impScDataNum = (impDataNum - impDataMin) * (dataNumMax - dataNumMin) / (impDataMax - impDataMin) + dataNumMin

# insert imputed data in missing values
impDataNum2 = dataNum.copy()
for idx in randIdxNum:
    impDataNum2.loc[idx[0], idx[1]] = impScDataNum.loc[idx[0], idx[1]]
    
#--------------------------------------------
#boolean data
    
imputerBool = KNNImputer(missing_values=nan,
                         n_neighbors=n_neighbors,
                         weights="distance")
impDataBool = imputerBool.fit_transform(dataBoolVal)
impDataBool = pd.DataFrame(impDataBool, columns=dataBoolVal.columns).round().astype(bool)

rssImpBool = sum([abs(impDataBool.loc[idx[0],idx[1]] ^ dataBool.loc[idx[0],idx[1]]) for idx in randIdxBool])

#--------------------------------------------
# numerical + boolean data

imputerFull = KNNImputer(missing_values=nan,
                         n_neighbors=n_neighbors,
                         weights="distance")
FullData = pd.concat([dataNumVal,dataBoolVal], axis=1)
impFullData = imputerFull.fit_transform(FullData)
impFullData = pd.DataFrame(impFullData, columns=FullData.columns)
impFullNum = impFullData[dataNumVal.columns]
impFullBool = impFullData[dataBoolVal.columns].round().astype(bool)

rssFullNum = sum([(impFullNum.loc[idx[0],idx[1]] - dataNumNorm.loc[idx[0],idx[1]])**2 for idx in randIdxNum])
rssFullBool = sum([abs(impFullBool.loc[idx[0],idx[1]] ^ dataBool.loc[idx[0],idx[1]]) for idx in randIdxBool])

impFullMin = impFullNum.max(axis=0)
impFullMax = impFullNum.min(axis=0)
impScFullNum = (impFullNum - impFullMin) * (dataNumMax - dataNumMin) / (impFullMax - impFullMin) + dataNumMin

#--------------------------------------------
#print results
print('\n-----------------------------------------------------')
print('-----------------------------------------------------\n')
print('results for numerical variables')
print('-----------------------------------------------------')
print('reconstruction (NMF) residuals sum of squared error = {}'.format(rssNMF))
print('imputation (KNN) residuals sum of squared error = {}'.format(rssImpNum))
print('imputation (KNN,full) residuals sum of squared error = {}'.format(rssFullNum))
print('\n'+'results for boolean variables')
print('-----------------------------------------------------')
print('reconstructed (BMF) residuals sum of absolute error = {}'.format(rssBMF))
print('imputation (KNN) residuals sum of absolute error = {}'.format(rssImpBool))
print('imputation (KNN,full) residuals sum of absolute error = {}'.format(rssFullBool))

