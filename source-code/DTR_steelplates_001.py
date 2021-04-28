#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
from sklearn.model_selection import cross_val_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import precision_recall_fscore_support, accuracy_score, confusion_matrix
from sklearn.utils import resample

missing_values = ["n/a", "na", "--", "NA", "?", "", " ", -1, "NAN", "NaN"]
df = pd.read_csv('/home/mohammoa/HiWi/asm-2/1_data/steelplates.csv', na_values=missing_values)
df2 = pd.read_csv('/home/mohammoa/HiWi/asm-2/1_data/steelplates_train_75.csv', na_values=missing_values)
df3 = pd.read_csv('/home/mohammoa/HiWi/asm-2/1_data/steelplates_test_25.csv', na_values=missing_values)

seed = 25

df_majority = df[df['target']!='Other_Faults']
df_minority = df[df['target']=='Other_Faults']
df_minority_upsampled = resample(df_minority, replace=True,n_samples=len(df_majority),random_state=seed)     # sample with replacement
df=pd.concat([df_majority, df_minority_upsampled])


print(df.shape)
y = df.pop('target')
X = df
categorical_columns = df.select_dtypes(exclude=['int', 'float']).columns
numerical_columns = df.select_dtypes(include=['int', 'float']).columns

numerical_pipe = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),
])

preprocessing = ColumnTransformer([('num', numerical_pipe, numerical_columns)])

lr = Pipeline([
    ('preprocess', preprocessing),
    ('classifier', DecisionTreeClassifier(min_impurity_decrease=0.00001))])



X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=0.25, random_state=seed)
y_train = df2.pop('target')
X_train = df2
y_test = df3.pop('target')
X_test = df3
start = time.time()
lr.fit(X_train, y_train)
stop = time.time()
start1 = time.time()
score = cross_val_score(lr, X_test, y_test, cv=5, scoring='accuracy')
stop1 = time.time()
start3 = time.time()
y_pred = lr.predict(X_test)
stop3 = time.time()
accuracy = lr.score(X_test, y_test)

print(f"Training_Time_in_s_before_cv: {stop - start}s")
print(f"Training_Time_in_s_for_cv: {stop1 - start1}s")

import joblib

filename = '/home/mohammoa/HiWi/asm-2/3_pickle/DTR_steelplates_001.pkl'
with open(filename, 'wb') as file:
    joblib.dump(lr, file)
with open(filename, 'rb') as file:
    dt_pkl = joblib.load(file)

y_pred = dt_pkl.predict(X_test)
accuracy = dt_pkl.score(X_test, y_test)
print("Accuracy:",accuracy)
print("Error:",1 - accuracy)
metrics = {}
prec_recall = precision_recall_fscore_support(y_test, y_pred, average=None)
p, r, f, sp = prec_recall
t = (stop - start)
t1 = (stop1 - start1)
t2 = (stop3 - start3)
s = accuracy_score(y_test, y_pred)
c = confusion_matrix(y_test, y_pred)
d = c.tolist()
metrics['accuracy'] = s
metrics['error'] = 1 - s
metrics['precision'] = p[1]
metrics['recall'] = r[1]
metrics['fscore'] = f[1]
metrics["single_training_time"] = t
metrics["cross_validated_training_time"] = t1
metrics["test_time_per_unit"] = t2 / 11303
metrics["confusion_matrix_rowstrue_colspred"] = d
metrics["test_file"] = "steelplates_test_25.csv"
print("Score= {}".format(s))
print("Error= {}".format(1 - s))
print("Precision,Recall,F_beta,Support {}".format(prec_recall))
print(confusion_matrix(y_test, y_pred))
print("test time per unit", (t2 / 11303))

import json
import os

if os.path.exists('/home/mohammoa/HiWi/asm-2/3_pickle/DTR_steelplates_001.json'):
    with open('/home/mohammoa/HiWi/asm-2/3_pickle/DTR_steelplates_001.json', 'r') as f:
        models = json.load(f)
    models["Model"]["Metrics"] = metrics
    with open('/home/mohammoa/HiWi/asm-2/3_pickle/DTR_steelplates_001.json', 'w') as f:
        json.dump(models, f, indent=2)





