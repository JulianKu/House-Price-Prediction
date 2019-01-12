import os
import json
import pandas as pd
import numpy as np
import geocoder as geo
from missingpy import KNNImputer
from loadData import loadData

def prepNeighbors(data, target, bins):
    '''
    function to get geographical coordinates and price value for 'Neighborhood' 
    variable
    
    Parameters:
        trainData:  pandas DataFrame (training data frame without missing values)
        target:     pandas DataFrame (values of target variable)
        bins:       list (price boundaries of bins to group neighborhoods in)
    Returns:
        neighborhoods: dict
            keys =
                'abbr': str (abbreviated Neighborhood name 
                             (as it appears as category))
                'adr':  str (address of the center of that neighborhood)
                'loc':  list (longitude and latitude coordinates)
    '''
    
    neighborhoods = [{'abbr':'Blmngtn','adr':'Berkshire Avenue'},
                 {'abbr':'Blueste','adr':'Bluestem'},
                 {'abbr':'BrDale','adr':'Barkley Ct'},
                 {'abbr':'BrkSide','adr':'Brookside'},
                 {'abbr':'ClearCr','adr':'Clear Creek'},
                 {'abbr':'CollgCr','adr':'College Creek'},
                 {'abbr':'Crawfor','adr':'415 Stanton Ave'},
                 {'abbr':'Edwards','adr':'Edwards'},
                 {'abbr':'Gilbert','adr':'Gilbert'},
                 {'abbr':'IDOTRR','adr':'800 Lincoln Way'},
                 {'abbr':'MeadowV','adr':'Meadow Village'},
                 {'abbr':'Mitchel','adr':'3521 Jewel Drive'},
                 {'abbr':'NAmes','adr':'North Ames'},
                 {'abbr':'NoRidge','adr':'Northridge'},
                 {'abbr':'NPkVill','adr':'2932 Northwestern Ave'},
                 {'abbr':'NridgHt','adr':'Northridge Heights'},
                 {'abbr':'NWAmes','adr':'Northwest Ames'},
                 {'abbr':'OldTown','adr':'307 8th St'},
                 {'abbr':'SWISU','adr':'Arbor St'},
                 {'abbr':'Sawyer','adr':'Sawyer'},
                 {'abbr':'SawyerW','adr':'Sawyer West'},
                 {'abbr':'Somerst','adr':'Clayton Dr'},
                 {'abbr':'StoneBr','adr':'Stone Brook'},
                 {'abbr':'Timber','adr':'Timberland'},
                 {'abbr':'Veenker','adr':'Veenker'}]
    data = pd.concat([data, target], axis=1)
    # compute median for each neighborhood
    medians = data.groupby('Neighborhood').median()['SalePrice']
    # put neighborhoods into valence group according to median sales price
    nbhoodvals = pd.cut(medians, bins, labels=bins[:-1])
    
    for entry in neighborhoods:
        success = False
        while not success:
            g = geo.osm(','.join([entry['adr'], 'Ames']))
            if g.latlng is None:
                print('no address found for neighborhood %s', entry['adr'])
            else:
                success = True
        entry['loc'] = g.latlng
        entry['val'] = int(nbhoodvals[entry['abbr']])
        
    return neighborhoods


def getLocVal(nbhood, hoods, misVal):
    '''
    function returns for the given neighborhood the corresponding geographical 
    location and valence group
    
    Parameters:
        nbhood: str (name of the neigborhood whose location should be returned)
        hoods:  dict (dictionary as returned by locNeighbors() )
    Returns:
        loc:    list (longitude and latitude coordinates of neighboorhood)
        val:    integer (valence group of neighborhood) 
    '''
    if isinstance(nbhood, str):
        h = list(filter(lambda entry: entry['abbr'].lower() == nbhood.lower(), hoods))
    else:
        h = [{'loc': [misVal, misVal], 'val': misVal}]
    return h[0]['loc'] + [h[0]['val']]


def imputeKNN(data, **kwargs):
    imputer = KNNImputer(**kwargs)
    imputedData = imputer.fit_transform(data)
    imputedData = pd.DataFrame(imputedData, index=data.index, columns=data.columns)
    return imputedData

