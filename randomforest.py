import os
import numpy as np
import pandas as pd
import sklearn as sk
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_validate, RandomizedSearchCV
from sklearn.svm import SVR
from scipy.stats import beta
from loadData import loadData

def str2bool(s):
    if s.lower == 'true':
         return True
    elif s.lower == 'false':
         return False
    else:
         raise ValueError('can only convert "true"/"false" strings to bool')

def betadistr(expec, lenDat, numSam, seed):
    a = expec / 25
    b = (lenDat - expec) / 25
    samples = beta.rvs(a, b, loc=2, scale=lenDat, size=numSam, random_state=seed)
    return map(int,samples)

seed = 2
data, target = loadData('house_geo_binominal', 'SalePrice', seed)
numData = data.shape[0]

#------------------------------------------------------------------------------
#----------------------------------Random Forest-------------------------------
#------------------------------------------------------------------------------

# model extracted from Rapidminer
RFreg = RandomForestRegressor(n_estimators=77, 
                              max_depth=90, 
                              min_samples_split=43, 
                              min_samples_leaf=38, 
                              min_weight_fraction_leaf=0.0, 
                              max_features='auto', 
                              max_leaf_nodes=None, 
                              min_impurity_decrease=0.0, 
                              #bootstrap=True,
                              n_jobs=None,
                              random_state=seed)

scoresRF = cross_validate(RFreg, data, target, scoring='neg_mean_squared_log_error', cv=10)


RFreg2 = RandomForestRegressor(min_weight_fraction_leaf=0.0, 
                               max_features='auto', 
                               max_leaf_nodes=None, 
                               min_impurity_decrease=0.0, 
                               #bootstrap=True,
                               n_jobs=None,
                               random_state=seed)


Parameters = ['n_estimators', 'max_depth', 'min_samples_split', 'min_samples_leaf']
#desired expectations for different params
Expectations = [75, 70, 20, 20]

paramDist = {}
for idx, param in enumerate(Parameters):
    #use of beta distribution because likely optimal values will be 
    #at the lower end of the value range but we do not want to rule 
    #out the high values as well (beta distr like skewed normal distr)
    paramDist[param] = list(betadistr(Expectations[idx], numData, 100, seed)) 
paramDist['bootstrap'] = [True, False]

RFreg_random = RandomizedSearchCV(RFreg2, paramDist, 
                                  n_iter=100, scoring='neg_mean_squared_log_error', 
                                  cv=10, random_state=seed)
RFreg_random.fit(data,target)
resultsRF = RFreg_random.cv_results_
bestRFreg = RFreg_random.best_estimator_
bestRFParams = RFreg_random.best_params_
print('Randomized Search found these best parameters for the RF:\n{}'.format(bestRFParams))

#------------------------------------------------------------------------------
#------------------------------Support Vector Regression-----------------------
#------------------------------------------------------------------------------

#SVreg = SVR()
##scoresSVR = scores = cross_validate(SVreg, data, target, scoring='neg_mean_squared_log_error', cv=10)
#
#paramDist = {}
#paramDist['kernel'] = ['rbf','poly']#,'sigmoid']
#paramDist['degree'] = list(range(1,15))
#paramDist['gamma'] = list(np.logspace(-15,-1,base=10))
#paramDist['epsilon'] = [0] + list(np.logspace(-3,1))
#paramDist['C'] = list(np.logspace(-3,4,base=10))
#
#SVR_random = RandomizedSearchCV(SVreg, paramDist, 
#                                n_iter=100, scoring='neg_mean_squared_log_error', 
#                                cv=10, random_state=seed)
#
#SVR_random.fit(data,target)
#resultsSVR = SVR_random.cv_results_
#bestSVRreg = SVR_random.best_estimator_
#bestSVRParams = SVR_random.best_params_
#print('Randomized Search found these best parameters for the SVR:\n{}'.format(bestSVRParams))