import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
import xgboost as xgb
from xgboost import XGBRegressor
from sklearn.metrics import r2_score
from sklearn.metrics import root_mean_squared_error
from sklearn.preprocessing import MinMaxScaler
import time
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import dask.dataframe as dd
#import pickle
from datetime import datetime

start=now =  datetime.now().strftime("%Y-%m-%d %H:%M:%S")

df0=dd.read_csv('./BIG DATA/df_0.csv')
df1=dd.read_csv('./BIG DATA/df_1.csv')
df2=dd.read_csv('./BIG DATA/df_2.csv')
df3=dd.read_csv('./BIG DATA/df_3.csv')
df_val=dd.read_csv('./BIG DATA/df_val.csv')
target0=dd.read_csv('./BIG DATA/target_0.csv')
target1=dd.read_csv('./BIG DATA/target_1.csv')
target2=dd.read_csv('./BIG DATA/target_2.csv')
target3=dd.read_csv('./BIG DATA/target_3.csv')
target_val=dd.read_csv('./BIG DATA/target_val.csv')

print("Data load")

def prepareDF(df):
    df=df.drop([ '6', '12', '13', '14', '24', '28'],axis=1)
    df=df.astype('int32')
    return df

def prepareTarget(df):
    df=df.drop([ '1'],axis=1)
    df=df.astype('int32')
    return df

result_df=prepareDF(df0).compute().to_csv('data_X.csv')
result_df_val=prepareDF(df_val).compute().to_csv('data_X_val.csv')
target=prepareTarget(target0).compute().to_csv('data_Y.csv')
target_valll=prepareTarget(target_val).compute().to_csv('data_Y_val.csv')

result_df=None
result_df_val=None
target=None
target_valll=None

def pipeline(directory):
    df=pd.read_csv(directory+'data_X.csv', nrows=100_000)
    target=pd.read_csv(directory+'data_Y.csv', nrows=100_000)

    df_val=pd.read_csv(directory+'data_X_val.csv', nrows=10_000)
    target_val=pd.read_csv(directory+'data_Y_val.csv', nrows=10_000)

    X_train, X_test, y_train, y_test = train_test_split(df , target, test_size=0.2, random_state=69)
    
    xgbr=xgb.XGBRegressor(eval_metric='rmsle',random_state = 69)
    xgbr.fit(X_train, y_train)

    return xgbr, {'R2':r2_score(xgbr.predict(df_val),target_val),'RMSE':root_mean_squared_error(xgbr.predict(df_val),target_val)}

model,data=pipeline('./')

file = open('model.pkl', 'wb')
#pickle.dump(model, file)
#model.save_model("model_reserve.pkl")

with open ('metrics.txt', 'w') as f:
    f.write(start)
    f.write(data)
    f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))