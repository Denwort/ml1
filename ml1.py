# -*- coding: utf-8 -*-
"""MachineLearning_1Testa.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1MYCKg2YUs4IH8ubGPkb2OyJH6y3moQMV

David Mamani: realizo la funcion load(), plotVariables(), nullAnalysis(), normalizarBoxCox(), normalizarPowerTransformer(), plotNormalizacion(), ols(), normalEquation(), linearR(), linearRegression(), polinomial(), polinomialRegression(),

Piero Rozas: realizo la funcion analisisNumerica(), removeOutliers(), scaleMinMax(), scaleMaxAbs(), scaleStandard(), scaleRobust(), correlation(), forward_selection(), selectFeatures(), main(),
"""

import math
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np

from sklearn.preprocessing import MinMaxScaler, StandardScaler, PowerTransformer, MaxAbsScaler, RobustScaler

from scipy.stats import boxcox

from sklearn.model_selection import train_test_split
import statsmodels.api as sm
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error,r2_score
from sklearn.linear_model import Ridge, Lasso, ElasticNet
from sklearn.preprocessing import PolynomialFeatures

from sklearn.feature_selection import RFE
from sklearn.linear_model import LogisticRegression

# Cargar el csv
def load():
  path="/content/TSLA.csv"
  df=pd.read_csv(path,delimiter=',')
  df['Date']=pd.to_datetime(df['Date'])
  df['Date'] = df['Date'].astype('int64')
  return df

# Analisis exploratorio
# Graficar algunas variables
def plotVariables(data):
  print(data.info())
  print(data.describe())
  plt.figure(figsize=(15,5))
  plt.plot(data['Volume'])
  plt.title('Tesla Volume.', fontsize=15)
  plt.ylabel('Volume')
  plt.show()

# Histograma y diagrama de caja
def analisisNumericas(df):
  varNumericas = df.select_dtypes(include=np.number).columns
  for numerica in varNumericas:
    print("#"*20,numerica,"#"*20)
    df[numerica].plot.hist(bins=25,figsize=(8,4))
    plt.title(f'{numerica} \n',fontdict={'fontsize':16})
    plt.show()
    print("\n")
    df[numerica].plot.box(figsize=(8,4))
    plt.show()
    print("\n\n")

# Analisis de nulos
def nullAnalysis(df):
  null_columns=df.isnull().any()
  print("Nulos en columnas:")
  print(null_columns)
  null_sum = df.isnull().sum()
  print("Suma de nulos:")
  print(null_sum)

# Tratar outliers

def removeOutliers(df, variable):
  Q1 = df[variable].quantile(0.25)
  Q3 = df[variable].quantile(0.75)
  IQR = Q3 - Q1
  lower = Q1 - 1.5*IQR
  upper = Q3 + 1.5*IQR

  # Create arrays of Boolean values indicating the outlier rows
  upper_array = np.where(df[variable] >= upper)[0]
  lower_array = np.where(df[variable] <= lower)[0]

  # Removing the outliers
  df.drop(index=upper_array, inplace=True)
  df.drop(index=lower_array, inplace=True)
  return df

# Escalamientop

# Escalamiento de 0 a 1
def scaleMinMax(df, variable):
  minmax_scaler = MinMaxScaler()
  df[variable] = minmax_scaler.fit_transform(df[[variable]])
  return df

# Escalamiento de -1 a 1
def scaleMaxAbs(df, variable):
  maxabs_scaler = MaxAbsScaler()
  df[variable] = maxabs_scaler.fit_transform(df[[variable]])
  return df

# Escalamiento alrededor de la media usando la varianza
def scaleStandard(df, variable):
  standard_scaler = StandardScaler()
  df[variable] = standard_scaler.fit_transform(df[[variable]])
  return df

# Escalamiento robusto contra outliers
def scaleRobust(df, variable):
  robust_scaler = RobustScaler()
  df[variable] = robust_scaler.fit_transform(df[[variable]])
  return df

# Normalizacion

# Adaptar a una distribucion estandar. BoxCox acepta solo valores positivos
def normalizarBoxCox(df, variable):
  data_to_normalize=df[variable]
  variable_to_normalize=variable
  data_normalized,lambda_value=boxcox(data_to_normalize)
  return data_normalized,lambda_value

# Adaptar a una distribucion estandar. Yeo-johnson acepta valores positivos y negativos
def normalizarPowerTransformer(df, variable):
  pw_transf = PowerTransformer(method='yeo-johnson')
  data_normalized = pw_transf.fit_transform(df[[variable]])
  return data_normalized, pw_transf.lambdas_[0]

