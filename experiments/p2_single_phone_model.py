import os
import argparse
import utils as utils
import pandas as pd
import random
import numpy as np

from sklearn import svm
from sklearn.preprocessing import StandardScaler
from sklearn.utils import shuffle
from joblib import Parallel, delayed

parser = argparse.ArgumentParser()
parser.add_argument("-dataset", default="../data/features.csv")
parser.add_argument(
    "-phone", default="iPhone XS Max"
)  # "iPhone 6s Plus", "iPhone 7 Plus", "iPhone 8 Plus","iPhone 6s", "iPhone 7", "iPhone 8","iPhone X", "iPhone XS", "iPhone XS Max"
parser.add_argument(
    "-random_state", default=42, type=int
)  # random state for reproducability
parser.add_argument("-jobs", default=6, type=int)  # parallelization parameter
parser.add_argument(
    "-classifier", default="svm"
)  # classifier svm, random_forest, neural_network, knn
args = parser.parse_args()

users, user_touches, user_touches_shuffled, session_user_touches = utils.preprocessing(
    dataset_path=args.dataset,
    game="swipe",
    direction="left",
    random_state=args.random_state,
    phone=args.phone,
)


export = {"eer": [], "fpr": [], "tpr": [], "authorized": [], "unauthorized": []}


def user_eer(user):
    if len(user_touches[user]) < 10:
        return

    # Split into 2 equal user groups
    users_copy = list(user_touches)
    users_copy.remove(user)
    user_groups = utils.partition_list(users_copy)

    X_train, y_train, X_test, y_test = utils.combined_sessions(
        user_touches,
        user_touches_shuffled,
        user,
        train_users=user_groups[0],
        test_users=user_groups[1],
    )

    X_train, y_train = shuffle(X_train, y_train, random_state=args.random_state)
    X_test, y_test = shuffle(X_test, y_test, random_state=args.random_state)

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    y_pred = utils.classify(X_train, y_train, X_test, classifier=args.classifier)

    fpr, tpr, eer = utils.calculate_roc(y_test, y_pred)

    authorized = []
    unauthorized = []
    for i in range(len(y_test)):
        if y_test[i] == 0:
            unauthorized.append(y_pred[i])
        else:
            authorized.append(y_pred[i])

    fpr = list(np.around(fpr, 3))
    tpr = list(np.around(tpr, 3))
    authorized = list(np.around(authorized, 3))
    unauthorized = list(np.around(random.sample(unauthorized, len(authorized)), 3))

    return (eer, fpr, tpr, authorized, unauthorized)


results = Parallel(n_jobs=args.jobs)([delayed(user_eer)(user) for user in users])

for result in results:
    if result != None:
        export["eer"].append(result[0])
        export["fpr"].append(result[1])
        export["tpr"].append(result[2])
        export["authorized"].append(result[3])
        export["unauthorized"].append(result[4])


storage_path = (
    "../results/" + args.classifier + "/p2_phone_models/phone_" + args.phone + ".csv"
)
directory = "/".join(storage_path.split("/")[:-1])
if not os.path.exists(directory):
    os.makedirs(directory)

df = pd.DataFrame(export)
df.to_csv(storage_path, index=False)
