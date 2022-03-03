import os
import pandas as pd
import random

def load_csv(file_list, input_path):
    tab = []    
    for file in file_list:
        tab.append(pd.read_csv(os.path.join(input_path, file + '.csv')))
        tab[len(tab)-1].name = file
    return tab
    
def save_csv(X, y, indices, output_path, file_name='data'):
    df = pd.DataFrame()
    if indices == []:
        df = X
    else:
        df = X.iloc[:, indices]
    df = pd.concat([df, y], axis=1)
    df.to_csv(os.path.join(output_path, file_name + '.csv'), index=False)
    
def save_columns_to_csv(X, y, columns, output_path, file_name='data'):
    df = pd.DataFrame()
    if columns == []:
        df = X
    else:
        df = X.loc[:, columns]
    df = pd.concat([df, y], axis=1)
    df.to_csv(os.path.join(output_path, file_name + '.csv'), index=False)
    
def get_test_application(input_path):
    df = pd.read_csv(os.path.join(input_path, 'application_test.csv'))
    idx_max = df.shape[0]
    idx = random.randint(0, idx_max)
    return df.iloc[idx]