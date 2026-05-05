import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, cross_val_score, StratifiedKFold, train_test_split, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay, roc_auc_score
from sklearn.preprocessing import StandardScaler

#load data and split to test and training set
df = pd.read_csv("processed_dataa.csv")

model_features = [feature for feature in df.columns if feature!="label"]

X = df[model_features]
X.replace([np.inf, -np.inf],np.nan)
X = X.fillna(0)


y = (df["label"] == "distracted").astype(int).values

X_train, X_test, y_train, y_test = train_test_split(X, y , test_size=0.2, random_state=42,
                                                    stratify=y)
cv  = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)


models = {
    "Baseline Random Forest" : Pipeline([("clf",RandomForestClassifier(n_estimators=100, random_state=42))
              ]),
    "Tuned Random Forest" : Pipeline([("clf", RandomForestClassifier(
                      n_estimators=200,
                      max_depth=6,
                      min_samples_leaf=5,
                      random_state=42,
                      max_features="sqrt",
                      class_weight="balanced",
    ))]),
    "Gradient Boosting" : Pipeline([("clf", GradientBoostingClassifier(
                        n_estimators=100,
                        max_depth=3,
                        learning_rate=0.05,
                        subsample=0.8,
                        random_state=42
    ))]),
    # "Logistic Regression": Pipeline([
    #           ("scaler", StandardScaler()),
    #           ("clf", LogisticRegression(max_iter=1000,class_weight="balanced", solver="liblinear"))
    #         ]),

}

for name,model in models.items():
    scores = cross_validate(model, X_train, y_train, cv=cv, scoring=["accuracy","roc_auc","f1"], return_train_score = True)
    acc = scores["test_accuracy"].mean()
    auc = scores["test_roc_auc"].mean()
    f1 = scores["test_f1"].mean()
    train_acc = scores["train_accuracy"].mean()
    gap = train_acc - acc
    print()
    print(f'Model : {name} ')
    print(f' Accuracy : {acc}')
    print(f' AUC ROC : {auc}')
    print(f' F1 score : {f1}')
    print(f' Train Accuracy : {train_acc}')
    print(f' Gap : {gap}')
    print()
