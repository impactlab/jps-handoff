#!/usr/bin/env python
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_curve, roc_auc_score
from sklearn.externals import joblib
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os, csv

features_file = 'features.csv'

df_features = pd.read_csv(features_file)
num_features = df_features.shape[1]
features = df_features.columns[1:num_features]

clf = joblib.load('model/model.pkl')

scores = clf.predict_proba(df_features[features])[:,1]

with open('predictions.csv', 'w') as f:
  fcsv = csv.writer(f)
  for meter, score in zip(df_features.id, scores):
    fcsv.writerow([str(meter) , score*100])