def predkNN(trainData, NHData, inData=None, n_neighbors = 5, misVal=None):
    '''
    function to predict the missing values in the dataframe with help of a 
    k-NearestNeighbor imputation 
    
    Parameters:
        trainData:  pandas DataFrame (training data frame without missing values)
        NHData:     dict (dictionary as returned by locNeighbors() function)
        inData:     pandas DataFrame (input data frame that contains missing values)
        misVal:     NaN or None (value that signifies that this value is missing)
    Return:
        data:       pandas DataFrame (data frame of same dimensions as the input 
                                      but with missing values predicted) 
    '''
    
    
    if inData is not None:
        data = trainData.append(inData, ignore_index=False, sort=False)
    else:
        data = trainData       
    
    # split up data into numerical and categorical
    numFeat = []
    catFeat = []
    for feature in data.columns:
        if data[feature].dtype == np.float64 or data[feature].dtype == np.int64:
            numFeat.append(feature)
        else:
            catFeat.append(feature)
            
            
    dataNum = data[numFeat]
    if 'Id' in dataNum.columns:
        dataNum = dataNum.drop('Id', axis=1)
    dataCat = data[catFeat]
    
    # make categorical features binary
    for feature in catFeat:
        if feature == 'Neighborhood':
            # compute coordinates and valence group for each sample
            locVals = dataCat[feature].apply(getLocVal, 
                                             hoods=NHData, 
                                             misVal=misVal)
            # cast into data frame
            locVals = pd.DataFrame.from_items(zip(locVals.index, locVals.values)).T
            locVals.columns = ['Hood_X','Hood_Y','NhMedGrThan']
            # data now numerical -> add to numerical data
            dataNum = pd.concat([dataNum,locVals], axis=1)
        else:    
            categories = dataCat[feature].unique()
            categories = categories[~pd.isna(categories)]
            for cat in categories:
                catName = '{} = {}'.format(feature, cat)
                dataCat[catName] = False
                dataCat.loc[dataCat[feature] == cat, catName] = True
                if np.isnan(misVal):
                    dataCat.loc[dataCat[feature].isna(), catName] = misVal
                elif misVal is None:
                    dataCat.loc[dataCat[feature].isnull(), catName] = misVal
        dataCat = dataCat.drop(feature, axis=1)      
    
    data = pd.concat([dataNum,dataCat], axis=1)
    
    if np.isnan(misVal):
        maskMissing = data.isna()
    elif misVal is None:
        maskMissing = data.isnull()
    else:
        raise ValueError('{} currently not implemented for missing values'.format(misVal))
    
    # normalize numerical data 
    # (necessary for distance function to value all features equally)
    dataNumMax = dataNum.max(axis=0)
    dataNumMin = dataNum.min(axis=0)
    dataNumNorm = (dataNum - dataNumMin)/(dataNumMax - dataNumMin)
    
    # impute numerical data
    impNumNorm = imputeKNN(dataNumNorm, 
                       missing_values=misVal,
                       n_neighbors=n_neighbors,
                       weights="distance",
                       row_max_missing=1,
                       col_max_missing=1)
    
    # scale back to normal    
    impNumMax = impNumNorm.max(axis=0)
    impNumMin = impNumNorm.min(axis=0)
    impNum = (impNumNorm - impNumMin) * (dataNumMax - dataNumMin) \
                / (impNumMax - impNumMin) + dataNumMin
    
    # impute boolean data
    impBool = imputeKNN(dataCat,
                        missing_values=misVal,
                        n_neighbors=n_neighbors,
                        weights="distance",
                        row_max_missing=1,
                        col_max_missing=1).round().astype(bool).astype(int)
    
    # concatenate numerical and boolean data again
    impData = pd.concat([impNum, impBool], axis=1)
    
    # insert imputed data in missing values
    data.mask(maskMissing, other=impData, inplace=True)
    
    return data
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
if __name__ == "__main__":    
#----------------------------------------
# to run at initialization of GUI:
#----------------------------------------
    
    # load data
    trainData, target = loadData('data', 'SalePrice')
    
    # get neighborhood geographical coordinates and value bins
    if not os.path.isfile('neighborhood.json'):
        neighborhoods = prepNeighbors(trainData, target,
                                  bins=[0,100000,150000,200000,250000,300000,np.inf])
    else:
        with open('neighborhood.json', 'r') as f:
            neighborhoods = json.load(f)
        
    missingVal = np.nan
    
    #----------------------------------------
    # create dummy data to test
    #----------------------------------------
    
    test = pd.read_csv('data_test.csv')
    inData = pd.DataFrame(np.array([np.full(len(trainData.columns), missingVal)]),
                          columns=trainData.columns)
    inData.loc[0,['Neighborhood', 'ExterQual', 'OverallQual', 'GrLivArea', 'GarageCars']] \
                = test.loc[0,['Neighborhood', 'ExterQual', 'OverallQual', 'GrLivArea', 'GarageCars']]
    inData.replace(to_replace='nan', value=missingVal, inplace=True)
    inData.rename({0: 'query'}, axis='index', inplace=True)
    
    #----------------------------------------
    # to run everytime query is made:
    #----------------------------------------
    #inData.replace(to_replace='nan', value=missingVal, inplace=True)
    prediction = predkNN(trainData, neighborhoods, inData, misVal = missingVal)  