import pandas as pd
import numpy as np
import os
import time
import json
from lightgbm import LGBMClassifier
#from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.model_selection import KFold, RepeatedStratifiedKFold, StratifiedKFold, cross_val_score, train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.compose import ColumnTransformer
from sklearn.tree import DecisionTreeClassifier
from sklearn.impute import SimpleImputer
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression, LogisticRegressionCV
from imblearn.pipeline import Pipeline, make_pipeline
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from xgboost import XGBClassifier
from imblearn.pipeline import Pipeline, make_pipeline
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
import seaborn as sns
import matplotlib.pyplot as plt
import joblib

def train_model(model, X_train, y_train, X_test, y_test): 
    pipe = Pipeline([('imputer', SimpleImputer(strategy='median')), ('scaler', StandardScaler()), ('clf', model["clf"])])
    start_time = time.time()
    pipe.fit(X_train, y_train)
    train_time = time.time() - start_time

    train_rocauc_score = roc_auc_score(y_train, pipe.predict_proba(X_train)[:, 1])
    test_rocauc_score = roc_auc_score(y_test, pipe.predict_proba(X_test)[:, 1])
    model_details = {"name": model["name"], "train_rocauc":train_rocauc_score, "test_rocauc":test_rocauc_score, "train_time": train_time, "model": pipe}
    return model_details
    
def train_models(data, labels):
    X = data
    y = labels.values
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)
    
    trained_models = []
    models = [
             {"name": "Naive Bayes", "clf": GaussianNB()},
             {"name": "logistic regression", "clf": LogisticRegression(solver='saga', max_iter=500, class_weight='balanced')}, 
             {"name": "Decision Tree", "clf": DecisionTreeClassifier(class_weight='balanced')},
             #{"name": "SVM", "clf": SVC(probability=True, class_weight='balanced', random_state=42)},
             {"name": "XG Boost", "clf": XGBClassifier(use_label_encoder=False, random_state=42)},
             {"name": "Random Forest", "clf": RandomForestClassifier(n_estimators=100, class_weight='balanced')},
             {"name": "Gradient Boosting", "clf": GradientBoostingClassifier(n_estimators=100)}, 
             {"name": "Light GBM Classifier", "clf": LGBMClassifier(class_weight='balanced', random_state=42)}]

    for model in models:
        print(model['name'])
        model_details = train_model(model, X_train, y_train, X_test, y_test)
        trained_models.append(model_details)
    return trained_models
    
def plot_training_scores(trained_models, output_path):
    model_df = pd.DataFrame(trained_models)
    model_df.sort_values("test_rocauc", inplace=True) 
    ax = model_df[["train_rocauc", "test_rocauc", "name"]].plot(kind="line", x="name", figsize=(19,5), title="Classifier Performance Sorted by Test ROC AUC")
    ax.legend(["Train ROC AUC", "Test ROC AUC"])
    for p in ax.patches:
        ax.annotate(str(round(p.get_height(),3)), (p.get_x() * 1.005, p.get_height() * 1.005))

    ax.title.set_size(20)
    plt.box(False)
    plt.savefig(os.path.join(output_path, 'test_classifier_performance.png'), format='png', transparent=True)
    
def plot_training_times(trained_models, output_path):
    model_df = pd.DataFrame(trained_models)
    model_df.sort_values("train_time", inplace=True)
    ax= model_df[["train_time","name"]].plot(kind="line", x="name", figsize=(19,5), grid=True, title="Classifier Training Time (seconds)")
    ax.title.set_size(20)
    ax.legend(["Train Time"])
    plt.box(False)  
    plt.savefig(os.path.join(output_path, 'test_classifier_time_performance.png'), format='png', transparent=True)

def train_optimized_XGBoost(X, y, grid_parameters, cv):
    train_optimized_model(X, y, XGBClassifier(use_label_encoder=False, eval_metric='aucpr', random_state=42))

def train_optimized_LGBM(X, y, grid_parameters, cv):
    train_optimized_model(X, y, LGBMClassifier(), grid_parameters, cv)
    
def train_optimized_model(X, y, model, grid_parameters, cv):
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)
    #clf = grid_search_imbalanced_data(X_train, y_train, X_test, y_test, model, grid_parameters)
    clf = grid_search_hyperparameters(X_train, y_train, X_test, y_test, model, grid_parameters, cv)
    joblib.dump(clf, 'trained_model.joblib') 
    with open('best_params.json', 'w', encoding='utf-8') as f:
        json.dump(clf.best_params_, f, ensure_ascii=False, indent=4)
    print(clf.best_params_)
    print(clf.best_score_)
    print('AUC test', roc_auc_score(y_test, clf.predict_proba(X_test)[:, 1]))
    plot_feature_importance(clf.best_estimator_['model'].feature_importances_, X.columns)
    
def grid_search_imbalanced_data(X_train, y_train, X_test, y_test, model, SMOTE_parameters, cv):
    over = SMOTE()
    under = RandomUnderSampler()
    steps = [('imputer', SimpleImputer(strategy='median')), ('scaler', StandardScaler()), ('over', over), ('under', under), ('model', model)]
    pipeline = Pipeline(steps=steps)
        
    #parameters = [{'over__sampling_strategy':[0.1, 0.15, 0.2], 'under__sampling_strategy':[0.6, 0.7]},
    #                {'over__sampling_strategy':[0.1, 0.2, 0.3]}]
    
    clf = GridSearchCV(pipeline, SMOTE_parameters, n_jobs=-1, scoring='roc_auc', cv=cv)
    clf.fit(X_train, y_train)
    return clf
    
def grid_search_hyperparameters(X_train, y_train, X_test, y_test, model, grid_parameters, cv):
    over = SMOTE(sampling_strategy=0.1)
    under = RandomUnderSampler(sampling_strategy=0.6)
    steps = [('imputer', SimpleImputer(strategy='median')), ('scaler', StandardScaler()), ('over', over), ('under', under), ('model', model)]
    pipeline = Pipeline(steps=steps)
        
    #parameters = {'model__n_estimators':[1500],
    #             #'model__learning_rate':[0.01],
    #             #'model__max_depth':[2],
    #             'model__max_features':[300],
    #             }

    clf = GridSearchCV(pipeline, grid_parameters, n_jobs=-1, scoring='roc_auc', cv=cv)
    clf.fit(X_train, y_train)
    cvres = clf.cv_results_
    for mean_score, params in zip(cvres["mean_test_score"], cvres["params"]):
        print(mean_score, params)
    return clf

def plot_feature_importance(feature_importances, columns):    
    color_list =  sns.color_palette("dark", len(columns)) 
    top_x = 10
    
    fig, ax = plt.subplots(figsize=(40, 5), facecolor='w', edgecolor='k')
    fig.subplots_adjust(hspace = 0.5, wspace=0.8)

    indices = np.argsort(feature_importances)
    indices = indices[-top_x:]

    bars = ax.barh(range(len(indices)), feature_importances[indices], color='b', align='center') 
    ax.set_title( 'Feature importances', fontweight="normal", fontsize=16)

    plt.sca(ax)
    plt.yticks(range(len(indices)), [columns[j] for j in indices], fontweight="normal", fontsize=16)
    plt.autoscale()
    plt.savefig('feature_importance.png', format='png', transparent=True)