Application based on Kaggle's Home Credit Default Risk competition.  

# Modelization  
## hc_transformations.py  
	- load Home Credit files		https://www.kaggle.com/c/home-credit-default-risk/data  
	- create new features, join tables and aggregate values  
	- write result to a CSV file  
## P7_scoring.ipynb  
	- select main features by logistic regression (with Lasso regularization)  
	- try several models  
	- grid search cross validation for best hyperparameters  
	- most important features of the final model  
	- threshold selection to minimize cost  
	
# hc_scoring_api  
data and results from the trained model  

# hc_scoring_dash  
Dashboard gathering information from API  
to know whether a loan application is accepted or not
