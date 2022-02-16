import os
import argparse
import utils as utils
import pandas as pd
import random
import numpy as np

from sklearn import svm
from sklearn.preprocessing import StandardScaler

parser = argparse.ArgumentParser()
parser.add_argument("-dataset", default="../data/features.csv")
parser.add_argument(
    "-randomized", default=False, type=bool
)  # shuffle user swipes or keep in order
parser.add_argument(
    "-random_state", default=42, type=int
)  # random state for reproducability
parser.add_argument(
    "-classifier", default="svm"
)  # classifier svm, random_forest, neural_network, knn
args = parser.parse_args()

users, user_touches, user_touches_shuffled, session_user_touches = utils.preprocessing(
    dataset_path=args.dataset,
    game="swipe",
    direction="left",
    random_state=args.random_state,
)

results = {"eer": [], "fpr": [], "tpr": [], "authorized": [], "unauthorized": []}

for user in users:
    # At least 2 measurments are needed
    if len(session_user_touches[user]) < 2:
        continue

    # Split into 2 equal user groups
    users_copy = list(users.copy())
    users_copy.remove(user)
    user_groups = utils.partition_list(users_copy)

    X_train, X_test, y_train, y_test = utils.dedicated_sessions(
        session_user_touches,
        user_touches_shuffled,
        user,
        train_users=user_groups[0],
        test_users=user_groups[1],
        randomized=args.randomized,
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


if args.randomized:
    storage_path = (
        "../results/"
        + args.classifier
        + "/p3_training_selection/dedicated_randomized_sessions.csv"
    )
else:
    storage_path = (
        "../results/"
        + args.classifier
        + "/p3_training_selection/dedicated_sessions.csv"
    )

directory = "/".join(storage_path.split("/")[:-1])
if not os.path.exists(directory):
    os.makedirs(directory)

df = pd.DataFrame(results)
df.to_csv(storage_path, index=False)
