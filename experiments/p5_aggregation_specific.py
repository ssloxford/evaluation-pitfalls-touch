import statistics
import argparse
import utils as utils
import numpy as np
import pandas as pd
import random

from sklearn import svm
from sklearn.preprocessing import StandardScaler
from sklearn.utils import shuffle
from joblib import Parallel, delayed

parser = argparse.ArgumentParser()
parser.add_argument("-dataset", default="../data/features.csv")
parser.add_argument("-aggregation_length", default=5, type=int)
parser.add_argument(
    "-random_state", default=42, type=int
)  # random state for reproducability
parser.add_argument("-jobs", default=6, type=int)  # parallelization parameter
args = parser.parse_args()

users, user_touches, user_touches_shuffled, session_user_touches = utils.preprocessing(
    dataset_path=args.dataset,
    game="swipe", 
    direction="left", 
    random_state=args.random_state,
)

results = {
    "eer": [],
    "fpr": [],
    "tpr": [],
    "authorized": [],
    "unauthorized": []
}

def user_eer(user, aggregation_length_user):

    if len(user_touches[user]) < aggregation_length_user * 5:
        return

    # Split into 2 equal user groups
    users_copy = list(users.copy())
    users_copy.remove(user)
    user_groups = utils.partition_list(users_copy)

    X_train, y_train, X_test, y_test = utils.combined_sessions_aggregation(
        user_touches,
        user_touches_shuffled,
        user,
        train_users=user_groups[0],
        test_users=user_groups[1],
        aggregation_length=args.aggregation_length,
    )

    X_train, y_train = shuffle(X_train, y_train, random_state=args.random_state)
    X_test, y_test = shuffle(X_test, y_test, random_state=args.random_state)

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)

    clf = svm.SVC(gamma="scale")
    clf.fit(X_train, y_train)

    y_pred = []

    for i in range(len(X_test)):
        y_pred_aggregation = clf.decision_function(scaler.transform(X_test[i]))

        y_pred.append(statistics.mean(y_pred_aggregation))

    fpr,tpr,eer = utils.calculate_roc(y_test, y_pred)
    results['eer'].append(eer)
    results['fpr'].append(list(np.around(fpr, 3)))
    results['tpr'].append(list(np.around(tpr, 3)))

    authorized = []
    unauthorized = []
    for i in range(len(y_test)):
        if y_test[i] == 0:
            unauthorized.append(y_pred[i])
        else:
            authorized.append(y_pred[i])

    results['authorized'].append(list(np.around(authorized, 3)))
    results['unauthorized'].append(list(np.around(random.sample(unauthorized,len(authorized)), 3)))

for user in users:
    user_eer(user, args.aggregation_length)


df = pd.DataFrame(results)
df.to_csv("../results/p5_aggregations/aggregation_" + str(args.aggregation_length) + ".csv", index=False)