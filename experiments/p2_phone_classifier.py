import random
import statistics
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from pprint import pprint
from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, balanced_accuracy_score
from sklearn.metrics import plot_confusion_matrix

parser = argparse.ArgumentParser()
parser.add_argument("-dataset", default="../data/features.csv")
parser.add_argument(
    "-random_state", default=42, type=int
)  # random state for reproducability
parser.add_argument(
    "-classifier", default="svm"
)  # classifier svm, random_forest, neural_network, knn
args = parser.parse_args()

iphone_to_class = {
    "iPhone 6s": 0,
    "iPhone 7": 1,
    "iPhone 8": 2,
    "iPhone 6s Plus": 3,
    "iPhone 7 Plus": 4,
    "iPhone 8 Plus": 5,
    "iPhone X": 6,
    "iPhone XS": 7,
    "iPhone XS Max": 8,
}

features_model_train = {
    "iPhone 6s": [],
    "iPhone 7": [],
    "iPhone 8": [],
    "iPhone 6s Plus": [],
    "iPhone 7 Plus": [],
    "iPhone 8 Plus": [],
    "iPhone X": [],
    "iPhone XS": [],
    "iPhone XS Max": [],
}

features_model_test = {
    "iPhone 6s": [],
    "iPhone 7": [],
    "iPhone 8": [],
    "iPhone 6s Plus": [],
    "iPhone 7 Plus": [],
    "iPhone 8 Plus": [],
    "iPhone X": [],
    "iPhone XS": [],
    "iPhone XS Max": [],
}

features = pd.read_csv(args.dataset)

for fm in features_model_train:
    print(fm)
    model_users = features.loc[(features["phone_model"] == fm)]["uuid"].unique()
    random.Random(args.random_state).shuffle(model_users)

    features_model_train[fm] = features.loc[
        (features["uuid"].isin(model_users[: int(len(model_users) * 0.8)]))
        & (features["gametype"] == "swipe")
        & (features["direction"] == "left")
        & (features["phone_model"] == fm)
    ]
    features_model_test[fm] = features.loc[
        (features["uuid"].isin(model_users[int(len(model_users) * 0.8) :]))
        & (features["gametype"] == "swipe")
        & (features["direction"] == "left")
        & (features["phone_model"] == fm)
    ]

features_train = pd.concat(
    [
        features_model_train["iPhone 6s"],
        features_model_train["iPhone 6s Plus"],
        features_model_train["iPhone 7"],
        features_model_train["iPhone 7 Plus"],
        features_model_train["iPhone 8"],
        features_model_train["iPhone 8 Plus"],
        features_model_train["iPhone X"],
        features_model_train["iPhone XS"],
        features_model_train["iPhone XS Max"],
    ],
    ignore_index=True,
)


features_train = features_train.dropna()

minSizeTest = 10000000

for fm in features_model_test:
    if len(features_model_test[fm]) < minSizeTest:
        minSizeTest = len(features_model_test[fm])

for fm in features_model_test:
    features_model_test[fm] = features_model_test[fm].sample(
        n=minSizeTest, random_state=args.random_state
    )

features_test = pd.concat(
    [
        features_model_test["iPhone 6s"],
        features_model_test["iPhone 6s Plus"],
        features_model_test["iPhone 7"],
        features_model_test["iPhone 7 Plus"],
        features_model_test["iPhone 8"],
        features_model_test["iPhone 8 Plus"],
        features_model_test["iPhone X"],
        features_model_test["iPhone XS"],
        features_model_test["iPhone XS Max"],
    ],
    ignore_index=True,
)

features_test = features_test.dropna()


X_train = []
y_train = []
X_test = []
y_test = []

X_train = features_train.loc[:, "duration":"midCover"].values.tolist()

for target in features_train.loc[:, "phone_model"].values.tolist():
    y_train.append(iphone_to_class[target])

X_test = features_test.loc[:, "duration":"midCover"].values.tolist()

for target in features_test.loc[:, "phone_model"].values.tolist():
    y_test.append(iphone_to_class[target])

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

clf = svm.SVC(gamma="scale", class_weight="balanced")
clf.fit(X_train, y_train)

np.set_printoptions(precision=2)

y_pred = clf.predict(X_test)

print(accuracy_score(y_test, y_pred))
print(balanced_accuracy_score(y_test, y_pred))

# Plot confusion matrix
titles_options = [
    ("Normalized confusion matrix", "true"),
    ("Confusion matrix, without normalization", None),
]
for title, normalize in titles_options:
    disp = plot_confusion_matrix(
        clf,
        X_test,
        y_test,
        display_labels=[*iphone_to_class],
        cmap=plt.cm.Blues,
        normalize=normalize,
    )
    disp.ax_.set_title(title)

    pprint(title)
    pprint(np.array(disp.confusion_matrix))
