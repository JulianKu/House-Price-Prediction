import pandas as pd 
import os 
import numpy as np  
import matplotlib.pyplot as plt  
import pandas as pd  


data = pd.read_csv("house_geo_binominal.csv") 
inputfile="test.csv"

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def distanz(input,house):    
    score = 0.0;
    for i in range(0, input.size - 1) :
        if isinstance((input[i]),str):
            if str(input[i]) == str(house[i]):
                score +=1 ; 
            else:
                score += 0;
        else:
            if input[i] == house[i]:
                if input[i] == 0.0 or house[i] == 0.0:
                    score+=0.3;
                else:
                    score+=1;
            elif input[i] == 0.0 or house[i] == 0.0:
                score+=0;
            elif (input[i] + house[i]) == 1.0:
                score+=0;
            elif is_number(house[i]) :
                a = abs(input[i] - house[i]);
                score+=1/((abs(input[i]))/(a));
    return score; 

def findsimilarhouses(inputfile):
    input = pd.read_csv(inputfile);
    df = data[list(input.columns.values)]
    scores = np.empty(len(df.index), dtype=float)
    for i in range(0, len(df.index)-1) :   
        print(i);
        scores[i] = distanz(input.iloc[0],data.iloc[i])
    df['Score'] = scores; 
    df = pd.DataFrame(df.sort_values(by=['Score'],ascending =False))
    df = pd.DataFrame(df.head())
    print(df.head())
    ## parse back to categorical! 
    df.to_csv("Similar_Houses.csv" )
    return df.head();
    
def run():
    findsimilarhouses(inputfile);
    