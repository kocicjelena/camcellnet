from flask import Flask, render_template, request
import numpy as np
from scipy import stats
import pandas as pd
import re

Flask_App = Flask(__name__) 

result1=None
result2=None
table_data_a2=None
table_data_a3=None
table_data_b21=None
table_data_b22=None
table_data_a3_calculated=[]
table_data_a2_calculated=[]
table_data_b2_calculated=[] 
table_data_b22_calculated=[]
max_abudance=[]


file_path_a = 'static/9606_abund.txt'
first_file = pd.read_csv(file_path_a, sep='\t')
first_result = first_file.groupby('Gn')['Mean-copy-number'].apply(list).to_dict()
if 'Gn' in first_result:
    del first_result['Gn']
else:
    print("'Gn' not found in dictionary")
first_result = {key: [float(x) for x in value if x != 'Mean'] for key, value in first_result.items()}
unique_mean_ar = first_file['Mean-copy-number'].unique()
unique_mean_arr = [k for k in unique_mean_ar if k != 'Mean']
np_arr_unique_mean_array =np.array(unique_mean_arr)
unique_mean_array = np_arr_unique_mean_array.astype(float)
min_unique = min(unique_mean_array)
a1=first_file[['Gn', 'Mean-copy-number']].drop_duplicates().shape[0]


file_path_b = 'static/9606_gn_dom.txt'
second_file = pd.read_csv(file_path_b, sep='\t')
second_result = second_file.groupby('#Gn')['Domain'].apply(list).to_dict()
second_result_eval = second_file.groupby('Domain')['Eval'].apply(list).to_dict()
second_calc={}
second_calc_mean={}
second_calc_sd={}
second_calc_percentile={}
for second_key, second_value in second_result_eval.items():
    second_arr =np.array(second_value)
    second_arr = second_arr.astype(float)
    second_mean = np.mean(second_arr)
    second_st_dev =np.std(second_arr)
    if second_key in second_calc_mean:
        second_calc_mean(second_key, []).append(second_mean)
    else:
        second_calc_mean[second_key]=second_mean
    max_abudance.append(second_mean)
    for k, v in second_result.items():
        if second_key in v:
            if k in second_calc:
                second_calc[k].append(second_mean)
            else:
                second_calc[k]=[second_mean]

table_data_b2_calculated = [[k,np.mean(second_calc[k]),np.std(second_calc[k])] for k,v in second_calc.items()]
range_percent=[k[1] for k in table_data_b2_calculated]
table_data_b22_calculated = [[k[0],stats.percentileofscore(range_percent, k[1])] for k in table_data_b2_calculated]


@Flask_App.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@Flask_App.route('/answer/', methods=['POST'])
def answer():
    result1=None
    result2=None
    table_data_a2=None
    table_data_a3=None
    table_data_b2=None
    table_data_b22=None
    
    for key, value in first_result.items():

        np_arr =np.array(value)
        np_arr = np_arr.astype(float)
        if len(np_arr)>0:
            mean = np.mean(np_arr)
        else:
            mean = None
        st_dev =np.std(np_arr)
        temp = [key, mean, st_dev]
        table_data_a2_calculated.append(temp)
    
    if mean is not None:
        table_data_a3_calculated.append([key,stats.percentileofscore(unique_mean_array, mean)])
    else:
        table_data_a3_calculated.append([key,0])

    if 'answer1' in request.form:
        result1=a1
    elif 'answer2' in request.form:
        table_data_a3=None
        table_data_a2=np.array(table_data_a2_calculated)[:10,:]
    elif 'answer3' in request.form:
        table_data_a3=np.array(table_data_a3_calculated)[:10,:]
    elif 'banswer1' in request.form:
        result1=None
        #table_data_b2=None
        result2=max(max_abudance)
        #table_data_a3=None
    elif 'banswer2' in request.form:
        table_data_a3=None
        table_data_b22=np.array(table_data_b22_calculated)[:10,:]
        table_data_b2=np.array(table_data_b2_calculated)[:10,:]
    else:
        pass
    
    return render_template(
            'index.html',
            result1=result1,
            result2=result2,
            table_data_a2=table_data_a2,
            table_data_a3=table_data_a3,
            table_data_b2=table_data_b2,
            table_data_b22=table_data_b22
        )
    

if __name__ == '__main__':
    # Flask_App.debug = True
    Flask_App.run()
