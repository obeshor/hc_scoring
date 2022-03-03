import pandas as pd
import numpy as np
import gc

def convert_dtypes32(df):
    '''Changes data types to reduce memory usage
    
    Args:
        df (dataframe):   DataFrame to process
        
    Returns:
        DataFrame
    '''
    float64_cols = df.select_dtypes(include='float64').columns
    mapper_float = {col_name: np.float32 for col_name in float64_cols}
    df = df.astype(mapper_float)
    
    int64_cols = df.select_dtypes(include='int64').columns
    mapper_int = {col_name: np.int32 for col_name in int64_cols}
    df = df.astype(mapper_int)
    
    return df

def replace_365243_DAYS_by_nan(df):
    for var in df.columns:
        if var.startswith('DAY'):
            df[var].replace(365243, np.nan, inplace= True)
            
def drop_columns_nearlyempty(df, fill_rate=.5):
    '''Drops all the columns with less than a defined percentage of non-NA values
    
    Args:
        df (dataframe):   DataFrame to process
        nb (int):         Minimum rate of rows filled
        
    Returns:
        DataFrame
    '''
    t = df.shape[0] * fill_rate
    return df.dropna(thresh=t, axis=1)

def impute_missing_data(df):
    '''Replace NaN with mode for categorical and median for numerical variables
    
    Args:
        df (dataframe):   DataFrame to process
        
    Returns:
        DataFrame
    '''
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].fillna(df[col].mode()[0])
    for col in df.select_dtypes(exclude=['object']).columns:
        df[col] = df[col].fillna(df[col].median())
    return df
        
def one_hot_encoder(df, nan_as_category=True):
    original_columns = list(df.columns)
    categorical_columns = [col for col in df.columns if df[col].dtype == 'object']
    df = pd.get_dummies(df, columns= categorical_columns, dummy_na= nan_as_category)
    new_columns = [c for c in df.columns if c not in original_columns]
    return df, new_columns
    
def preprocess_application(df1):
    df = df1.copy()
    df = df[df['CODE_GENDER'] != 'XNA']
    df['FLAG_OWN_CAR'] = df['FLAG_OWN_CAR'].map({'N': 0, 'Y': 1})
    df['FLAG_OWN_REALTY'] = df['FLAG_OWN_REALTY'].map({'N': 0, 'Y': 1})
    df['EMERGENCYSTATE_MODE'] = df['EMERGENCYSTATE_MODE'].map({'No': 0, 'Yes': 1})
    df['IS_FEMALE'] = df['CODE_GENDER'].map({'M': 0, 'F': 1})
    df.drop(['CODE_GENDER'], axis=1, inplace=True)
    df.drop(['HOUSETYPE_MODE', 'FONDKAPREMONT_MODE', 'ORGANIZATION_TYPE', 'WALLSMATERIAL_MODE', 'OCCUPATION_TYPE'], axis=1, inplace=True)
    df = drop_columns_nearlyempty(df)
    
    # Categorical features with One-Hot encode
    df, cat_cols = one_hot_encoder(df, False)
    
    # NaN values for DAYS_EMPLOYED: 365.243 -> nan
    replace_365243_DAYS_by_nan(df)
    # Some simple new features (percentages)
    df['DAYS_EMPLOYED_PERC'] = df['DAYS_EMPLOYED'] / df['DAYS_BIRTH']
    df['INCOME_CREDIT_PERC'] = df['AMT_INCOME_TOTAL'] / df['AMT_CREDIT']
    df['INCOME_PER_PERSON'] = df['AMT_INCOME_TOTAL'] / df['CNT_FAM_MEMBERS']
    df['ANNUITY_INCOME_PERC'] = df['AMT_ANNUITY'] / df['AMT_INCOME_TOTAL']
    df['PAYMENT_RATE'] = df['AMT_ANNUITY'] / df['AMT_CREDIT']
    df['DAYS_EMPLOYED_PERC'].replace(np.inf, np.nan, inplace= True)
    df['INCOME_CREDIT_PERC'].replace(np.inf, np.nan, inplace= True)
    df['INCOME_PER_PERSON'].replace(np.inf, np.nan, inplace= True)
    df['ANNUITY_INCOME_PERC'].replace(np.inf, np.nan, inplace= True)
    df['PAYMENT_RATE'].replace(np.inf, np.nan, inplace= True)
    return df