# Graficar el df original vs el df normalizado
def plotNormalizacion(df, variable, transformada, lambda_value):
  X = df[variable]
  plt.figure(figsize=(12,6))
  plt.subplot(1,2,1)
  plt.hist(X,bins=20,color='b',alpha=0.7)
  plt.title('Datos antes')
  plt.xlabel(variable)
  plt.ylabel('Frecuencia')

  plt.subplot(1,2,2)
  plt.hist(transformada,bins=20,color='r',alpha=0.7)
  plt.title('Datos despues')
  plt.xlabel('transformado '+variable)
  plt.ylabel('Frecuencia')

  plt.tight_layout()
  plt.show()
  print("valor de lambda ",lambda_value)

# Regresion simple

# NormalEcuation
def normalEquation(df, var_x, var_y):
  # Calculates intercept and slope using normal equation
  X = df[[var_x]].values
  y = df[var_y].values
  y_res = y.reshape(-1,1)
  X_intercept=np.c_[np.ones(X.shape[0]),X]
  theta=np.linalg.inv(X_intercept.T.dot(X_intercept)).dot(X_intercept.T).dot(y)
  intercept = theta[0]
  slope = theta[1]
  print("intercept ",intercept," slope ",slope)
  # Plot the regression
  plt.scatter(X,y,alpha=0.5,label='Original Data')
  x_values=np.linspace(X.min(),X.max(),100)
  y_values=intercept+slope*x_values
  plt.plot(x_values,y_values,color='green',label='Linear Regressor Line')
  plt.xlabel('Variable')
  plt.ylabel('Volume')
  plt.legend()
  plt.grid(True)
  plt.show()
  y_test = y_res
  y_test_pred = intercept+slope*X
  mape = np.mean(np.abs((y_test - y_test_pred) / y_test)) * 100
  rmse = math.sqrt(mean_squared_error(y_test, y_test_pred))
  r2=r2_score(y_test,y_test_pred)
  # Metricas
  print("R2: ", r2)
  print("RMSE: ", rmse)
  print("MAPE: ", mape)
  print("\n")
  return intercept, slope

# LinealRegression: Single variable
def linearR(df, var_x, var_y):
  # Create the regression
  X = df[[var_x]].values
  y = df[var_y].values
  y_reshaped = y.reshape(-1,1)
  model=LinearRegression()
  model.fit(X,y_reshaped)
  y_pred=model.predict(X)
  # Plot the original data vs predicted data
  plt.scatter(X,y,label='Original data')
  plt.plot(X,y_pred,color='red',label='Linear Regression')
  plt.xlabel(var_x)
  plt.ylabel(var_y)
  plt.title(f'Linear Regression {var_x} vs {var_y}')
  plt.legend()
  plt.show()
  y_test = y_reshaped
  y_test_pred = y_pred
  mape = np.mean(np.abs((y_test - y_test_pred) / y_test)) * 100
  rmse = math.sqrt(mean_squared_error(y_test, y_test_pred))
  r2=r2_score(y_test,y_test_pred)
  print("R2: ", r2)
  print("RMSE: ", rmse)
  print("MAPE: ", mape)
  print("\n")

# Polinomial simple
def polinomial(data, predictor, target):
  # Create the regression
  X=data[[predictor]].values
  y=data[target].values
  regr=LinearRegression()
  cubic=PolynomialFeatures(degree=3)
  X_cubic=cubic.fit_transform(X)
  regr=regr.fit(X_cubic, y)
  predictions = regr.predict(X_cubic)
  real = y
  # Plot the regression
  x_max=np.max([np.max(predictions),np.max(predictions)])
  x_min=np.min([np.min(predictions),np.min(predictions)])
  # Fit plots the predicted values vs the residuals
  fig,ax=plt.subplots(1,1,figsize=(7,3),sharey=True)
  ax.scatter(predictions,predictions-y,c='limegreen',marker='s',edgecolor='white',label='Real data')
  ax.set_ylabel('Residuals')
  ax.set_xlabel('Predicted values')
  ax.legend()
  ax.hlines(y=0,xmin=x_min,xmax=x_max,color='black',lw=2)
  plt.tight_layout()
  plt.show()
  # Metricas
  mape = np.mean(np.abs((real - predictions) / real)) * 100
  rmse = math.sqrt(mean_squared_error(real, predictions))
  r2=r2_score(real,predictions)
  print("R2: ", r2)
  print("RMSE: ", rmse)
  print("MAPE: ", mape)
  print("\n")

# Regresion multiple

