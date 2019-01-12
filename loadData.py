import os
import numpy as np
import pandas as pd

def str2bool(s):
    if s.lower == 'true':
         return True
    elif s.lower == 'false':
         return False
    else:
         raise ValueError # evil ValueError that doesn't tell you what the wrong value was

def loadData(whichData, targetVar, seed=1):
    '''
    Loads specified dataframe and if not already happend, 
    splits up data into training and test. 
    Drops unneeded variables (non-numerical or non-boolean)
    
    Parameters:
        whichData:  str ('house_geo_binominal' or 'data')
        targetVar:  str (target variable)
        seed:       int (specifies random seed)
    Return:
        data:       pandas DataFrame (training data)
        target:     pandas DataFrame (values of target variable)
    '''
    
    if not os.path.isfile('{}_train.csv'.format(whichData)):
        rawdataset = pd.read_csv('{}.csv'.format(whichData))
        rand_perm = rawdataset.sample(rawdataset.shape[0], random_state = seed) # random_state: seed for reproducability
        data_test = rand_perm[:5].sort_index()
        data_train = rand_perm[5:].sort_index()
        
        data_test.to_csv('{}_test.csv'.format(whichData), sep=',',header=True,)
        data_train.to_csv('{}_train.csv'.format(whichData), sep=',',header=True,)
    
    dataset = pd.read_csv('{}_train.csv'.format(whichData))
    try:
        dataset = dataset.drop(labels='Unnamed: 0', axis=1)
    except Exception:
        pass
    try:
        dataset = dataset.drop(labels='Id', axis=1)
    except Exception:
        pass
    
    if whichData == 'house_geo_binominal':
        # process non-numerical data
        for feature in dataset.columns:
          if not dataset[feature].dtype == np.float64 \
          and not dataset[feature].dtype == np.int64 \
          and not dataset[feature].dtype == bool:
            try:
                dataset[feature] = dataset[feature].apply(str2bool)
            except ValueError:
                print('feature {} is neither numerical nor could be converted to boolean\n'.format(feature) +
                      'feature {} will be removed from dataset'.format(feature))
                dataset = dataset.drop(feature, axis=1)
    
        # to make all data non-negative
        dataset['Hood_Y'] = dataset['Hood_Y'].abs()
            
    target = dataset[targetVar]
    data = dataset.drop(targetVar, axis=1)
    return data, target