def preprocess_bureau(df1, df2):
    df1['IS_MAIN_CURRENCY'] = (df1['CREDIT_CURRENCY'] == 'currency 1') * 1
    df1.drop(['CREDIT_CURRENCY'], axis=1, inplace=True)
    
    bureau, bureau_cat = one_hot_encoder(df1, False)
    
    df2['STATUS'] = df2['STATUS'].map({'C': 0, '0': 0, 'X': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5})
    
    # Bureau balance: Perform aggregations and merge with bureau.csv
    bb_aggregations = {'MONTHS_BALANCE': ['min', 'max', 'size']}
    bb_agg = df2.groupby('SK_ID_BUREAU').agg(bb_aggregations)
    bb_agg.columns = pd.Index([e[0] + "_" + e[1].upper() for e in bb_agg.columns.tolist()])
    
    bureau = bureau.join(bb_agg, how='left', on='SK_ID_BUREAU')
    bureau.drop(['SK_ID_BUREAU'], axis=1, inplace= True)
    del bb_agg
    gc.collect()
    
    # Bureau and bureau_balance numeric features
    num_aggregations = {
        'DAYS_CREDIT': ['min', 'max', 'mean', 'var'],
        'DAYS_CREDIT_ENDDATE': ['min', 'max', 'mean'],
        'DAYS_CREDIT_UPDATE': ['mean'],
        'CREDIT_DAY_OVERDUE': ['max', 'mean'],
        'AMT_CREDIT_MAX_OVERDUE': ['mean'],
        'AMT_CREDIT_SUM': ['max', 'mean', 'sum'],
        'AMT_CREDIT_SUM_DEBT': ['max', 'mean', 'sum'],
        'AMT_CREDIT_SUM_OVERDUE': ['mean'],
        'AMT_CREDIT_SUM_LIMIT': ['mean', 'sum'],
        'AMT_ANNUITY': ['max', 'mean'],
        'CNT_CREDIT_PROLONG': ['sum'],
        'MONTHS_BALANCE_MIN': ['min'],
        'MONTHS_BALANCE_MAX': ['max'],
        'MONTHS_BALANCE_SIZE': ['mean', 'sum']
    }
    # Bureau and bureau_balance categorical features
    cat_aggregations = {}
    for cat in bureau_cat: cat_aggregations[cat] = ['mean']
    
    bureau_agg = bureau.groupby('SK_ID_CURR').agg({**num_aggregations, **cat_aggregations})
    bureau_agg.columns = pd.Index(['BURO_' + e[0] + "_" + e[1].upper() for e in bureau_agg.columns.tolist()])
    # Bureau: Active credits - using only numerical aggregations
    active = bureau[bureau['CREDIT_ACTIVE_Active'] == 1]
    active_agg = active.groupby('SK_ID_CURR').agg(num_aggregations)
    active_agg.columns = pd.Index(['ACTIVE_' + e[0] + "_" + e[1].upper() for e in active_agg.columns.tolist()])
    bureau_agg = bureau_agg.join(active_agg, how='left', on='SK_ID_CURR')
    del active, active_agg
    gc.collect()
    
    # Bureau: Closed credits - using only numerical aggregations
    closed = bureau[bureau['CREDIT_ACTIVE_Closed'] == 1]
    closed_agg = closed.groupby('SK_ID_CURR').agg(num_aggregations)
    closed_agg.columns = pd.Index(['CLOSED_' + e[0] + "_" + e[1].upper() for e in closed_agg.columns.tolist()])
    bureau_agg = bureau_agg.join(closed_agg, how='left', on='SK_ID_CURR')
    del closed, closed_agg, bureau
    gc.collect()
    
    return bureau_agg

