import os
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import joblib

def plot_feature_importance(model, data, output_path):
    top_x = 10
    color_list =  sns.color_palette("dark", len(data.columns)) 
    
    fig, ax = plt.subplots(figsize=(40, 5), facecolor='w', edgecolor='k')
    fig.subplots_adjust(hspace = 0.5, wspace=0.8)
    
    feature_importance = model.feature_importances_
    indices = np.argsort(feature_importance)
    indices = indices[-top_x:]

    bars = ax.barh(range(len(indices)), feature_importance[indices], color='b', align='center') 
    ax.set_title("Feature importances", fontweight="normal", fontsize=16)

    plt.sca(ax)
    plt.yticks(range(len(indices)), [data.columns[j] for j in indices], fontweight="normal", fontsize=16) 
    
    for i, ticklabel in enumerate(plt.gca().get_yticklabels()):
        ticklabel.set_color(color_list[indices[i]])  

    for i,bar in enumerate(bars):
        bar.set_color(color_list[indices[i]])
    plt.box(False)
    
    plt.savefig(os.path.join(output_path, 'lgbm_feature_importances.png'), format='png', transparent=True)

def plot_precision_recall_vs_threshold():
    return 0