# OLS
def ols(df, variable):
  print("OLS")
  # Fit Ordinary Least Squares (OLS) regression model on training data
  X = df.drop(columns=[variable])
  y = df[variable]
  X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=123)
  X_train_with_intercept = sm.add_constant(X_train) # Add intercept term
  ols_model = sm.OLS(y_train, X_train_with_intercept).fit()
  print(ols_model.summary())
  # Predictions on the training and test sets
  X_test_with_intercept = sm.add_constant(X_test) # Add intercept term
  predictions_test = ols_model.predict(X_test_with_intercept)
  predictions_train = ols_model.predict(X_train_with_intercept)

  # Calculate RMSE and R-squared for training data
  residuals_train = y_train - predictions_train
  mse_train = np.mean(residuals_train ** 2)
  rmse_train = np.sqrt(mse_train)
  r_squared_train = ols_model.rsquared
  # Calculate RMSE and R-squared and MAPE for testing data
  residuals_test = y_test - predictions_test
  mse_test = np.mean(residuals_test ** 2)
  rmse_test = np.sqrt(mse_test)
  mape = np.mean(np.abs((y_test - predictions_test) / y_test)) * 100
  r_squared_test = 1 - (np.sum(residuals_test ** 2) / np.sum((y_test - np.mean(y_test)) ** 2))

  # Plot actual vs. predicted values for training data
  plt.figure(figsize=(10, 6))
  plt.scatter(y_train, predictions_train, alpha=0.5)
  plt.plot([y_train.min(), y_train.max()], [y_train.min(), y_train.max()], 'k--', lw=2)
  plt.xlabel('Actual Values (Training)')
  plt.ylabel('Predicted Values (Training)')
  plt.title('Actual vs. Predicted Values (Training)')
  plt.grid(True)
  plt.show()
  # Plot actual vs. predicted values for testing data
  plt.figure(figsize=(10, 6))
  plt.scatter(y_test, predictions_test, alpha=0.5)
  # Plot diagonal line
  plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'k--', lw=2)
  plt.xlabel('Actual Values (Testing)')
  plt.ylabel('Predicted Values (Testing)')
  plt.title('Actual vs. Predicted Values (Testing)')
  plt.grid(True)
  plt.show()
  # Metricas
  print("R2: ", r_squared_test)
  print("RMSE: ", rmse_test)
  print("MAPE: ", mape)
  print("\n")

# LinealRegression, Ridge, Lasso, Elastic Net
def linearRegression(tipo, data, target):
  print(tipo)
  # Create linealRegression with its predictions
  features=data.columns[data.columns!=target]
  X=data[features].values
  y=data[target].values
  X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=0.3,random_state=200)
  # Create the models
  if tipo == "linear":
    model=LinearRegression()
  elif tipo == "ridge":
    model=Ridge(alpha=10)
  elif tipo == "lasso":
    model=Lasso(alpha=10)
  elif tipo == "elasticnet":
    model=ElasticNet(random_state=123)
  model.fit(X_train,y_train)
  y_train_pred=model.predict(X_train)
  y_test_pred=model.predict(X_test)
  x_max=np.max([np.max(y_train_pred),np.max(y_test_pred)])
  x_min=np.min([np.min(y_train_pred),np.min(y_test_pred)])
  # Fit plots the predicted values vs the residuals
  fig,(ax1,ax2)=plt.subplots(1,2,figsize=(7,3),sharey=True)
  ax1.scatter(y_test_pred,y_test_pred-y_test,c='limegreen',marker='s',edgecolor='white',label='Test data')
  ax2.scatter(y_train_pred,y_train_pred-y_train,c='steelblue',marker='s',edgecolor='white',label='Training data')
  ax1.set_ylabel('Residuals')
  for ax in (ax1,ax2):
    ax.set_xlabel('Predicted values')
    ax.legend()
    ax.hlines(y=0,xmin=x_min,xmax=x_max,color='black',lw=2)
  plt.tight_layout()
  plt.show()
  # Metricas
  mape = np.mean(np.abs((y_test - y_test_pred) / y_test)) * 100
  rmse = math.sqrt(mean_squared_error(y_test, y_test_pred))
  r2=r2_score(y_test,y_test_pred)
  print("R2: ", r2)
  print("RMSE: ", rmse)
  print("MAPE: ", mape)
  print("\n")