def preprocess_credit_card(df):
    cc, cat_cols = one_hot_encoder(df, False)
    # General aggregations
    cc.drop(['SK_ID_PREV'], axis= 1, inplace = True)
    cc_agg = cc.groupby('SK_ID_CURR').agg(['min', 'max', 'mean', 'sum', 'var'])
    cc_agg.columns = pd.Index(['CC_' + e[0] + "_" + e[1].upper() for e in cc_agg.columns.tolist()])
    # Count credit card lines
    cc_agg['CC_COUNT'] = cc.groupby('SK_ID_CURR').size()
    del cc
    gc.collect()
    return cc_agg

def preprocess_installments_payments(df):
    # Percentage and difference paid in each installment (amount paid and installment value)
    df['PAYMENT_PERC'] = df['AMT_PAYMENT'] / df['AMT_INSTALMENT']
    df['PAYMENT_PERC'].replace(np.inf, np.nan, inplace= True)
    df['PAYMENT_DIFF'] = df['AMT_INSTALMENT'] - df['AMT_PAYMENT']
    # Days past due and days before due (no negative values)
    df['DPD'] = df['DAYS_ENTRY_PAYMENT'] - df['DAYS_INSTALMENT']
    df['DBD'] = df['DAYS_INSTALMENT'] - df['DAYS_ENTRY_PAYMENT']
    df['DPD'] = df['DPD'].apply(lambda x: x if x > 0 else 0)
    df['DBD'] = df['DBD'].apply(lambda x: x if x > 0 else 0)
    # Features: Perform aggregations
    aggregations = {
        'NUM_INSTALMENT_VERSION': ['nunique'],
        'DPD': ['max', 'mean', 'sum'],
        'DBD': ['max', 'mean', 'sum'],
        'PAYMENT_PERC': ['max', 'mean', 'sum', 'var'],
        'PAYMENT_DIFF': ['max', 'mean', 'sum', 'var'],
        'AMT_INSTALMENT': ['max', 'mean', 'sum'],
        'AMT_PAYMENT': ['min', 'max', 'mean', 'sum'],
        'DAYS_ENTRY_PAYMENT': ['max', 'mean', 'sum']
    }
    ins_agg = df.groupby('SK_ID_CURR').agg(aggregations)
    ins_agg.columns = pd.Index(['INSTAL_' + e[0] + "_" + e[1].upper() for e in ins_agg.columns.tolist()])
    # Count installments accounts
    ins_agg['INSTAL_COUNT'] = df.groupby('SK_ID_CURR').size()
    return ins_agg

def preprocess_POS_CASH(df):
    pos, cat_cols = one_hot_encoder(df, False)
    # Features
    aggregations = {
        'MONTHS_BALANCE': ['max', 'mean', 'size'],
        'SK_DPD': ['max', 'mean'],
        'SK_DPD_DEF': ['max', 'mean']
    }
    for cat in cat_cols:
        aggregations[cat] = ['mean']
    
    pos_agg = pos.groupby('SK_ID_CURR').agg(aggregations)
    pos_agg.columns = pd.Index(['POS_' + e[0] + "_" + e[1].upper() for e in pos_agg.columns.tolist()])
    # Count pos cash accounts
    pos_agg['POS_COUNT'] = pos.groupby('SK_ID_CURR').size()
    del pos
    gc.collect()
    return pos_agg

