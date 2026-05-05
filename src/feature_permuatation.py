import joblib
import pandas as pd
from sklearn.inspection import permutation_importance
from sklearn.model_selection import train_test_split

model = joblib.load("tuned_model.pkl")
#load data and split to test and training set
df = pd.read_csv("processed_dataa.csv")

model_features = [feature for feature in df.columns if feature!="label"]

X = df[model_features]
y = (df["label"] == "distracted").astype(int).values

X_train, X_test, y_train, y_test = train_test_split(X, y , test_size=0.2, random_state=42,
                                                    stratify=y)

permutation = permutation_importance(model,X_train, y_train,
                                     n_repeats=20, random_state=42, n_jobs=1)

importance = pd.DataFrame({
    "Feature" : model_features,
    "importance" : permutation.importances_mean
})

importance = importance.sort_values("importance",ascending=False)

print(importance)
