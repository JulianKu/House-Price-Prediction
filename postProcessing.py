import json
import csv
import re
import pandas as pd
import numpy as np

def postProcessing():
    #convertes gui input into processing format
    reader = csv.reader(open('plain.csv'))    
    dic = {}
    for row in reader:
        key = row[0]
        if key in dic:
            pass
        dic[key] = row[1:]

    my_csv_path = 'user_input.csv'
    # open your csv and read as a text string
    with open(my_csv_path, 'r') as f:
        my_csv_text = f.read()
    
    
    for key in dic:
        my_csv_text = re.sub(str(key),str(dic[key][0]),my_csv_text)


    with open(my_csv_path, 'w') as f:
        f.write(my_csv_text)

def postProcessing2():
    #converts the finished alternative back into gui output
    reader = csv.reader(open('plain2.csv'))    
    dic = {}
    for row in reader:
        key = row[0]
        if key in dic:
            pass
        dic[key] = row[1:]
    my_csv_path = 'finished_alternative.csv'
    # open your csv and read as a text string
    with open(my_csv_path, newline='') as f:
        reader = csv.reader(f)
        row1 = next(reader)
        row2 = next(f)
        
    with open(my_csv_path, 'r') as f:
        my_csv_text = f.read()

    for key in dic:
        row2 = re.sub(str(key),str(dic[key][0]),row2)

    df = pd.DataFrame([row2.split(",")],columns=row1,index=[0])
    df.to_csv(my_csv_path, sep=',', index = False, header = True)


def convertAlternatives():
    temp = pd.read_csv('test_similarhouses.csv')
    columns = ['Neighborhood', 'ExterQual', 'KitchenQual', 'BsmtQual', 'GarageFinish', 'Foundation', 'HeatingQC', 'GarageType', 'MasVnrType', 'BsmtFinType1', 'SalePrice','GrLivArea','GarageCars','GarageArea','TotalBsmtSF','1stFlrSF','FullBath','TotRmsAbvGrd','YearBuilt','OverallQual']
    df = pd.DataFrame(columns=columns)
    
    #Add the similarity score to the dataframe
    df['Score'] = temp['Score']
    
    #Drop the neighborhood value so it won' get from temp to df
    temp.drop(columns=['Neighborhood'],inplace=True)
    
    #load dictionary
    json1_file = open('neighborhood.json')
    json1_str = json1_file.read()
    dic = json.loads(json1_str)
 
    #map location back too hood
    comp = [temp.loc[0,'Hood_X'],temp.loc[0,'Hood_Y']]
  
    for Dict in dic:
        if comp == Dict['loc']:
            df['Neighborhood'] = Dict['adr']
        else:
            pass

    #print(temp.columns.values.tolist())
    columns = temp.columns.tolist()
    columns.pop(0)
    
    for column in columns:
        if temp.loc[0,column] == False:
            temp.drop(columns=[column],inplace=True)
        else:
            pass
        
    numFeat = []
    catFeat = []
    for feature in temp.columns:
        if temp[feature].dtype == np.float64 or temp[feature].dtype == np.int64:
            numFeat.append(feature)
        else:
            catFeat.append(feature) 
    for column in catFeat:
        x = column.split(' = ')
        df[x[0]] = x[1]
    
    fields = ['SalePrice','GrLivArea','GarageCars','GarageArea','TotalBsmtSF','1stFlrSF','FullBath','TotRmsAbvGrd','YearBuilt','OverallQual']
    
    for field in fields:
        df[field] = temp[field]
  
    df.to_csv('finished_alternative.csv', sep=',', index = False, header = True)
    
if __name__ == "__main__":
    convertAlternatives()
    postProcessing2()