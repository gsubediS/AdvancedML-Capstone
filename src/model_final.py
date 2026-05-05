import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, cross_val_score, StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay, roc_auc_score


#load data and split to test and training set
df = pd.read_csv("processed_dataa.csv")

model_features = [feature for feature in df.columns if feature!="label"]

X = df[model_features]
y = (df["label"] == "distracted").astype(int).values

X_train, X_test, y_train, y_test = train_test_split(X, y , test_size=0.2, random_state=42,
                                                    stratify=y)
cv  = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)

#Hyperparam search - Grid Search
grid_params = {"clf__n_estimators": [100, 200, 300],
               "clf__max_depth" : [4,6,8,3],"clf__min_samples_leaf" : [3,5,7]}
grid_pipeline = Pipeline([("clf", RandomForestClassifier(class_weight="balanced", random_state=42))])
grid_search = GridSearchCV(grid_pipeline,param_grid=grid_params, cv=cv,
                           scoring="roc_auc",n_jobs=1,verbose=0)
grid_search.fit(X_train, y_train)
print()
print("Optimal Parameters: " ,grid_search.best_params_)
print()
tuned_model = grid_search.best_estimator_
tuned_model.fit(X_train, y_train)

#Evaluation on test set
y_pred = tuned_model.predict(X_test)
y_prob = tuned_model.predict_proba(X_test)[:,1]

#display results
print()
print(classification_report(y_test, y_pred))
print("ROC AUC: ",roc_auc_score(y_test, y_prob))
tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
print("False Positive (FP) ratio : ", fp/(tn+fp))
print("False Negative (FPN ratio : ", fn/(tn+fn))

#display confusion matrix
cm = confusion_matrix(y_test, y_pred)
ConfusionMatrixDisplay(cm,display_labels=["focused","distracted"]).plot(cmap="Blues")
plt.show()

#save model
joblib.dump(tuned_model, "tuned_model.pkl")
print("Model saved!")