# PolinomialRegression (PolynomialFeatures)
def polinomialRegression(data, target, grados):
  # Create the model
  print("Polinomial grado ",grados)
  X=data.drop(columns=[target]).values
  y=data[target].values
  x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=2)
  poly = PolynomialFeatures(degree=grados, include_bias=True)
  x_train_trans = poly.fit_transform(x_train)
  x_test_trans = poly.transform(x_test)
  lr = LinearRegression()
  lr = lr.fit(x_train_trans, y_train)
  predictions = lr.predict(x_test_trans)
  real = y_test
  # Plot the regression
  x_max=np.max([np.max(predictions),np.max(predictions)])
  x_min=np.min([np.min(predictions),np.min(predictions)])
  # Fit plots the predicted values vs the residuals
  fig,ax=plt.subplots(1,1,figsize=(7,3),sharey=True)
  ax.scatter(predictions,predictions-real,c='limegreen',marker='s',edgecolor='white',label='Real data')
  ax.set_ylabel('Residuals')
  ax.set_xlabel('Predicted values')
  ax.legend()
  ax.hlines(y=0,xmin=x_min,xmax=x_max,color='black',lw=2)
  plt.tight_layout()
  plt.show()
  # Metricas
  mape = np.mean(np.abs((real - predictions) / real)) * 100
  rmse = math.sqrt(mean_squared_error(real, predictions))
  r2=r2_score(real,predictions)
  print("R2: ", r2)
  print("RMSE: ", rmse)
  print("MAPE: ", mape)
  print("\n")

from scipy import stats

# Feature Engineering

def correlation(df):
  # Plot correlations
  corr=df.corr()['Volume'].sort_values(ascending=False)[1:]
  print("correlation")
  print(corr)
  abs_corr=abs(corr)
  print(abs_corr)
  print("relevant features by corr: ")
  relevant=abs_corr[abs_corr>0.4]
  print(relevant)
  plt.figure(figsize=(20,10))
  sns.heatmap(df.corr().abs(),annot=True)

def corr_pearson(df, target):
  print("Coeficientes de correlacion de Pearson con", target, ":")
  data = df.drop(columns=[target], axis=0)
  for feature in data.columns:
    print(feature, ": ", stats.pearsonr(df[feature], df[target]).statistic)

def forward_selection(data, target, significance_level=0.05):
  initial_features = data.columns.tolist()
  best_features = []
  while (len(initial_features)>0):
      remaining_features = list(set(initial_features)-set(best_features))
      new_pval = pd.Series(index=remaining_features)
      for new_column in remaining_features:
          model = sm.OLS(target, sm.add_constant(data[best_features+[new_column]])).fit()
          new_pval[new_column] = model.pvalues[new_column]
      min_p_value = new_pval.min()
      if(min_p_value<significance_level):
          best_features.append(new_pval.idxmin())
      else:
          break
  return best_features

def selectFeatures(X,y, n_features):
  # Recursive Forward Elimination algorithm
  model=LinearRegression()
  rfe=RFE(model,n_features_to_select=n_features)
  fit=rfe.fit(X, y)
  print("selected features ",X.columns[fit.support_])

def main():

  df = load()

  # Feature engineering aplicado
  df = df[['Volume','High', 'Low', 'Date']]

  '''
  # Analisis exploratorio
  df.info()
  plotVariables(df)
  analisisNumericas(df)
  '''

  '''
  # Nulos
  nullAnalysis(df)
  '''vscode-terminal:/c8eaad140977ac4f9f74fa2c2734ba54/3

  # Outliers
  df = removeOutliers(df, 'Volume')

  # Escalamiento
  varNumericas = df.drop(['Volume'], axis=1)
  varNumericas = varNumericas.select_dtypes(include=np.number).columns
  for variable in varNumericas:
    df = scaleMinMax(df, variable)

  '''
  # Normalizacion
  for variable in varNumericas:
    (data_normalized, lambda_value) = normalizarPowerTransformer(df, variable)
    df[variable] = data_normalized
    #plotNormalizacion(df, variable, data_normalized, lambda_value)
  '''

  '''
  # Regresion simple
  normalEquation(df, 'Date', 'Volume')
  linearR(df, 'Date', 'Volume')
  polinomial(df, 'Open', 'Volume')
  '''


  # Regresion multiple
  ols(df, 'Volume')
  linearRegression('linear', df, 'Volume') # El mejor de las regresiones lineales
  linearRegression('ridge', df, 'Volume')
  linearRegression('lasso', df, 'Volume')
  linearRegression('elasticnet', df, 'Volume')
  polinomialRegression(df, 'Volume', 2)
  polinomialRegression(df, 'Volume', 3)
  polinomialRegression(df, 'Volume', 4) # El mejor de todos

  '''
  # Feature Engineering
  correlation(df)
  corr_pearson(df, 'Volume')
  X=df.drop('Volume',axis=1)
  y=df['Volume']
  print(forward_selection(X, y))
  selectFeatures(X, y, 3)
  '''

if __name__ == "__main__":
  main()