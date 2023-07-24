from flask import Flask, render_template, request
import numpy as np
from scipy import stats
import pandas as pd
import re

Flask_App = Flask(__name__) 



file_path_a = 'static/9606_abund.txt'
first_file = pd.read_csv(file_path_a, sep='\t')
a = first_file[["Gn", "Mean-copy-number"]]

# A1
temp_a = a[["Gn", "Mean-copy-number"]].drop_duplicates()
a1 = temp_a.shape[0]

# A2
temp_a['Mean-copy-number'] = pd.to_numeric(temp_a['Mean-copy-number'], errors='coerce')
# SeriesGroupBy object will contain groups of values from the ‘Mean-copy-number’ column, 
# where each group corresponds to a unique value in the ‘Gn’ column.
temp_aa = temp_a['Mean-copy-number'].groupby(temp_a['Gn'])
temp_a_mean  = temp_aa.mean().reset_index()
temp_a_mean.columns = ['Gn','Mean']
temp_a_std  = temp_aa.std().reset_index()
temp_a_std.columns = ['Gn','std']
a2 = pd.merge(temp_a_mean, temp_a_std, on="Gn")

# A3
a3 = a2.copy()
a3['percentile_rank'] = a3['Mean'].rank(pct=True) * 100
a3.drop(['Mean', 'std'], axis=1)
# TO DO: delete for real case (only 20 rows shown)
# a2.head(20)
# a3.head(20)

# B
file_path_b = 'static/9606_gn_dom.txt'
second_file = pd.read_csv(file_path_b, sep='\t')

#  - combining the data from two files -
#  Rough assumtion for getting the data from 9606_abund: 
#  percentile of abundace of the gene is the measure
#  of abundance of the domains of that gene

def weighted_mean(group):
    weights = group['End'] - group['Start']
    return (group['percentile_rank'] / 100) *((group['Eval'] * weights).sum() / weights.sum())

second_file.columns = second_file.columns.str.replace("#Gn", "Gn")

# combine the files
comb = pd.merge(second_file, a3, on = "Gn", how = "inner")

# DataFrameGroupBy object will contain groups of rows from the comb dataframe, 
# where each group corresponds to a unique combination of values in both the ‘Gn’ and ‘Domain’ columns.
grouped = comb.groupby(['Gn', 'Domain'])
abundance = grouped.apply(weighted_mean)

# B1
b1 = abundance.groupby(level='Domain').mean().max()

# B2
b21_mean = abundance.groupby(level='Domain').mean().reset_index()
b21_mean.columns = ['Domain','Mean']
b21_std = abundance.groupby(level='Domain').std().reset_index()
b21_std.columns = ['Domain','STD']
b21 = pd.merge(b21_mean, b21_std, on="Domain")
b22=b21.copy()
# percentile rank in % (calculation * 100)
b22['percentile_rank'] = b22['Mean'].rank(pct=True) * 100

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
      
    if 'answer1' in request.form:
        result1=a1
    elif 'answer2' in request.form:
        table_data_a2=a2.head(20).to_html(classes='table table-striped', index=False)
    elif 'answer3' in request.form:
        table_data_a3=a3.drop(['Mean', 'std'], axis=1).head(20).to_html(classes='table table-striped', index=False)
    elif 'banswer1' in request.form:
        result2=b1
    elif 'banswer2' in request.form:
        table_data_b2=b21.head(20).to_html(classes='table table-striped', index=False)
        table_data_b22=b22.drop(['Mean', 'STD'], axis=1).head(20).to_html(classes='table table-striped', index=False)
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


