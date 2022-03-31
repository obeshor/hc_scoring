{"metadata":{"language_info":{"name":"python","version":"3.6.6","mimetype":"text/x-python","codemirror_mode":{"name":"ipython","version":3},"pygments_lexer":"ipython3","nbconvert_exporter":"python","file_extension":".py"},"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"}},"nbformat_minor":4,"nbformat":4,"cells":[{"cell_type":"code","source":"import os\nimport pandas as pd\nimport numpy as np\nimport gc\nimport time\nfrom contextlib import contextmanager\n\nFILE_LIST = [\"application_train\", \"application_test\", \"bureau\", \"bureau_balance\", \"credit_card_balance\", \"installments_payments\", \"POS_CASH_balance\", \"previous_application\"]\n\n@contextmanager\ndef timer(title):\n    t0 = time.time()\n    yield\n    print(\"{} - done in {:.0f}s\".format(title, time.time() - t0))\n\ndef load_csv(file_list=FILE_LIST, input_path=\"../input/home-credit-default-risk\"):\n    tab = []    \n    for file in file_list:\n        tab.append(pd.read_csv(os.path.join(input_path, file + '.csv')))\n        tab[len(tab)-1].name = file\n    return tab\n\ndef save_columns_to_csv(X, y, columns, output_path, file_name='data'):\n    df = pd.DataFrame()\n    if columns == []:\n        df = X\n    else:\n        df = X.loc[:, columns]\n    df = pd.concat([df, y], axis=1)\n    df.to_csv(os.path.join(output_path, file_name + '.csv'), index=False)\n    \ndef convert_dtypes32(df):\n    '''Changes data types to reduce memory usage\n    \n    Args:\n        df (dataframe):   DataFrame to process\n        \n    Returns:\n        DataFrame\n    '''\n    float64_cols = df.select_dtypes(include='float64').columns\n    mapper_float = {col_name: np.float32 for col_name in float64_cols}\n    df = df.astype(mapper_float)\n    \n    int64_cols = df.select_dtypes(include='int64').columns\n    mapper_int = {col_name: np.int32 for col_name in int64_cols}\n    df = df.astype(mapper_int)\n    \n    return df\n\ndef replace_365243_DAYS_by_nan(df):\n    for var in df.columns:\n        if var.startswith('DAY'):\n            df[var].replace(365243, np.nan, inplace= True)\n            \ndef rename_OHE_columns(init_cat_columns):\n    d_col = {col_name: 'x' + str(col_index) for col_index, col_name in enumerate(init_cat_columns)}\n    return [cat_col.replace(d_col[key], key) for key in d_col.keys() for cat_col in list(enc.get_feature_names()) if cat_col.startswith(d_col[key])]\n            \ndef drop_columns_nearlyempty(df, fill_rate=.5):\n    '''Drops all the columns with less than a defined percentage of non-NA values\n    \n    Args:\n        df (dataframe):   DataFrame to process\n        nb (int):         Minimum rate of rows filled\n        \n    Returns:\n        DataFrame\n    '''\n    t = df.shape[0] * fill_rate\n    return df.dropna(thresh=t, axis=1)\n\ndef one_hot_encoder(df, nan_as_category=True):\n    original_columns = list(df.columns)\n    categorical_columns = [col for col in df.columns if df[col].dtype == 'object']\n    df = pd.get_dummies(df, columns= categorical_columns, dummy_na= nan_as_category)\n    new_columns = [c for c in df.columns if c not in original_columns]\n    return df, new_columns\n    \ndef preprocess_application(df1):\n    df = df1.copy()\n    df = df[df['CODE_GENDER'] != 'XNA']\n    df['FLAG_OWN_CAR'] = df['FLAG_OWN_CAR'].map({'N': 0, 'Y': 1})\n    df['FLAG_OWN_REALTY'] = df['FLAG_OWN_REALTY'].map({'N': 0, 'Y': 1})\n    df['EMERGENCYSTATE_MODE'] = df['EMERGENCYSTATE_MODE'].map({'No': 0, 'Yes': 1})\n    df['IS_FEMALE'] = df['CODE_GENDER'].map({'M': 0, 'F': 1})\n    df.drop(['CODE_GENDER'], axis=1, inplace=True)\n    df.drop(['HOUSETYPE_MODE', 'FONDKAPREMONT_MODE', 'ORGANIZATION_TYPE', 'WALLSMATERIAL_MODE', 'OCCUPATION_TYPE'], axis=1, inplace=True)\n    df = drop_columns_nearlyempty(df)\n    \n    # Categorical features with One-Hot encode\n    df, cat_cols = one_hot_encoder(df, False)\n    \n    # NaN values for DAYS_EMPLOYED: 365.243 -> nan\n    replace_365243_DAYS_by_nan(df)\n    # Some simple new features (percentages)\n    df['DAYS_EMPLOYED_PERC'] = df['DAYS_EMPLOYED'] / df['DAYS_BIRTH']\n    df['INCOME_CREDIT_PERC'] = df['AMT_INCOME_TOTAL'] / df['AMT_CREDIT']\n    df['INCOME_PER_PERSON'] = df['AMT_INCOME_TOTAL'] / df['CNT_FAM_MEMBERS']\n    df['ANNUITY_INCOME_PERC'] = df['AMT_ANNUITY'] / df['AMT_INCOME_TOTAL']\n    df['PAYMENT_RATE'] = df['AMT_ANNUITY'] / df['AMT_CREDIT']\n    df['DAYS_EMPLOYED_PERC'].replace(np.inf, np.nan, inplace= True)\n    df['INCOME_CREDIT_PERC'].replace(np.inf, np.nan, inplace= True)\n    df['INCOME_PER_PERSON'].replace(np.inf, np.nan, inplace= True)\n    df['ANNUITY_INCOME_PERC'].replace(np.inf, np.nan, inplace= True)\n    df['PAYMENT_RATE'].replace(np.inf, np.nan, inplace= True)\n    return df\n\ndef preprocess_bureau(df1, df2):\n    df1['IS_MAIN_CURRENCY'] = (df1['CREDIT_CURRENCY'] == 'currency 1') * 1\n    df1.drop(['CREDIT_CURRENCY'], axis=1, inplace=True)\n    \n    bureau, bureau_cat = one_hot_encoder(df1, False)\n    \n    df2['STATUS'] = df2['STATUS'].map({'C': 0, '0': 0, 'X': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5})\n    \n    # Bureau balance: Perform aggregations and merge with bureau.csv\n    bb_aggregations = {'MONTHS_BALANCE': ['min', 'max', 'size']}\n    bb_agg = df2.groupby('SK_ID_BUREAU').agg(bb_aggregations)\n    bb_agg.columns = pd.Index([e[0] + \"_\" + e[1].upper() for e in bb_agg.columns.tolist()])\n    \n    bureau = bureau.join(bb_agg, how='left', on='SK_ID_BUREAU')\n    bureau.drop(['SK_ID_BUREAU'], axis=1, inplace= True)\n    del bb_agg\n    gc.collect()\n    \n    # Bureau and bureau_balance numeric features\n    num_aggregations = {\n        'DAYS_CREDIT': ['min', 'max', 'mean', 'var'],\n        'DAYS_CREDIT_ENDDATE': ['min', 'max', 'mean'],\n        'DAYS_CREDIT_UPDATE': ['mean'],\n        'CREDIT_DAY_OVERDUE': ['max', 'mean'],\n        'AMT_CREDIT_MAX_OVERDUE': ['mean'],\n        'AMT_CREDIT_SUM': ['max', 'mean', 'sum'],\n        'AMT_CREDIT_SUM_DEBT': ['max', 'mean', 'sum'],\n        'AMT_CREDIT_SUM_OVERDUE': ['mean'],\n        'AMT_CREDIT_SUM_LIMIT': ['mean', 'sum'],\n        'AMT_ANNUITY': ['max', 'mean'],\n        'CNT_CREDIT_PROLONG': ['sum'],\n        'MONTHS_BALANCE_MIN': ['min'],\n        'MONTHS_BALANCE_MAX': ['max'],\n        'MONTHS_BALANCE_SIZE': ['mean', 'sum']\n    }\n    # Bureau and bureau_balance categorical features\n    cat_aggregations = {}\n    for cat in bureau_cat: cat_aggregations[cat] = ['mean']\n    \n    bureau_agg = bureau.groupby('SK_ID_CURR').agg({**num_aggregations, **cat_aggregations})\n    bureau_agg.columns = pd.Index(['BURO_' + e[0] + \"_\" + e[1].upper() for e in bureau_agg.columns.tolist()])\n    # Bureau: Active credits - using only numerical aggregations\n    active = bureau[bureau['CREDIT_ACTIVE_Active'] == 1]\n    active_agg = active.groupby('SK_ID_CURR').agg(num_aggregations)\n    active_agg.columns = pd.Index(['ACTIVE_' + e[0] + \"_\" + e[1].upper() for e in active_agg.columns.tolist()])\n    bureau_agg = bureau_agg.join(active_agg, how='left', on='SK_ID_CURR')\n    del active, active_agg\n    gc.collect()\n    \n    # Bureau: Closed credits - using only numerical aggregations\n    closed = bureau[bureau['CREDIT_ACTIVE_Closed'] == 1]\n    closed_agg = closed.groupby('SK_ID_CURR').agg(num_aggregations)\n    closed_agg.columns = pd.Index(['CLOSED_' + e[0] + \"_\" + e[1].upper() for e in closed_agg.columns.tolist()])\n    bureau_agg = bureau_agg.join(closed_agg, how='left', on='SK_ID_CURR')\n    del closed, closed_agg, bureau\n    gc.collect()\n    \n    return bureau_agg\n\ndef preprocess_credit_card(df):\n    cc, cat_cols = one_hot_encoder(df, False)\n    # General aggregations\n    cc.drop(['SK_ID_PREV'], axis= 1, inplace = True)\n    cc_agg = cc.groupby('SK_ID_CURR').agg(['min', 'max', 'mean', 'sum', 'var'])\n    cc_agg.columns = pd.Index(['CC_' + e[0] + \"_\" + e[1].upper() for e in cc_agg.columns.tolist()])\n    # Count credit card lines\n    cc_agg['CC_COUNT'] = cc.groupby('SK_ID_CURR').size()\n    del cc\n    gc.collect()\n    return cc_agg\n\ndef preprocess_installments_payments(df):\n    # Percentage and difference paid in each installment (amount paid and installment value)\n    df['PAYMENT_PERC'] = df['AMT_PAYMENT'] / df['AMT_INSTALMENT']\n    df['PAYMENT_PERC'].replace(np.inf, np.nan, inplace= True)\n    df['PAYMENT_DIFF'] = df['AMT_INSTALMENT'] - df['AMT_PAYMENT']\n    # Days past due and days before due (no negative values)\n    df['DPD'] = df['DAYS_ENTRY_PAYMENT'] - df['DAYS_INSTALMENT']\n    df['DBD'] = df['DAYS_INSTALMENT'] - df['DAYS_ENTRY_PAYMENT']\n    df['DPD'] = df['DPD'].apply(lambda x: x if x > 0 else 0)\n    df['DBD'] = df['DBD'].apply(lambda x: x if x > 0 else 0)\n    # Features: Perform aggregations\n    aggregations = {\n        'NUM_INSTALMENT_VERSION': ['nunique'],\n        'DPD': ['max', 'mean', 'sum'],\n        'DBD': ['max', 'mean', 'sum'],\n        'PAYMENT_PERC': ['max', 'mean', 'sum', 'var'],\n        'PAYMENT_DIFF': ['max', 'mean', 'sum', 'var'],\n        'AMT_INSTALMENT': ['max', 'mean', 'sum'],\n        'AMT_PAYMENT': ['min', 'max', 'mean', 'sum'],\n        'DAYS_ENTRY_PAYMENT': ['max', 'mean', 'sum']\n    }\n    ins_agg = df.groupby('SK_ID_CURR').agg(aggregations)\n    ins_agg.columns = pd.Index(['INSTAL_' + e[0] + \"_\" + e[1].upper() for e in ins_agg.columns.tolist()])\n    # Count installments accounts\n    ins_agg['INSTAL_COUNT'] = df.groupby('SK_ID_CURR').size()\n    return ins_agg\n\ndef preprocess_POS_CASH(df):\n    pos, cat_cols = one_hot_encoder(df, False)\n    # Features\n    aggregations = {\n        'MONTHS_BALANCE': ['max', 'mean', 'size'],\n        'SK_DPD': ['max', 'mean'],\n        'SK_DPD_DEF': ['max', 'mean']\n    }\n    for cat in cat_cols:\n        aggregations[cat] = ['mean']\n    \n    pos_agg = pos.groupby('SK_ID_CURR').agg(aggregations)\n    pos_agg.columns = pd.Index(['POS_' + e[0] + \"_\" + e[1].upper() for e in pos_agg.columns.tolist()])\n    # Count pos cash accounts\n    pos_agg['POS_COUNT'] = pos.groupby('SK_ID_CURR').size()\n    del pos\n    gc.collect()\n    return pos_agg\n\ndef preprocess_previous_application(df2):\n    df = df2.copy()\n    df['NAME_YIELD_GROUP'].replace('XNA', np.nan, inplace= True)\n    df['NAME_YIELD_GROUP'] = df['NAME_YIELD_GROUP'].map({'low_normal': 1, 'low_action': 1, 'middle': 2, 'high': 3})\n\n    # only last application\n    df = df[df['FLAG_LAST_APPL_PER_CONTRACT'] == 'Y']\n    df.drop(['FLAG_LAST_APPL_PER_CONTRACT'], axis=1, inplace=True)\n\n    df.drop(['NAME_GOODS_CATEGORY', 'NAME_CASH_LOAN_PURPOSE', 'NAME_SELLER_INDUSTRY', 'NAME_TYPE_SUITE', 'PRODUCT_COMBINATION'], axis=1, inplace=True)\n\n    # new feature\n    df['APP_CREDIT_PERC'] = df['AMT_APPLICATION'] / df['AMT_CREDIT']\n    df['APP_CREDIT_PERC'].replace(np.inf, np.nan, inplace= True)\n    \n    prev, cat_cols = one_hot_encoder(df, nan_as_category= True)\n    replace_365243_DAYS_by_nan(prev)\n    \n    num_aggregations = {\n        'AMT_ANNUITY': ['min', 'max', 'mean'],\n        'AMT_APPLICATION': ['min', 'max', 'mean'],\n        'AMT_CREDIT': ['min', 'max', 'mean'],\n        'APP_CREDIT_PERC': ['min', 'max', 'mean', 'var'],\n        'AMT_DOWN_PAYMENT': ['min', 'max', 'mean'],\n        'AMT_GOODS_PRICE': ['min', 'max', 'mean'],\n        'HOUR_APPR_PROCESS_START': ['min', 'max', 'mean'],\n        'RATE_DOWN_PAYMENT': ['min', 'max', 'mean'],\n        'DAYS_DECISION': ['min', 'max', 'mean'],\n        'CNT_PAYMENT': ['mean', 'sum'],\n    }\n    # Previous applications categorical features\n    cat_aggregations = {}\n    for cat in cat_cols:\n        cat_aggregations[cat] = ['mean']\n    \n    prev_agg = prev.groupby('SK_ID_CURR').agg({**num_aggregations, **cat_aggregations})\n    prev_agg.columns = pd.Index(['PREV_' + e[0] + \"_\" + e[1].upper() for e in prev_agg.columns.tolist()])\n    # Previous Applications: Approved Applications - only numerical features\n    approved = prev[prev['NAME_CONTRACT_STATUS_Approved'] == 1]\n    approved_agg = approved.groupby('SK_ID_CURR').agg(num_aggregations)\n    approved_agg.columns = pd.Index(['APPROVED_' + e[0] + \"_\" + e[1].upper() for e in approved_agg.columns.tolist()])\n    prev_agg = prev_agg.join(approved_agg, how='left', on='SK_ID_CURR')\n    # Previous Applications: Refused Applications - only numerical features\n    refused = prev[prev['NAME_CONTRACT_STATUS_Refused'] == 1]\n    refused_agg = refused.groupby('SK_ID_CURR').agg(num_aggregations)\n    refused_agg.columns = pd.Index(['REFUSED_' + e[0] + \"_\" + e[1].upper() for e in refused_agg.columns.tolist()])\n    prev_agg = prev_agg.join(refused_agg, how='left', on='SK_ID_CURR')\n    del refused, refused_agg, approved, approved_agg, prev\n    gc.collect()\n    return prev_agg\n\ndef preprocess_tables(tab_csv, train=True, compress=True, drop_id=True):\n    if train:\n        data = preprocess_application(tab_csv[0])\n    else:\n        data = preprocess_application(tab_csv[1])\n    data = data.join(preprocess_bureau(tab_csv[2], tab_csv[3]), how='left', on='SK_ID_CURR')\n    data = data.join(preprocess_previous_application(tab_csv[7]), how='left', on='SK_ID_CURR')\n    data = data.join(preprocess_POS_CASH(tab_csv[6]), how='left', on='SK_ID_CURR')\n    data = data.join(preprocess_installments_payments(tab_csv[5]), how='left', on='SK_ID_CURR')\n    data = data.join(preprocess_credit_card(tab_csv[4]), how='left', on='SK_ID_CURR')\n    if drop_id:\n        data.drop(['SK_ID_CURR'], axis=1, inplace=True)\n    del tab_csv\n    gc.collect()\n    if compress:\n        return convert_dtypes32(data)\n    else:\n        return data","metadata":{"collapsed":false,"_kg_hide-input":false,"jupyter":{"outputs_hidden":false}},"execution_count":null,"outputs":[]}]}