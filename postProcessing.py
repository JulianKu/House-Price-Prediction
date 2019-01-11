
import csv
import re
def postProcessing():
    
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
    # substitute
    #new_csv_str = re.sub(find_str, replace_str, my_csv_text)
    
    # open new file and save
    print(my_csv_text)
    with open(my_csv_path, 'w') as f:
        f.write(my_csv_text)

 
if __name__ == "__main__":
    postProcessing()