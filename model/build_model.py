#!/usr/bin/env python
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_curve, roc_auc_score
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

# These are the features and subsample files to use
features_file = 'testtrain_features.csv'
labels_file = 'testtrain_labels.csv'

# Read in pandas data frames for the features and events.
df_features = pd.read_csv(features_file)
df_labels = pd.read_csv(labels_file)

# Combine the features and subsample data.
df=pd.merge(df_features,df_labels,how='inner',left_on='id', right_on='Unnamed: 0')

# Generate the features vector
num_features = df_features.shape[1]
features = df.columns[1:num_features]

# Split the data into training and test sets
df['is_train'] = np.random.uniform(0, 1, len(df)) <= .5 
train, test = df[df['is_train']==True], df[df['is_train']==False]

# Set up the Random Forest classifier
clf = RandomForestClassifier(n_jobs=2, n_estimators = 1000)
# Turn the lossimpacting column into a factor (categorical variable)
y, _ = pd.factorize(train['lossimpacting'])
# Train the model
clf.fit(train[features], y)

# Check the accuracy using the test data
preds = clf.predict(test[features])
y_tst = test['lossimpacting']
print pd.crosstab(y_tst, preds, rownames=['actual'], colnames=['preds'])

# Construct the ROC curve to check model performance
scores = clf.predict_proba(test[features])[:,1]
fpr, tpr, thresholds = roc_curve(y_tst, scores)
plt.plot(fpr, tpr)
plt.savefig('roc.png')
# Print out the accuracy score from the ROC curve
print roc_auc_score(y_tst, scores)

# Figure out which features were the most important
importances = clf.feature_importances_
indices = np.argsort(importances)[::-1]
print("Feature ranking:")
for f in range(10):
    print("%d. feature %s (%f)" % (f + 1, \
      df_features.columns[1+indices[f]], importances[indices[f]]))

# Save the model to make predictions
from sklearn.externals import joblib
clf.fit(df[features], df['lossimpacting'])
try:
  os.mkdir('model')
except:
  pass
os.chdir('model')
joblib.dump(clf, 'model.pkl')
os.chdir('..')
