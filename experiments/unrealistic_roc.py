import argparse
import os
import random

import numpy as np
import pandas as pd
import utils as utils
from joblib import Parallel, delayed
from sklearn import svm
from sklearn.preprocessing import StandardScaler
from sklearn.utils import shuffle

parser = argparse.ArgumentParser()
parser.add_argument("-dataset", default="../data/features.csv")
parser.add_argument("-sample_size", default=40, type=int)
parser.add_argument(
    "-random_state", default=42, type=int
)  # random state for reproducability
parser.add_argument("-jobs", default=6, type=int)  # parallelization parameter
parser.add_argument(
    "-classifier", default="svm"
)  # classifier svm, random_forest, neural_network, knn
args = parser.parse_args()

(
    users,
    user_touches,
    user_touches_shuffled,
    session_user_touches,
) = utils.preprocessing(
    dataset_path=args.dataset,
    game="swipe",
    direction="left",
    random_state=args.random_state,
)

results = {"eer": [], "fpr": [], "tpr": [], "authorized": [], "unauthorized": []}

random.Random(args.random_state).shuffle(users)
subsampled_users = users[: args.sample_size]

for user in subsampled_users:
    if len(user_touches[user]) < 10:
        continue

    # Split into 2 equal user groups
    users_copy = list(subsampled_users.copy())
    users_copy.remove(user)
    user_groups = utils.partition_list(users_copy)

    for user_group in user_groups:
        (
            X_train,
            y_train,
            X_test,
            y_test,
        ) = utils.combined_sessions_subsampled_include_attacker(
            user_touches,
            user_touches_shuffled,
            user,
            subsampled_users=user_group,
            randomized=True,
        )

        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)

        y_pred = utils.classify(X_train, y_train, X_test, classifier=args.classifier)

        fpr, tpr, eer = utils.calculate_roc(y_test, y_pred)
        results["eer"].append(eer)
        results["fpr"].append(list(np.around(fpr, 3)))
        results["tpr"].append(list(np.around(tpr, 3)))

        authorized = []
        unauthorized = []
        for i in range(len(y_test)):
            if y_test[i] == 0:
                unauthorized.append(y_pred[i])
            else:
                authorized.append(y_pred[i])

        results["authorized"].append(list(np.around(authorized, 3)))
        results["unauthorized"].append(
            list(np.around(random.sample(unauthorized, len(authorized)), 3))
        )

storage_path = "../results/" + args.classifier + "/general/unrealistic_roc.csv"
directory = "/".join(storage_path.split("/")[:-1])
if not os.path.exists(directory):
    os.makedirs(directory)

df = pd.DataFrame(results)
df.to_csv(storage_path, index=False)