def preprocess_previous_application(df2):
    df = df2.copy()
    df['NAME_YIELD_GROUP'].replace('XNA', np.nan, inplace= True)
    df['NAME_YIELD_GROUP'] = df['NAME_YIELD_GROUP'].map({'low_normal': 1, 'low_action': 1, 'middle': 2, 'high': 3})

    # only last application
    df = df[df['FLAG_LAST_APPL_PER_CONTRACT'] == 'Y']
    df.drop(['FLAG_LAST_APPL_PER_CONTRACT'], axis=1, inplace=True)

    df.drop(['NAME_GOODS_CATEGORY', 'NAME_CASH_LOAN_PURPOSE', 'NAME_SELLER_INDUSTRY', 'NAME_TYPE_SUITE', 'PRODUCT_COMBINATION'], axis=1, inplace=True)

    # new feature
    df['APP_CREDIT_PERC'] = df['AMT_APPLICATION'] / df['AMT_CREDIT']
    df['APP_CREDIT_PERC'].replace(np.inf, np.nan, inplace= True)
    
    prev, cat_cols = one_hot_encoder(df, nan_as_category= True)
    replace_365243_DAYS_by_nan(prev)
    
    num_aggregations = {
        'AMT_ANNUITY': ['min', 'max', 'mean'],
        'AMT_APPLICATION': ['min', 'max', 'mean'],
        'AMT_CREDIT': ['min', 'max', 'mean'],
        'APP_CREDIT_PERC': ['min', 'max', 'mean', 'var'],
        'AMT_DOWN_PAYMENT': ['min', 'max', 'mean'],
        'AMT_GOODS_PRICE': ['min', 'max', 'mean'],
        'HOUR_APPR_PROCESS_START': ['min', 'max', 'mean'],
        'RATE_DOWN_PAYMENT': ['min', 'max', 'mean'],
        'DAYS_DECISION': ['min', 'max', 'mean'],
        'CNT_PAYMENT': ['mean', 'sum'],
    }
    # Previous applications categorical features
    cat_aggregations = {}
    for cat in cat_cols:
        cat_aggregations[cat] = ['mean']
    
    prev_agg = prev.groupby('SK_ID_CURR').agg({**num_aggregations, **cat_aggregations})
    prev_agg.columns = pd.Index(['PREV_' + e[0] + "_" + e[1].upper() for e in prev_agg.columns.tolist()])
    # Previous Applications: Approved Applications - only numerical features
    approved = prev[prev['NAME_CONTRACT_STATUS_Approved'] == 1]
    approved_agg = approved.groupby('SK_ID_CURR').agg(num_aggregations)
    approved_agg.columns = pd.Index(['APPROVED_' + e[0] + "_" + e[1].upper() for e in approved_agg.columns.tolist()])
    prev_agg = prev_agg.join(approved_agg, how='left', on='SK_ID_CURR')
    # Previous Applications: Refused Applications - only numerical features
    refused = prev[prev['NAME_CONTRACT_STATUS_Refused'] == 1]
    refused_agg = refused.groupby('SK_ID_CURR').agg(num_aggregations)
    refused_agg.columns = pd.Index(['REFUSED_' + e[0] + "_" + e[1].upper() for e in refused_agg.columns.tolist()])
    prev_agg = prev_agg.join(refused_agg, how='left', on='SK_ID_CURR')
    del refused, refused_agg, approved, approved_agg, prev
    gc.collect()
    return prev_agg

def preprocess_tables(tab_csv, train=True, compress=True):
    if train:
        data = preprocess_application(tab_csv[0])
    else:
        data = preprocess_application(tab_csv[1])
    data = data.join(preprocess_bureau(tab_csv[2], tab_csv[3]), how='left', on='SK_ID_CURR')
    data = data.join(preprocess_previous_application(tab_csv[7]), how='left', on='SK_ID_CURR')
    data = data.join(preprocess_POS_CASH(tab_csv[6]), how='left', on='SK_ID_CURR')
    data = data.join(preprocess_installments_payments(tab_csv[5]), how='left', on='SK_ID_CURR')
    data = data.join(preprocess_credit_card(tab_csv[4]), how='left', on='SK_ID_CURR')
    data.drop(['SK_ID_CURR'], axis=1, inplace=True)
    del tab_csv
    gc.collect()
    if compress:
        return convert_dtypes32(data)
    else:
        return data